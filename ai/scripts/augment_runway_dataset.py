"""
Augment a YOLO-format runway hazard dataset with harsh runway conditions.

The script:
1. Copies the original dataset to a new output directory.
2. Applies augmentations only to the training split by default.
3. Preserves YOLO labels while simulating:
   - low light / night vision,
   - rain / fog,
   - motion blur,
   - sensor noise.

Example:
    python ai/scripts/augment_runway_dataset.py ^
        --dataset-root ai/datasets/fod_runway ^
        --output-root ai/datasets/fod_runway_aug ^
        --copies-per-image 3 ^
        --data-yaml ai/configs/fod_data.yaml
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Augment a YOLO runway dataset with harsh-condition transforms."
    )
    parser.add_argument(
        "--dataset-root",
        required=True,
        help="Root dataset directory containing images/ and labels/ folders.",
    )
    parser.add_argument(
        "--output-root",
        required=True,
        help="Where the copied + augmented dataset should be written.",
    )
    parser.add_argument(
        "--copies-per-image",
        type=int,
        default=3,
        help="Number of augmented copies to generate for every training image.",
    )
    parser.add_argument(
        "--augment-split",
        default="train",
        help="Dataset split to augment. Usually train.",
    )
    parser.add_argument(
        "--min-visibility",
        type=float,
        default=0.3,
        help="Minimum bbox visibility retained after augmentation.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete the output dataset first if it already exists.",
    )
    parser.add_argument(
        "--data-yaml",
        help="Optional input data.yaml to clone with an updated output path.",
    )
    return parser.parse_args()


def prepare_output_root(output_root: Path, overwrite: bool) -> Path:
    if overwrite and output_root.exists():
        shutil.rmtree(output_root)

    output_root.mkdir(parents=True, exist_ok=True)
    return output_root


def list_images(images_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in images_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def read_yolo_labels(label_path: Path) -> tuple[list[list[float]], list[int]]:
    bboxes: list[list[float]] = []
    class_labels: list[int] = []

    if not label_path.exists():
        return bboxes, class_labels

    with label_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) != 5:
                continue

            class_id = int(float(parts[0]))
            bbox = [float(value) for value in parts[1:]]
            class_labels.append(class_id)
            bboxes.append(bbox)

    return bboxes, class_labels


def write_yolo_labels(label_path: Path, bboxes: list[list[float]], class_labels: list[int]) -> None:
    label_path.parent.mkdir(parents=True, exist_ok=True)
    with label_path.open("w", encoding="utf-8") as handle:
        for class_id, bbox in zip(class_labels, bboxes):
            x, y, w, h = bbox
            handle.write(f"{class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")


def night_vision_effect(image, **kwargs):
    import cv2
    import numpy as np

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    night = np.zeros_like(image)
    night[:, :, 1] = gray
    night[:, :, 0] = (gray * 0.10).astype(image.dtype)
    night[:, :, 2] = (gray * 0.10).astype(image.dtype)

    return cv2.GaussianBlur(night, (0, 0), sigmaX=1.4)


def build_augmentation_pipeline(min_visibility: float):
    import albumentations as A

    return A.Compose(
        [
            A.OneOf(
                [
                    A.Compose(
                        [
                            A.RandomBrightnessContrast(
                                brightness_limit=(-0.55, -0.20),
                                contrast_limit=(-0.15, 0.15),
                                p=1.0,
                            ),
                            A.RandomGamma(gamma_limit=(60, 90), p=1.0),
                        ]
                    ),
                    A.Lambda(image=night_vision_effect, p=1.0),
                ],
                p=0.85,
            ),
            A.OneOf(
                [
                    A.RandomRain(
                        slant_range=(-12, 12),
                        drop_length=18,
                        drop_width=1,
                        blur_value=5,
                        brightness_coefficient=0.85,
                        p=1.0,
                    ),
                    A.RandomFog(
                        fog_coef_range=(0.2, 0.45),
                        alpha_coef=0.10,
                        p=1.0,
                    ),
                ],
                p=0.70,
            ),
            A.OneOf(
                [
                    A.MotionBlur(blur_limit=(7, 15), p=1.0),
                    A.AdvancedBlur(blur_limit=(5, 9), noise_limit=(0.75, 1.25), p=1.0),
                ],
                p=0.60,
            ),
            A.OneOf(
                [
                    A.GaussNoise(std_range=(0.08, 0.20), mean_range=(0.0, 0.03), p=1.0),
                    A.ISONoise(color_shift=(0.02, 0.08), intensity=(0.15, 0.45), p=1.0),
                ],
                p=0.65,
            ),
            A.RandomShadow(
                shadow_roi=(0.0, 0.35, 1.0, 1.0),
                num_shadows_limit=(1, 3),
                shadow_dimension=6,
                p=0.35,
            ),
        ],
        bbox_params=A.BboxParams(
            format="yolo",
            label_fields=["class_labels"],
            min_visibility=min_visibility,
        ),
    )


def copy_split(dataset_root: Path, output_root: Path, split: str) -> None:
    source_images = dataset_root / "images" / split
    source_labels = dataset_root / "labels" / split
    target_images = output_root / "images" / split
    target_labels = output_root / "labels" / split

    if source_images.exists():
        shutil.copytree(source_images, target_images, dirs_exist_ok=True)
    if source_labels.exists():
        shutil.copytree(source_labels, target_labels, dirs_exist_ok=True)


def clone_data_yaml(data_yaml: Path, output_root: Path) -> Path:
    import yaml

    with data_yaml.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    config["path"] = str(output_root.resolve())
    output_yaml = output_root / data_yaml.name
    with output_yaml.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(config, handle, sort_keys=False)

    return output_yaml


def main() -> None:
    import cv2

    args = parse_args()
    dataset_root = Path(args.dataset_root).resolve()
    output_root = prepare_output_root(Path(args.output_root).resolve(), args.overwrite)

    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root not found: {dataset_root}")

    for split in ("train", "val", "test"):
        copy_split(dataset_root, output_root, split)

    augment_split = args.augment_split
    input_images_dir = dataset_root / "images" / augment_split
    input_labels_dir = dataset_root / "labels" / augment_split
    output_images_dir = output_root / "images" / augment_split
    output_labels_dir = output_root / "labels" / augment_split

    pipeline = build_augmentation_pipeline(args.min_visibility)
    image_paths = list_images(input_images_dir)

    if not image_paths:
        raise FileNotFoundError(f"No images found in split: {input_images_dir}")

    print(f"Found {len(image_paths)} images in {input_images_dir}")

    generated = 0
    for index, image_path in enumerate(image_paths, start=1):
        relative_stem = image_path.relative_to(input_images_dir).with_suffix("")
        label_path = input_labels_dir / relative_stem.with_suffix(".txt")
        bboxes, class_labels = read_yolo_labels(label_path)

        image = cv2.imread(str(image_path))
        if image is None:
            print(f"[warning] Skipping unreadable image: {image_path}")
            continue

        for copy_idx in range(args.copies_per_image):
            transformed = pipeline(
                image=image,
                bboxes=bboxes,
                class_labels=class_labels,
            )

            augmented_image = transformed["image"]
            augmented_bboxes = [list(bbox) for bbox in transformed["bboxes"]]
            augmented_labels = list(transformed["class_labels"])

            output_image_path = output_images_dir / relative_stem.parent / f"{relative_stem.name}_aug_{copy_idx + 1}{image_path.suffix}"
            output_label_path = output_labels_dir / relative_stem.parent / f"{relative_stem.name}_aug_{copy_idx + 1}.txt"

            output_image_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_image_path), augmented_image)
            write_yolo_labels(output_label_path, augmented_bboxes, augmented_labels)
            generated += 1

        if index % 25 == 0 or index == len(image_paths):
            print(f"Processed {index}/{len(image_paths)} images")

    if args.data_yaml:
        output_yaml = clone_data_yaml(Path(args.data_yaml).resolve(), output_root)
        print(f"Wrote updated data.yaml to: {output_yaml}")

    print(f"Augmentation complete. Generated {generated} augmented images in {output_root}")


if __name__ == "__main__":
    main()
