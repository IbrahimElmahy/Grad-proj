"""
Convert the FOD-A Pascal VOC dataset into a YOLO dataset compatible with fod_data.yaml.

Current strategy:
1. Read FOD-A VOC XML annotations.
2. Map every FOD object category to class 0 -> Debris.
3. Build train/val/test folders in YOLO format.
4. Optionally cap each split size for faster local experiments.

Example:
    .venv311_cuda\\Scripts\\python.exe ai\\scripts\\prepare_foda_yolo.py ^
        --source-voc ai\\datasets\\FODPascalVOCFormat-V2.1\\FODPascalVOCFormat-V.2.1\\VOC2007 ^
        --output-root ai\\datasets\\fod_runway ^
        --train-count 1000 ^
        --val-count 200 ^
        --test-count 200 ^
        --overwrite
"""

from __future__ import annotations

import argparse
import random
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert FOD-A Pascal VOC annotations into YOLO format."
    )
    parser.add_argument("--source-voc", required=True, help="Path to VOC2007 root.")
    parser.add_argument("--output-root", required=True, help="Output YOLO dataset root.")
    parser.add_argument(
        "--trainval-file",
        help="Optional custom trainval.txt path. Defaults to VOC ImageSets/Main/trainval.txt.",
    )
    parser.add_argument(
        "--test-file",
        help="Optional custom test.txt path. Defaults to VOC ImageSets/Main/test.txt.",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.10,
        help="Fraction of trainval images to move into validation.",
    )
    parser.add_argument(
        "--train-count",
        type=int,
        help="Optional max number of training images after split.",
    )
    parser.add_argument(
        "--val-count",
        type=int,
        help="Optional max number of validation images after split.",
    )
    parser.add_argument(
        "--test-count",
        type=int,
        help="Optional max number of test images.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--overwrite", action="store_true", help="Delete output root first.")
    return parser.parse_args()


def load_ids(txt_path: Path) -> list[str]:
    with txt_path.open("r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def sample_ids(ids: list[str], count: int | None, rng: random.Random) -> list[str]:
    if count is None or count >= len(ids):
        return list(ids)
    return rng.sample(ids, count)


def convert_bbox(size: tuple[int, int], box: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    width, height = size
    xmin, ymin, xmax, ymax = box

    x_center = ((xmin + xmax) / 2.0) / width
    y_center = ((ymin + ymax) / 2.0) / height
    box_width = (xmax - xmin) / width
    box_height = (ymax - ymin) / height

    return x_center, y_center, box_width, box_height


def parse_xml(xml_path: Path) -> tuple[tuple[int, int], list[tuple[float, float, float, float]]]:
    root = ET.parse(xml_path).getroot()

    size_node = root.find("size")
    width = int(float(size_node.findtext("width", "0")))
    height = int(float(size_node.findtext("height", "0")))

    boxes: list[tuple[float, float, float, float]] = []
    for obj in root.findall("object"):
        bndbox = obj.find("bndbox")
        if bndbox is None:
            continue

        xmin = float(bndbox.findtext("xmin", "0"))
        ymin = float(bndbox.findtext("ymin", "0"))
        xmax = float(bndbox.findtext("xmax", "0"))
        ymax = float(bndbox.findtext("ymax", "0"))

        if xmax <= xmin or ymax <= ymin:
            continue

        boxes.append((xmin, ymin, xmax, ymax))

    return (width, height), boxes


def write_yolo_label(label_path: Path, size: tuple[int, int], boxes: list[tuple[float, float, float, float]]) -> None:
    label_path.parent.mkdir(parents=True, exist_ok=True)
    with label_path.open("w", encoding="utf-8") as handle:
        for box in boxes:
            x_center, y_center, box_width, box_height = convert_bbox(size, box)
            handle.write(f"0 {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}\n")


def copy_split(
    ids: list[str],
    split: str,
    voc_root: Path,
    output_root: Path,
) -> int:
    image_dir = voc_root / "JPEGImages"
    ann_dir = voc_root / "Annotations"
    out_img_dir = output_root / "images" / split
    out_lbl_dir = output_root / "labels" / split

    out_img_dir.mkdir(parents=True, exist_ok=True)
    out_lbl_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for image_id in ids:
        src_image = image_dir / f"{image_id}.jpg"
        src_xml = ann_dir / f"{image_id}.xml"
        if not src_image.exists() or not src_xml.exists():
            continue

        size, boxes = parse_xml(src_xml)
        if not boxes:
            continue

        shutil.copy2(src_image, out_img_dir / src_image.name)
        write_yolo_label(out_lbl_dir / f"{image_id}.txt", size, boxes)
        copied += 1

    return copied


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    voc_root = Path(args.source_voc).resolve()
    output_root = Path(args.output_root).resolve()

    if args.overwrite and output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True, exist_ok=True)

    trainval_file = Path(args.trainval_file).resolve() if args.trainval_file else voc_root / "ImageSets" / "Main" / "trainval.txt"
    test_file = Path(args.test_file).resolve() if args.test_file else voc_root / "ImageSets" / "Main" / "test.txt"

    trainval_ids = load_ids(trainval_file)
    test_ids = load_ids(test_file)
    rng.shuffle(trainval_ids)

    val_size = max(1, int(len(trainval_ids) * args.val_ratio))
    val_ids = trainval_ids[:val_size]
    train_ids = trainval_ids[val_size:]

    train_ids = sample_ids(train_ids, args.train_count, rng)
    val_ids = sample_ids(val_ids, args.val_count, rng)
    test_ids = sample_ids(test_ids, args.test_count, rng)

    train_copied = copy_split(train_ids, "train", voc_root, output_root)
    val_copied = copy_split(val_ids, "val", voc_root, output_root)
    test_copied = copy_split(test_ids, "test", voc_root, output_root)

    print(f"Prepared YOLO dataset at: {output_root}")
    print(f"train images: {train_copied}")
    print(f"val images:   {val_copied}")
    print(f"test images:  {test_copied}")
    print("Label mapping: all FOD-A object categories -> class 0 (Debris)")


if __name__ == "__main__":
    main()
