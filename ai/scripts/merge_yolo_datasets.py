"""
Merge multiple YOLO-format datasets into one unified master dataset.

Each source dataset can provide its own class-id remapping so labels are rewritten
to match the project's canonical class order.

Example:
    python ai/scripts/merge_yolo_datasets.py ^
        --dataset birds=ai/datasets/birds ^
        --dataset aircraft=ai/datasets/aircraft ^
        --dataset spills=ai/datasets/fuel_spill ^
        --class-map birds="{\"0\": 1}" ^
        --class-map aircraft="{\"0\": 6}" ^
        --class-map spills="{\"0\": 7}" ^
        --oversample birds=4 ^
        --oversample aircraft=8 ^
        --output-dir ai/datasets/fod_master ^
        --overwrite
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "ai" / "datasets" / "fod_master"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
CANONICAL_NAMES = {
    0: "Debris",
    1: "Wildlife_Birds",
    2: "Vehicles",
    3: "Cracks",
    4: "Luggage",
    5: "Personnel",
    6: "Aircraft",
    7: "Fuel_Spill",
    8: "Standing_Water",
    9: "Potholes",
    10: "Tool_Equipment",
    11: "Cone_or_Barrier",
}
SPLIT_ALIASES = {
    "train": ("train",),
    "val": ("val", "valid"),
    "test": ("test",),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge multiple YOLO datasets into a single master dataset."
    )
    parser.add_argument(
        "--dataset",
        action="append",
        required=True,
        help="Dataset spec in alias=path form. Repeat for each input dataset.",
    )
    parser.add_argument(
        "--class-map",
        action="append",
        default=[],
        help='Class remap in alias={"0": 1, "2": 6} form. Repeat for each dataset.',
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Destination master dataset directory.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete the output directory first if it already exists.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any source label contains an unmapped class id.",
    )
    parser.add_argument(
        "--oversample",
        action="append",
        default=[],
        help="Optional train-only repetition factor in alias=factor form, e.g. birds=4.",
    )
    return parser.parse_args()


def parse_alias_path(spec: str) -> tuple[str, Path]:
    if "=" not in spec:
        raise ValueError(f"Invalid --dataset value '{spec}'. Expected alias=path.")
    alias, raw_path = spec.split("=", 1)
    alias = alias.strip()
    raw_path = raw_path.strip()
    if not alias or not raw_path:
        raise ValueError(f"Invalid --dataset value '{spec}'. Expected alias=path.")
    return alias, Path(raw_path).resolve()


def parse_class_maps(specs: list[str]) -> dict[str, dict[int, int]]:
    parsed: dict[str, dict[int, int]] = {}
    for spec in specs:
        if "=" not in spec:
            raise ValueError(
                f"Invalid --class-map value '{spec}'. Expected alias={{...}}."
            )
        alias, raw_json = spec.split("=", 1)
        alias = alias.strip()
        if not alias:
            raise ValueError(f"Invalid --class-map value '{spec}'. Alias is missing.")

        mapping = json.loads(raw_json)
        if not isinstance(mapping, dict):
            raise ValueError(f"Class map for '{alias}' must be a JSON object.")

        clean_map: dict[int, int] = {}
        for source_id, target_id in mapping.items():
            source_int = int(source_id)
            target_int = int(target_id)
            if target_int not in CANONICAL_NAMES:
                raise ValueError(
                    f"Target class id {target_int} for dataset '{alias}' is outside the canonical range 0-11."
                )
            clean_map[source_int] = target_int
        parsed[alias] = clean_map
    return parsed


def parse_int_map(specs: list[str], *, field_name: str) -> dict[str, int]:
    parsed: dict[str, int] = {}
    for spec in specs:
        if "=" not in spec:
            raise ValueError(f"Invalid --{field_name} value '{spec}'. Expected alias=value.")
        alias, raw_value = spec.split("=", 1)
        alias = alias.strip()
        value = int(raw_value.strip())
        if not alias:
            raise ValueError(f"Invalid --{field_name} value '{spec}'. Alias is missing.")
        if value < 1:
            raise ValueError(f"--{field_name} factor for '{alias}' must be >= 1.")
        parsed[alias] = value
    return parsed


def discover_split_dir(dataset_root: Path, split: str, kind: str) -> Path | None:
    for split_name in SPLIT_ALIASES[split]:
        candidates = [
            dataset_root / kind / split_name,
            dataset_root / split_name / kind,
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate
    return None


def dataset_has_standard_splits(dataset_root: Path) -> bool:
    for split in ("train", "val", "test"):
        if discover_split_dir(dataset_root, split, "images") and discover_split_dir(dataset_root, split, "labels"):
            return True
    return False


def prepare_output_dir(output_dir: Path, overwrite: bool) -> None:
    if overwrite and output_dir.exists():
        shutil.rmtree(output_dir)

    for split in ("train", "val", "test"):
        (output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)


def copy_image(src_image: Path, dst_image: Path) -> None:
    dst_image.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_image, dst_image)


def remap_label_file(
    src_label: Path,
    dst_label: Path,
    class_map: dict[int, int],
    strict: bool,
    counts: Counter[int],
) -> None:
    dst_label.parent.mkdir(parents=True, exist_ok=True)
    rewritten_lines: list[str] = []

    for raw_line in src_label.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) < 5:
            raise ValueError(f"Malformed YOLO label line in {src_label}: '{raw_line}'")

        source_class_id = int(parts[0])
        if source_class_id not in class_map:
            if strict:
                raise ValueError(
                    f"Source class id {source_class_id} in {src_label} has no mapping."
                )
            continue

        target_class_id = class_map[source_class_id]
        counts[target_class_id] += 1
        rewritten_lines.append(" ".join([str(target_class_id), *parts[1:]]))

    dst_label.write_text("\n".join(rewritten_lines) + ("\n" if rewritten_lines else ""), encoding="utf-8")


def merge_dataset(
    alias: str,
    dataset_root: Path,
    output_dir: Path,
    class_map: dict[int, int],
    strict: bool,
    oversample_factor: int,
) -> dict[str, object]:
    if not dataset_root.exists():
        raise FileNotFoundError(f"Dataset root does not exist: {dataset_root}")
    if not dataset_has_standard_splits(dataset_root):
        raise ValueError(
            f"Dataset '{alias}' does not look like a YOLO dataset with images/<split> and labels/<split>: {dataset_root}"
        )

    split_image_counts: Counter[str] = Counter()
    split_label_counts: Counter[str] = Counter()
    class_counts: Counter[int] = Counter()
    collision_guard: set[str] = set()

    for split in ("train", "val", "test"):
        src_images_dir = discover_split_dir(dataset_root, split, "images")
        src_labels_dir = discover_split_dir(dataset_root, split, "labels")
        if src_images_dir is None or src_labels_dir is None:
            continue

        for src_image in sorted(src_images_dir.iterdir()):
            if not src_image.is_file() or src_image.suffix.lower() not in IMAGE_EXTENSIONS:
                continue

            src_label = src_labels_dir / f"{src_image.stem}.txt"
            if not src_label.exists():
                if strict:
                    raise FileNotFoundError(f"Missing label file for image: {src_image}")
                continue

            repeat_count = oversample_factor if split == "train" else 1
            for repeat_idx in range(repeat_count):
                output_stem = (
                    f"{alias}__{src_image.stem}"
                    if repeat_idx == 0
                    else f"{alias}__{src_image.stem}__os{repeat_idx + 1}"
                )
                if output_stem in collision_guard:
                    raise ValueError(
                        f"Filename collision detected after prefixing alias '{alias}': {output_stem}"
                    )
                collision_guard.add(output_stem)

                dst_image = output_dir / "images" / split / f"{output_stem}{src_image.suffix.lower()}"
                dst_label = output_dir / "labels" / split / f"{output_stem}.txt"

                copy_image(src_image, dst_image)
                remap_label_file(src_label, dst_label, class_map, strict, class_counts)

                split_image_counts[split] += 1
                split_label_counts[split] += 1

    return {
        "alias": alias,
        "dataset_root": str(dataset_root),
        "class_map": class_map,
        "oversample_factor": oversample_factor,
        "images_per_split": dict(split_image_counts),
        "labels_per_split": dict(split_label_counts),
        "class_counts": {CANONICAL_NAMES[k]: v for k, v in sorted(class_counts.items())},
    }


def write_master_yaml(output_dir: Path) -> Path:
    data = {
        "path": output_dir.as_posix(),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": len(CANONICAL_NAMES),
        "names": CANONICAL_NAMES,
    }
    yaml_path = output_dir / "data.yaml"
    with yaml_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=False)
    return yaml_path


def main() -> None:
    args = parse_args()
    datasets = dict(parse_alias_path(spec) for spec in args.dataset)
    class_maps = parse_class_maps(args.class_map)
    oversample_map = parse_int_map(args.oversample, field_name="oversample")
    output_dir = Path(args.output_dir).resolve()

    missing_maps = [alias for alias in datasets if alias not in class_maps]
    if missing_maps:
        raise ValueError(
            "Missing --class-map entries for dataset alias(es): "
            + ", ".join(sorted(missing_maps))
        )

    prepare_output_dir(output_dir, overwrite=args.overwrite)

    merged: list[dict[str, object]] = []
    aggregate_counts: Counter[str] = Counter()
    for alias, dataset_root in datasets.items():
        summary = merge_dataset(
            alias=alias,
            dataset_root=dataset_root,
            output_dir=output_dir,
            class_map=class_maps[alias],
            strict=args.strict,
            oversample_factor=oversample_map.get(alias, 1),
        )
        merged.append(summary)
        for class_name, count in summary["class_counts"].items():
            aggregate_counts[class_name] += count

    yaml_path = write_master_yaml(output_dir)
    manifest = {
        "output_dir": str(output_dir),
        "master_yaml": str(yaml_path),
        "canonical_names": CANONICAL_NAMES,
        "datasets": merged,
        "aggregate_class_counts": dict(sorted(aggregate_counts.items())),
    }

    manifest_path = output_dir / "merge_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
