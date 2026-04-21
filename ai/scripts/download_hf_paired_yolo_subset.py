"""
Download a public Hugging Face dataset repo that already stores paired YOLO images/labels.

Example:
    python ai/scripts/download_hf_paired_yolo_subset.py ^
        --repo windysir/military-aircraft-detection-dataset ^
        --train-image-prefix images/ ^
        --train-label-prefix annotations/yolo/train/ ^
        --val-image-prefix images/ ^
        --val-label-prefix annotations/yolo/val/ ^
        --test-image-prefix images/ ^
        --test-label-prefix annotations/yolo/test/ ^
        --output-dir ai/datasets/aircraft_hf_source ^
        --class-id 0
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download


REPO_ROOT = Path(__file__).resolve().parents[2]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
HF_LOCAL_CACHE = REPO_ROOT / "ai" / "datasets" / "downloads" / "hf_local_cache"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download paired YOLO image/label files from a public Hugging Face dataset repo."
    )
    parser.add_argument("--repo", required=True, help="HF dataset repo id.")
    parser.add_argument("--output-dir", required=True, help="Destination YOLO dataset root.")
    parser.add_argument("--train-image-prefix", required=True)
    parser.add_argument("--train-label-prefix", required=True)
    parser.add_argument("--val-image-prefix", required=True)
    parser.add_argument("--val-label-prefix", required=True)
    parser.add_argument("--test-image-prefix", required=True)
    parser.add_argument("--test-label-prefix", required=True)
    parser.add_argument("--max-train", type=int, default=3000)
    parser.add_argument("--max-val", type=int, default=600)
    parser.add_argument("--max-test", type=int, default=600)
    parser.add_argument(
        "--class-id",
        type=int,
        default=None,
        help="If provided, rewrite kept label lines to this single class id.",
    )
    parser.add_argument(
        "--source-class-ids",
        nargs="*",
        type=int,
        default=None,
        help="Optional source class ids to keep. Other classes are dropped before writing labels.",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def normalize_stem(path: str) -> str:
    return Path(path).stem


def rewrite_class_ids(
    src_label: Path,
    dst_label: Path,
    class_id: int | None,
    source_class_ids: set[int] | None,
) -> bool:
    lines = []
    for raw_line in src_label.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = raw_line.strip().split()
        if len(parts) < 5:
            continue
        source_id = int(float(parts[0]))
        if source_class_ids is not None and source_id not in source_class_ids:
            continue
        target_id = class_id if class_id is not None else source_id
        lines.append(" ".join([str(target_id), *parts[1:]]))
    if not lines:
        return False
    dst_label.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def copy_or_rewrite_label(
    src_label: Path,
    dst_label: Path,
    class_id: int | None,
    source_class_ids: set[int] | None,
) -> bool:
    dst_label.parent.mkdir(parents=True, exist_ok=True)
    if class_id is None and source_class_ids is None:
        shutil.copy2(src_label, dst_label)
        return True
    return rewrite_class_ids(src_label, dst_label, class_id, source_class_ids)


def prepare_output(output_dir: Path, overwrite: bool) -> None:
    if overwrite and output_dir.exists():
        shutil.rmtree(output_dir)
    for split in ("train", "val", "test"):
        (output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)


def download_split(
    *,
    api: HfApi,
    repo: str,
    image_prefix: str,
    label_prefix: str,
    split: str,
    limit: int,
    output_dir: Path,
    class_id: int | None,
    source_class_ids: set[int] | None,
) -> int:
    siblings = api.dataset_info(repo).siblings
    image_files = [
        sibling.rfilename
        for sibling in siblings
        if sibling.rfilename.startswith(image_prefix)
        and Path(sibling.rfilename).suffix.lower() in IMAGE_EXTENSIONS
    ]
    label_files = {
        normalize_stem(sibling.rfilename): sibling.rfilename
        for sibling in siblings
        if sibling.rfilename.startswith(label_prefix) and sibling.rfilename.endswith(".txt")
    }

    selected_count = 0
    for image_file in sorted(image_files):
        if selected_count >= limit:
            break
        stem = normalize_stem(image_file)
        label_file = label_files.get(stem)
        if not label_file:
            continue

        cached_image = Path(
            hf_hub_download(
                repo,
                image_file,
                repo_type="dataset",
                local_dir=str(HF_LOCAL_CACHE / repo.replace("/", "__")),
                local_dir_use_symlinks=False,
            )
        )
        cached_label = Path(
            hf_hub_download(
                repo,
                label_file,
                repo_type="dataset",
                local_dir=str(HF_LOCAL_CACHE / repo.replace("/", "__")),
                local_dir_use_symlinks=False,
            )
        )
        dst_image = output_dir / "images" / split / cached_image.name
        dst_label = output_dir / "labels" / split / f"{stem}.txt"
        kept = copy_or_rewrite_label(cached_label, dst_label, class_id, source_class_ids)
        if not kept:
            if dst_label.exists():
                dst_label.unlink()
            continue
        shutil.copy2(cached_image, dst_image)
        selected_count += 1

        if selected_count % 250 == 0 or selected_count == limit:
            print(f"[{split}] downloaded {selected_count}/{limit}")

    return selected_count


def main() -> None:
    args = parse_args()
    output_dir = (REPO_ROOT / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir).resolve()
    prepare_output(output_dir, overwrite=args.overwrite)
    api = HfApi()

    counts = {
        "train": download_split(
            api=api,
            repo=args.repo,
            image_prefix=args.train_image_prefix,
            label_prefix=args.train_label_prefix,
            split="train",
            limit=args.max_train,
            output_dir=output_dir,
            class_id=args.class_id,
            source_class_ids=set(args.source_class_ids) if args.source_class_ids is not None else None,
        ),
        "val": download_split(
            api=api,
            repo=args.repo,
            image_prefix=args.val_image_prefix,
            label_prefix=args.val_label_prefix,
            split="val",
            limit=args.max_val,
            output_dir=output_dir,
            class_id=args.class_id,
            source_class_ids=set(args.source_class_ids) if args.source_class_ids is not None else None,
        ),
        "test": download_split(
            api=api,
            repo=args.repo,
            image_prefix=args.test_image_prefix,
            label_prefix=args.test_label_prefix,
            split="test",
            limit=args.max_test,
            output_dir=output_dir,
            class_id=args.class_id,
            source_class_ids=set(args.source_class_ids) if args.source_class_ids is not None else None,
        ),
    }

    print({"output_dir": str(output_dir), "counts": counts})


if __name__ == "__main__":
    main()
