"""
Build a YOLO-format bird detection subset from the public torchgeo/bird_detection dataset.

It downloads the metadata parquet plus split archive parts, combines the archive,
extracts only the requested images, and writes class-0 YOLO labels.
"""

from __future__ import annotations

import argparse
import shutil
import tarfile
from pathlib import Path

import pandas as pd
from huggingface_hub import hf_hub_download


REPO_ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a YOLO bird subset from torchgeo/bird_detection.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-train", type=int, default=3000)
    parser.add_argument("--max-val", type=int, default=600)
    parser.add_argument("--max-test", type=int, default=600)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def prepare_output(output_dir: Path, overwrite: bool) -> None:
    if overwrite and output_dir.exists():
        shutil.rmtree(output_dir)
    for split in ("train", "val", "test"):
        (output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)


def combine_parts(part_a: Path, part_b: Path, combined_path: Path) -> Path:
    if combined_path.exists():
        return combined_path
    with combined_path.open("wb") as handle:
        handle.write(part_a.read_bytes())
        handle.write(part_b.read_bytes())
    return combined_path


def yolo_lines(group: pd.DataFrame, img_w: int, img_h: int) -> list[str]:
    lines = []
    for _, row in group.iterrows():
        x1, y1, x2, y2 = float(row["xmin"]), float(row["ymin"]), float(row["xmax"]), float(row["ymax"])
        w = max(x2 - x1, 1.0)
        h = max(y2 - y1, 1.0)
        x_center = (x1 + w / 2) / img_w
        y_center = (y1 + h / 2) / img_h
        lines.append(f"0 {x_center:.6f} {y_center:.6f} {w / img_w:.6f} {h / img_h:.6f}")
    return lines


def main() -> None:
    args = parse_args()
    output_dir = (REPO_ROOT / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir).resolve()
    prepare_output(output_dir, overwrite=args.overwrite)

    metadata_path = Path(hf_hub_download("torchgeo/bird_detection", "metadata.parquet", repo_type="dataset"))
    part_a = Path(hf_hub_download("torchgeo/bird_detection", "images.tar.gzaa", repo_type="dataset"))
    part_b = Path(hf_hub_download("torchgeo/bird_detection", "images.tar.gzab", repo_type="dataset"))
    combined_tar = combine_parts(part_a, part_b, metadata_path.parent / "images.tar.gz")

    df = pd.read_parquet(metadata_path)
    split_limits = {"train": args.max_train, "val": args.max_val, "test": args.max_test}
    split_name_map = {"train": "train", "val": "val", "test": "test"}

    selected_groups: dict[str, pd.DataFrame] = {}
    selected_paths: set[str] = set()
    for source_split, target_split in split_name_map.items():
        subset = df[df["split"] == source_split].copy()
        image_order = subset["image_path"].drop_duplicates().tolist()[: split_limits[target_split]]
        subset = subset[subset["image_path"].isin(image_order)]
        selected_groups[target_split] = subset
        selected_paths.update(image_order)
        print(f"[{target_split}] selected {len(image_order)} images and {len(subset)} boxes")

    with tarfile.open(combined_tar, "r:gz") as archive:
        members = {member.name: member for member in archive.getmembers() if member.isfile()}
        for target_split, subset in selected_groups.items():
            grouped = subset.groupby("image_path")
            processed = 0
            for image_path, group in grouped:
                member = members.get(image_path)
                if member is None:
                    continue
                extracted = archive.extractfile(member)
                if extracted is None:
                    continue
                image_bytes = extracted.read()
                dst_image = output_dir / "images" / target_split / Path(image_path).name
                dst_image.write_bytes(image_bytes)

                import cv2
                import numpy as np

                image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
                if image is None:
                    dst_image.unlink(missing_ok=True)
                    continue
                img_h, img_w = image.shape[:2]
                lines = yolo_lines(group, img_w, img_h)
                dst_label = output_dir / "labels" / target_split / f"{Path(image_path).stem}.txt"
                dst_label.write_text("\n".join(lines) + "\n", encoding="utf-8")
                processed += 1
                if processed % 250 == 0:
                    print(f"[{target_split}] extracted {processed}")

            print(f"[{target_split}] total extracted {processed}")


if __name__ == "__main__":
    main()
