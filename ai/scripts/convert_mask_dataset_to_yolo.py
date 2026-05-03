"""
Convert paired image/mask segmentation datasets into YOLO detection labels by
extracting connected-component bounding boxes.

Supports:
- exact RGB target color matching
- grayscale threshold masks
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import cv2
import numpy as np


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert paired image/mask segmentation data to YOLO detection labels."
    )
    parser.add_argument("--images-root", required=True)
    parser.add_argument("--masks-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--class-id", type=int, required=True)
    parser.add_argument(
        "--mask-mode",
        choices=["rgb", "grayscale"],
        default="rgb",
        help="How the positive spill region is encoded in masks.",
    )
    parser.add_argument(
        "--target-rgb",
        default="255,0,124",
        help="Target positive class RGB value for rgb mode.",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=240,
        help="Positive threshold for grayscale mode.",
    )
    parser.add_argument("--min-area", type=int, default=32)
    parser.add_argument(
        "--resize-mask-to-image",
        action="store_true",
        help="Resize mask to the corresponding image size before extracting connected components.",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def prepare_output(output_root: Path, overwrite: bool) -> None:
    if overwrite and output_root.exists():
        shutil.rmtree(output_root)
    for split in ("train", "val", "test"):
        (output_root / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_root / "labels" / split).mkdir(parents=True, exist_ok=True)


def image_list(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)


def find_matching_mask(image_path: Path, masks_root: Path) -> Path | None:
    stem_digits = "".join(ch for ch in image_path.stem if ch.isdigit())
    candidates = list(masks_root.rglob(f"*{stem_digits}*"))
    for candidate in candidates:
        if candidate.is_file() and candidate.suffix.lower() in IMAGE_EXTENSIONS:
            return candidate
    return None


def binary_mask(
    mask_path: Path,
    mask_mode: str,
    target_rgb: tuple[int, int, int],
    threshold: int,
) -> np.ndarray:
    if mask_mode == "rgb":
        mask = cv2.imread(str(mask_path), cv2.IMREAD_COLOR)
        if mask is None:
            raise ValueError(f"Unable to read mask: {mask_path}")
        # cv2 uses BGR
        target_bgr = np.array([target_rgb[2], target_rgb[1], target_rgb[0]], dtype=np.uint8)
        diff = np.abs(mask.astype(np.int16) - target_bgr.astype(np.int16))
        return (diff.max(axis=2) <= 8).astype(np.uint8) * 255

    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise ValueError(f"Unable to read mask: {mask_path}")
    return (mask >= threshold).astype(np.uint8) * 255


def connected_boxes(binary: np.ndarray, min_area: int) -> list[tuple[int, int, int, int]]:
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    boxes: list[tuple[int, int, int, int]] = []
    for label_id in range(1, num_labels):
        x, y, w, h, area = stats[label_id]
        if area < min_area or w <= 1 or h <= 1:
            continue
        boxes.append((x, y, w, h))
    return boxes


def yolo_line(x: int, y: int, w: int, h: int, img_w: int, img_h: int, class_id: int) -> str:
    x_center = (x + w / 2) / img_w
    y_center = (y + h / 2) / img_h
    return f"{class_id} {x_center:.6f} {y_center:.6f} {w / img_w:.6f} {h / img_h:.6f}"


def main() -> None:
    args = parse_args()
    images_root = Path(args.images_root).resolve()
    masks_root = Path(args.masks_root).resolve()
    output_root = Path(args.output_root).resolve()
    target_rgb = tuple(int(part.strip()) for part in args.target_rgb.split(","))
    prepare_output(output_root, overwrite=args.overwrite)

    for split in ("train", "val", "test"):
        split_images_root = images_root / split
        split_masks_root = masks_root / split
        split_images = image_list(split_images_root)
        processed = 0
        for image_path in split_images:
            mask_path = find_matching_mask(image_path, split_masks_root)
            if mask_path is None:
                continue

            image = cv2.imread(str(image_path))
            if image is None:
                continue

            binary = binary_mask(mask_path, args.mask_mode, target_rgb, args.threshold)
            if args.resize_mask_to_image:
                img_h, img_w = image.shape[:2]
                binary = cv2.resize(binary, (img_w, img_h), interpolation=cv2.INTER_NEAREST)
            boxes = connected_boxes(binary, args.min_area)
            if not boxes:
                continue

            img_h, img_w = image.shape[:2]
            dst_image = output_root / "images" / split / image_path.name
            dst_label = output_root / "labels" / split / f"{image_path.stem}.txt"
            shutil.copy2(image_path, dst_image)
            lines = [yolo_line(x, y, w, h, img_w, img_h, args.class_id) for x, y, w, h in boxes]
            dst_label.write_text("\n".join(lines) + "\n", encoding="utf-8")
            processed += 1

            if processed % 250 == 0:
                print(f"[{split}] converted {processed}")

        print(f"[{split}] total converted: {processed}")


if __name__ == "__main__":
    main()
