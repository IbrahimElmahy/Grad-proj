"""
Train or fine-tune a YOLO detector for runway hazard detection.

This version is tuned for the RVMS ultra-performance workflow:
- supports YOLOv8m at imgsz 960
- exposes advanced augmentations for tiny-object robustness
- uses virtual batch sizing via Ultralytics' `nbs` to approximate gradient accumulation
- validates after training and can optionally export deployment artifacts

Example:
    python ai/scripts/train_yolo_fod.py ^
        --data ai/configs/fod_data.yaml ^
        --weights yolov8m.pt ^
        --epochs 100 ^
        --imgsz 960 ^
        --batch 1 ^
        --accumulate 8 ^
        --device 0 ^
        --name rvms_ultra_v8m
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import yaml
from ultralytics import YOLO


REPO_ROOT = Path(__file__).resolve().parents[2]


def find_default_weights() -> str:
    candidates = [
        REPO_ROOT / "backend" / "ai_engine" / "models" / "best_unified_12c.pt",
        REPO_ROOT / "backend" / "ai_engine" / "models" / "best_unified.pt",
        REPO_ROOT / "backend" / "ai_engine" / "models" / "best.pt",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return "yolov8m.pt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train or fine-tune a YOLO model for runway hazard detection."
    )
    parser.add_argument("--data", required=True, help="Path to the dataset YAML file.")
    parser.add_argument(
        "--weights",
        default=find_default_weights(),
        help="Base model weights (.pt) or a model name such as yolov8m.pt.",
    )
    parser.add_argument("--epochs", type=int, default=100, help="Training epochs.")
    parser.add_argument("--imgsz", type=int, default=960, help="Training image size.")
    parser.add_argument(
        "--batch",
        type=int,
        default=1,
        help="Physical batch size. Keep 1 on a 4 GB GPU and use --accumulate to simulate larger batches.",
    )
    parser.add_argument(
        "--accumulate",
        type=int,
        default=8,
        help="Virtual gradient accumulation target. Implemented via Ultralytics nbs scaling.",
    )
    parser.add_argument("--device", default="0", help="CUDA device id, cpu, or 0,1 style list.")
    parser.add_argument("--workers", type=int, default=4, help="Dataloader workers.")
    parser.add_argument(
        "--project",
        default=str(REPO_ROOT / "ai" / "outputs" / "training"),
        help="Base directory where Ultralytics stores training runs.",
    )
    parser.add_argument("--name", default="rvms_ultra_v8m", help="Training run name.")
    parser.add_argument("--optimizer", default="AdamW", help="Optimizer name.")
    parser.add_argument("--lr0", type=float, default=0.001, help="Initial learning rate.")
    parser.add_argument("--lrf", type=float, default=0.01, help="Final learning rate factor.")
    parser.add_argument("--patience", type=int, default=30, help="Early stopping patience.")
    parser.add_argument("--freeze", type=int, default=0, help="Freeze first N layers.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--save-period", type=int, default=10, help="Periodic checkpoint cadence.")
    parser.add_argument("--resume", action="store_true", help="Resume from --weights.")
    parser.add_argument("--cache", action="store_true", help="Cache images in RAM.")
    parser.add_argument("--cos-lr", action="store_true", help="Enable cosine LR scheduling.")
    parser.add_argument("--multi-scale", action="store_true", help="Enable dynamic multi-scale training.")
    parser.add_argument("--no-amp", action="store_true", help="Disable mixed precision training.")
    parser.add_argument("--exist-ok", action="store_true", help="Reuse an existing run directory.")
    parser.add_argument("--close-mosaic", type=int, default=10, help="Disable mosaic in the final N epochs.")
    parser.add_argument("--mosaic", type=float, default=1.0, help="Mosaic augmentation probability.")
    parser.add_argument("--mixup", type=float, default=0.15, help="MixUp augmentation probability.")
    parser.add_argument("--copy-paste", type=float, default=0.0, help="Copy-paste augmentation probability.")
    parser.add_argument("--degrees", type=float, default=2.0, help="Random rotation degrees.")
    parser.add_argument("--translate", type=float, default=0.12, help="Random translation fraction.")
    parser.add_argument("--scale", type=float, default=0.35, help="Random scaling gain.")
    parser.add_argument("--shear", type=float, default=2.0, help="Random shear degrees.")
    parser.add_argument("--perspective", type=float, default=0.0006, help="Random perspective factor.")
    parser.add_argument("--hsv-h", type=float, default=0.015, help="HSV hue augmentation.")
    parser.add_argument("--hsv-s", type=float, default=0.7, help="HSV saturation augmentation.")
    parser.add_argument("--hsv-v", type=float, default=0.45, help="HSV value augmentation.")
    parser.add_argument("--fliplr", type=float, default=0.5, help="Horizontal flip probability.")
    parser.add_argument("--flipud", type=float, default=0.0, help="Vertical flip probability.")
    parser.add_argument("--box", type=float, default=7.5, help="Bounding-box loss gain.")
    parser.add_argument("--cls", type=float, default=0.5, help="Classification loss gain.")
    parser.add_argument("--dfl", type=float, default=1.5, help="Distribution focal loss gain.")
    parser.add_argument(
        "--label-smoothing",
        type=float,
        default=0.0,
        help="Classification label smoothing factor.",
    )
    parser.add_argument(
        "--export-formats",
        nargs="*",
        default=["engine"],
        help="Optional export formats after training, e.g. engine onnx. Leave empty to skip.",
    )
    parser.add_argument("--export-half", action="store_true", help="Use FP16 for export where supported.")
    parser.add_argument("--export-imgsz", type=int, default=960, help="Image size for export.")
    parser.add_argument("--export-device", default="0", help="Device used for export.")
    return parser.parse_args()


def load_dataset_config(data_yaml: Path) -> dict[str, Any]:
    with data_yaml.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    required_keys = {"train", "val", "names"}
    missing = required_keys - set(config)
    if missing:
        raise ValueError(
            f"Dataset config is missing required keys: {', '.join(sorted(missing))}"
        )

    names = config["names"]
    if isinstance(names, dict):
        class_names = [names[idx] for idx in sorted(names)]
    elif isinstance(names, list):
        class_names = names
    else:
        raise ValueError("'names' must be a list or dictionary in data.yaml")

    if "nc" in config and int(config["nc"]) != len(class_names):
        raise ValueError(
            f"'nc' is {config['nc']} but there are {len(class_names)} classes in 'names'"
        )

    dataset_root = (data_yaml.parent / config.get("path", ".")).resolve()
    for split_key in ("train", "val", "test"):
        split_path = config.get(split_key)
        if split_path:
            resolved = (dataset_root / split_path).resolve()
            if not resolved.exists():
                print(f"[warning] {split_key} path does not exist yet: {resolved}")

    return {
        "dataset_root": str(dataset_root),
        "class_names": class_names,
        "class_count": len(class_names),
    }


def summarize_metrics(metrics: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    box_metrics = getattr(metrics, "box", None)
    if box_metrics is not None:
        summary["mAP50"] = getattr(box_metrics, "map50", None)
        summary["mAP50-95"] = getattr(box_metrics, "map", None)
        summary["precision"] = getattr(box_metrics, "mp", None)
        summary["recall"] = getattr(box_metrics, "mr", None)
        if hasattr(box_metrics, "maps"):
            summary["per_class_map50_95"] = [
                round(float(value), 6) for value in list(box_metrics.maps)
            ]
    return {key: value for key, value in summary.items() if value is not None}


def compute_nominal_batch(batch: int, accumulate: int) -> int:
    if batch <= 0:
        return max(accumulate, 1)
    return max(batch * accumulate, batch)


def export_artifacts(model: YOLO, best_weights: Path, args: argparse.Namespace) -> dict[str, str]:
    exports: dict[str, str] = {}
    if not best_weights.exists():
        print(f"[warning] Best weights not found for export: {best_weights}")
        return exports

    export_model = YOLO(str(best_weights))
    for fmt in args.export_formats:
        try:
            result = export_model.export(
                format=fmt,
                imgsz=args.export_imgsz,
                device=args.export_device,
                half=args.export_half,
            )
            exports[fmt] = str(result)
        except Exception as exc:
            exports[fmt] = f"FAILED: {exc}"
            print(f"[warning] Export to {fmt} failed: {exc}")
    return exports


def main() -> None:
    args = parse_args()
    data_yaml = Path(args.data).resolve()
    if not data_yaml.exists():
        raise FileNotFoundError(f"Dataset YAML was not found: {data_yaml}")

    dataset_info = load_dataset_config(data_yaml)
    nominal_batch = compute_nominal_batch(args.batch, args.accumulate)
    run_dir = Path(args.project).resolve() / args.name

    print("Dataset root:", dataset_info["dataset_root"])
    print("Classes:", ", ".join(dataset_info["class_names"]))
    print("Base weights:", args.weights)
    print("Ultralytics detect loss uses CIoU internally for bbox regression.")
    print(f"Requested physical batch={args.batch}, virtual accumulate={args.accumulate}, nominal batch (nbs)={nominal_batch}")

    model = YOLO(args.weights)
    train_kwargs = {
        "data": str(data_yaml),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "batch": args.batch,
        "device": args.device,
        "workers": args.workers,
        "project": str(Path(args.project).resolve()),
        "name": args.name,
        "optimizer": args.optimizer,
        "lr0": args.lr0,
        "lrf": args.lrf,
        "patience": args.patience,
        "seed": args.seed,
        "save_period": args.save_period,
        "cache": args.cache,
        "cos_lr": args.cos_lr,
        "amp": not args.no_amp,
        "exist_ok": args.exist_ok,
        "plots": True,
        "resume": args.resume,
        "multi_scale": args.multi_scale,
        "close_mosaic": args.close_mosaic,
        "mosaic": args.mosaic,
        "mixup": args.mixup,
        "copy_paste": args.copy_paste,
        "degrees": args.degrees,
        "translate": args.translate,
        "scale": args.scale,
        "shear": args.shear,
        "perspective": args.perspective,
        "hsv_h": args.hsv_h,
        "hsv_s": args.hsv_s,
        "hsv_v": args.hsv_v,
        "fliplr": args.fliplr,
        "flipud": args.flipud,
        "box": args.box,
        "cls": args.cls,
        "dfl": args.dfl,
        "label_smoothing": args.label_smoothing,
        "nbs": nominal_batch,
    }
    if args.freeze > 0:
        train_kwargs["freeze"] = args.freeze

    print("Starting training with configuration:")
    print(json.dumps(train_kwargs, indent=2))
    model.train(**train_kwargs)

    best_weights = run_dir / "weights" / "best.pt"
    print("Running validation on the trained model...")
    metrics = model.val(
        data=str(data_yaml),
        imgsz=args.imgsz,
        batch=max(args.batch, 1),
        device=args.device,
        split="val",
        plots=True,
    )

    metrics_summary = summarize_metrics(metrics)
    export_summary = export_artifacts(model, best_weights, args) if args.export_formats else {}
    final_summary = {
        "run_dir": str(run_dir),
        "best_weights": str(best_weights),
        "last_weights": str(run_dir / "weights" / "last.pt"),
        "metrics": metrics_summary,
        "exports": export_summary,
    }

    print("Final summary:")
    print(json.dumps(final_summary, indent=2))

    summary_path = run_dir / "training_summary.json"
    summary_path.write_text(json.dumps(final_summary, indent=2), encoding="utf-8")
    print(f"Training complete. Summary written to: {summary_path}")


if __name__ == "__main__":
    main()
