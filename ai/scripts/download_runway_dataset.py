"""
Download a runway / FOD dataset from Roboflow or Kaggle.

Examples:
    python ai/scripts/download_runway_dataset.py roboflow ^
        --workspace your-workspace ^
        --project runway-fod ^
        --version 3 ^
        --format yolov8 ^
        --output-dir ai/datasets/fod_runway

    python ai/scripts/download_runway_dataset.py kaggle ^
        --dataset username/runway-fod-dataset ^
        --output-dir ai/datasets/kaggle_runway ^
        --unzip
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a runway hazard dataset from Roboflow or Kaggle."
    )
    subparsers = parser.add_subparsers(dest="provider", required=True)

    roboflow_parser = subparsers.add_parser(
        "roboflow",
        help="Download a versioned dataset export from Roboflow.",
    )
    roboflow_parser.add_argument(
        "--api-key",
        default=os.getenv("ROBOFLOW_API_KEY"),
        help="Roboflow API key. Defaults to the ROBOFLOW_API_KEY environment variable.",
    )
    roboflow_parser.add_argument("--workspace", required=True, help="Roboflow workspace slug.")
    roboflow_parser.add_argument("--project", required=True, help="Roboflow project slug.")
    roboflow_parser.add_argument("--version", required=True, type=int, help="Dataset version number.")
    roboflow_parser.add_argument(
        "--format",
        default="yolov8",
        help="Export format, e.g. yolov8, coco, voc, darknet.",
    )
    roboflow_parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "ai" / "datasets" / "fod_runway"),
        help="Directory where the dataset should be downloaded.",
    )
    roboflow_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete the target directory first if it already exists.",
    )

    kaggle_parser = subparsers.add_parser(
        "kaggle",
        help="Download a dataset from Kaggle using the official Kaggle API.",
    )
    kaggle_parser.add_argument(
        "--dataset",
        required=True,
        help="Dataset slug in owner/dataset-name form.",
    )
    kaggle_parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "ai" / "datasets" / "kaggle_runway"),
        help="Directory where the dataset should be downloaded.",
    )
    kaggle_parser.add_argument(
        "--unzip",
        action="store_true",
        help="Unzip the Kaggle download after it completes.",
    )
    kaggle_parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if files already exist.",
    )
    kaggle_parser.add_argument(
        "--file",
        help="Optional single file inside the Kaggle dataset to download.",
    )

    return parser.parse_args()


def prepare_output_dir(output_dir: Path, overwrite: bool) -> Path:
    if overwrite and output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def download_from_roboflow(args: argparse.Namespace) -> dict[str, str]:
    if not args.api_key:
        raise ValueError(
            "Roboflow API key is required. Pass --api-key or set ROBOFLOW_API_KEY."
        )

    try:
        from roboflow import Roboflow
    except ImportError as exc:
        raise ImportError(
            "roboflow is not installed. Install it with `pip install roboflow`."
        ) from exc

    output_dir = prepare_output_dir(Path(args.output_dir).resolve(), args.overwrite)

    rf = Roboflow(api_key=args.api_key)
    project = rf.workspace(args.workspace).project(args.project)
    version = project.version(args.version)

    try:
        dataset = version.download(args.format, location=str(output_dir), overwrite=args.overwrite)
    except TypeError:
        dataset = version.download(args.format, location=str(output_dir))

    location = getattr(dataset, "location", str(output_dir))

    return {
        "provider": "roboflow",
        "workspace": args.workspace,
        "project": args.project,
        "version": str(args.version),
        "format": args.format,
        "output_dir": str(Path(location).resolve()),
    }


def download_from_kaggle(args: argparse.Namespace) -> dict[str, str]:
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError as exc:
        raise ImportError(
            "kaggle is not installed. Install it with `pip install kaggle`."
        ) from exc

    output_dir = prepare_output_dir(Path(args.output_dir).resolve(), overwrite=False)

    api = KaggleApi()
    api.authenticate()

    if args.file:
        api.dataset_download_file(
            dataset=args.dataset,
            file_name=args.file,
            path=str(output_dir),
            force=args.force,
            quiet=False,
        )
    else:
        api.dataset_download_files(
            dataset=args.dataset,
            path=str(output_dir),
            unzip=args.unzip,
            force=args.force,
            quiet=False,
        )

    return {
        "provider": "kaggle",
        "dataset": args.dataset,
        "downloaded_file": args.file or "all",
        "output_dir": str(output_dir),
        "unzip": str(args.unzip),
    }


def main() -> None:
    args = parse_args()

    if args.provider == "roboflow":
        summary = download_from_roboflow(args)
    elif args.provider == "kaggle":
        summary = download_from_kaggle(args)
    else:
        raise ValueError(f"Unsupported provider: {args.provider}")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
