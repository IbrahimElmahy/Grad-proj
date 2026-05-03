"""
Run YOLO inference for airport runway hazards and export structured logs.

Features:
1. CLAHE preprocessing for low-light runway footage.
2. ByteTrack-based persistent IDs in the default full-frame path.
3. Optional slicing-assisted inference for wide-angle or high-altitude feeds.
4. Bounding boxes, exact coordinates, severity, timestamps, and track IDs in JSON/CSV.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "ai" / "outputs" / "inference"

DEFAULT_SEVERITY_RULES = {
    "debris": "High",
    "wildlife_birds": "High",
    "bird": "High",
    "birds": "High",
    "wildlife": "High",
    "fuel_spill": "High",
    "fuel": "High",
    "spill": "High",
    "vehicles": "Medium",
    "vehicle": "Medium",
    "cracks": "Medium",
    "crack": "Medium",
    "luggage": "High",
    "personnel": "High",
    "person": "High",
    "aircraft": "High",
    "standing_water": "Medium",
    "potholes": "Medium",
    "tool_equipment": "Medium",
    "cone_or_barrier": "Medium",
    "runway": "Low",
}

SEVERITY_COLORS = {
    "High": (0, 0, 255),
    "Medium": (0, 165, 255),
    "Low": (0, 200, 0),
}


@dataclass
class TrackMemory:
    next_track_id: int = 1
    previous_tracks: list[dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        if self.previous_tracks is None:
            self.previous_tracks = []


def find_default_model() -> str:
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
        description="Detect runway hazards and export JSON/CSV logs."
    )
    parser.add_argument("--source", required=True, help="Path to an image or video.")
    parser.add_argument(
        "--model",
        default=find_default_model(),
        help="Path to YOLO weights (.pt) or a built-in Ultralytics model name.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where annotated media and detection logs will be saved.",
    )
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold.")
    parser.add_argument("--iou", type=float, default=0.45, help="IoU threshold for NMS.")
    parser.add_argument("--device", default="0", help="CUDA device id or cpu.")
    parser.add_argument("--line-thickness", type=int, default=2, help="Bounding-box line thickness.")
    parser.add_argument("--tracker", default="bytetrack.yaml", help="Ultralytics tracker config file.")
    parser.add_argument("--display", action="store_true", help="Display annotated frames while processing.")
    parser.add_argument(
        "--tile-size",
        type=int,
        default=0,
        help="Enable slicing-assisted inference when > 0. Recommended 640 or 960 for large wide-angle frames.",
    )
    parser.add_argument(
        "--tile-overlap",
        type=float,
        default=0.2,
        help="Tile overlap fraction used when --tile-size > 0.",
    )
    return parser.parse_args()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def resolve_class_name(names: Any, class_id: int) -> str:
    if isinstance(names, dict):
        return str(names.get(class_id, f"class_{class_id}"))
    if isinstance(names, list) and 0 <= class_id < len(names):
        return str(names[class_id])
    return f"class_{class_id}"


def severity_for_class(class_name: str) -> str:
    return DEFAULT_SEVERITY_RULES.get(class_name.strip().lower(), "Low")


def preprocess_frame_clahe(frame: np.ndarray) -> np.ndarray:
    if frame is None or frame.size == 0:
        return frame
    if len(frame.shape) == 2:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(frame)

    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_l = clahe.apply(l_channel)
    enhanced_lab = cv2.merge((enhanced_l, a_channel, b_channel))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)


def draw_detection(
    frame: Any,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    class_name: str,
    confidence: float,
    severity: str,
    track_id: int | None,
    thickness: int,
) -> None:
    color = SEVERITY_COLORS.get(severity, (255, 255, 255))
    track_text = f"ID {track_id} | " if track_id is not None else ""
    label = f"{track_text}{class_name} | {severity} | {confidence:.2f}"
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
    text_size, baseline = cv2.getTextSize(
        label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, max(thickness - 1, 1)
    )
    label_top = max(y1 - text_size[1] - baseline - 6, 0)
    label_bottom = label_top + text_size[1] + baseline + 6
    cv2.rectangle(frame, (x1, label_top), (x1 + text_size[0] + 8, label_bottom), color, -1)
    cv2.putText(
        frame,
        label,
        (x1 + 4, label_bottom - baseline - 3),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        max(thickness - 1, 1),
        cv2.LINE_AA,
    )


def build_record(
    detection_id: int,
    source_file: str,
    frame_index: int,
    frame_timestamp_seconds: float | None,
    class_name: str,
    confidence: float,
    severity: str,
    track_id: int | None,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
) -> dict[str, Any]:
    width = max(x2 - x1, 0)
    height = max(y2 - y1, 0)
    return {
        "detection_id": detection_id,
        "source_file": source_file,
        "frame_index": frame_index,
        "frame_timestamp_seconds": frame_timestamp_seconds,
        "detected_at_utc": utc_now_iso(),
        "class_name": class_name,
        "confidence": round(confidence, 6),
        "hazard_severity": severity,
        "track_id": track_id,
        "bbox_xywh": {"x": x1, "y": y1, "w": width, "h": height},
        "bbox_xyxy": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
    }


def save_json(output_path: Path, payload: dict[str, Any]) -> None:
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def save_csv(output_path: Path, detections: list[dict[str, Any]]) -> None:
    fieldnames = [
        "detection_id",
        "source_file",
        "frame_index",
        "frame_timestamp_seconds",
        "detected_at_utc",
        "class_name",
        "confidence",
        "hazard_severity",
        "track_id",
        "bbox_x",
        "bbox_y",
        "bbox_w",
        "bbox_h",
        "bbox_x1",
        "bbox_y1",
        "bbox_x2",
        "bbox_y2",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in detections:
            writer.writerow(
                {
                    "detection_id": record["detection_id"],
                    "source_file": record["source_file"],
                    "frame_index": record["frame_index"],
                    "frame_timestamp_seconds": record["frame_timestamp_seconds"],
                    "detected_at_utc": record["detected_at_utc"],
                    "class_name": record["class_name"],
                    "confidence": record["confidence"],
                    "hazard_severity": record["hazard_severity"],
                    "track_id": record["track_id"],
                    "bbox_x": record["bbox_xywh"]["x"],
                    "bbox_y": record["bbox_xywh"]["y"],
                    "bbox_w": record["bbox_xywh"]["w"],
                    "bbox_h": record["bbox_xywh"]["h"],
                    "bbox_x1": record["bbox_xyxy"]["x1"],
                    "bbox_y1": record["bbox_xyxy"]["y1"],
                    "bbox_x2": record["bbox_xyxy"]["x2"],
                    "bbox_y2": record["bbox_xyxy"]["y2"],
                }
            )


def box_iou(a: list[int], b: list[int]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_w = max(inter_x2 - inter_x1, 0)
    inter_h = max(inter_y2 - inter_y1, 0)
    inter_area = inter_w * inter_h
    area_a = max(ax2 - ax1, 0) * max(ay2 - ay1, 0)
    area_b = max(bx2 - bx1, 0) * max(by2 - by1, 0)
    union = area_a + area_b - inter_area
    return inter_area / union if union > 0 else 0.0


def merge_tile_detections(raw_detections: list[dict[str, Any]], iou_threshold: float) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for candidate in sorted(raw_detections, key=lambda item: item["confidence"], reverse=True):
        keep = True
        for existing in merged:
            if candidate["class_id"] != existing["class_id"]:
                continue
            if box_iou(candidate["bbox"], existing["bbox"]) >= iou_threshold:
                keep = False
                break
        if keep:
            merged.append(candidate)
    return merged


def assign_lightweight_track_ids(
    detections: list[dict[str, Any]],
    memory: TrackMemory,
    iou_threshold: float = 0.35,
) -> list[dict[str, Any]]:
    previous_tracks = memory.previous_tracks or []
    remaining_previous = previous_tracks.copy()
    for detection in detections:
        best_match = None
        best_iou = 0.0
        for previous in remaining_previous:
            if detection["class_id"] != previous["class_id"]:
                continue
            overlap = box_iou(detection["bbox"], previous["bbox"])
            if overlap > best_iou:
                best_iou = overlap
                best_match = previous
        if best_match is not None and best_iou >= iou_threshold:
            detection["track_id"] = best_match["track_id"]
            remaining_previous.remove(best_match)
        else:
            detection["track_id"] = memory.next_track_id
            memory.next_track_id += 1

    memory.previous_tracks = [
        {"track_id": detection["track_id"], "class_id": detection["class_id"], "bbox": detection["bbox"]}
        for detection in detections
    ]
    return detections


def run_sliced_detection(
    model: YOLO,
    frame: np.ndarray,
    args: argparse.Namespace,
    memory: TrackMemory | None = None,
) -> list[dict[str, Any]]:
    tile_size = args.tile_size
    overlap = max(0.0, min(args.tile_overlap, 0.49))
    step = max(int(tile_size * (1.0 - overlap)), 1)
    height, width = frame.shape[:2]
    detections: list[dict[str, Any]] = []

    for y in range(0, max(height - tile_size, 0) + step, step):
        if y >= height:
            break
        y2 = min(y + tile_size, height)
        y1 = max(y2 - tile_size, 0)
        for x in range(0, max(width - tile_size, 0) + step, step):
            if x >= width:
                break
            x2 = min(x + tile_size, width)
            x1 = max(x2 - tile_size, 0)
            tile = frame[y1:y2, x1:x2]
            results = model.predict(
                source=tile,
                conf=args.conf,
                iou=args.iou,
                device=args.device,
                verbose=False,
            )
            result = results[0]
            for box in result.boxes:
                bx1, by1, bx2, by2 = [int(value) for value in box.xyxy[0].tolist()]
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": resolve_class_name(result.names, class_id),
                        "confidence": confidence,
                        "bbox": [bx1 + x1, by1 + y1, bx2 + x1, by2 + y1],
                    }
                )

    merged = merge_tile_detections(detections, iou_threshold=args.iou)
    if memory is not None:
        return assign_lightweight_track_ids(merged, memory)
    return merged


def process_result(
    result: Any,
    frame: Any,
    source_file: str,
    frame_index: int,
    frame_timestamp_seconds: float | None,
    start_detection_id: int,
    line_thickness: int,
) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    detection_id = start_detection_id
    for box in result.boxes:
        x1, y1, x2, y2 = [int(value) for value in box.xyxy[0].tolist()]
        class_id = int(box.cls[0].item())
        confidence = float(box.conf[0].item())
        track_id = None
        if getattr(box, "id", None) is not None:
            track_id = int(box.id[0].item())
        class_name = resolve_class_name(result.names, class_id)
        severity = severity_for_class(class_name)
        draw_detection(frame, x1, y1, x2, y2, class_name, confidence, severity, track_id, line_thickness)
        records.append(
            build_record(
                detection_id=detection_id,
                source_file=source_file,
                frame_index=frame_index,
                frame_timestamp_seconds=frame_timestamp_seconds,
                class_name=class_name,
                confidence=confidence,
                severity=severity,
                track_id=track_id,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
            )
        )
        detection_id += 1
    return records, detection_id


def process_sliced_detections(
    detections: list[dict[str, Any]],
    frame: Any,
    source_file: str,
    frame_index: int,
    frame_timestamp_seconds: float | None,
    start_detection_id: int,
    line_thickness: int,
) -> tuple[list[dict[str, Any]], int]:
    records: list[dict[str, Any]] = []
    detection_id = start_detection_id
    for detection in detections:
        x1, y1, x2, y2 = detection["bbox"]
        class_name = detection["class_name"]
        confidence = detection["confidence"]
        track_id = detection.get("track_id")
        severity = severity_for_class(class_name)
        draw_detection(frame, x1, y1, x2, y2, class_name, confidence, severity, track_id, line_thickness)
        records.append(
            build_record(
                detection_id=detection_id,
                source_file=source_file,
                frame_index=frame_index,
                frame_timestamp_seconds=frame_timestamp_seconds,
                class_name=class_name,
                confidence=confidence,
                severity=severity,
                track_id=track_id,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
            )
        )
        detection_id += 1
    return records, detection_id


def process_image(model: YOLO, source_path: Path, run_dir: Path, args: argparse.Namespace) -> tuple[list[dict[str, Any]], Path]:
    original_image = cv2.imread(str(source_path))
    if original_image is None:
        raise ValueError(f"Unable to read image: {source_path}")

    preprocessed_image = preprocess_frame_clahe(original_image)
    if args.tile_size > 0:
        sliced = run_sliced_detection(model, preprocessed_image, args, memory=TrackMemory())
        detections, _ = process_sliced_detections(
            sliced,
            frame=original_image,
            source_file=str(source_path.resolve()),
            frame_index=0,
            frame_timestamp_seconds=None,
            start_detection_id=1,
            line_thickness=args.line_thickness,
        )
        inference_mode = "sliced"
    else:
        results = model.track(
            source=preprocessed_image,
            conf=args.conf,
            iou=args.iou,
            device=args.device,
            persist=True,
            tracker=args.tracker,
            verbose=False,
        )
        detections, _ = process_result(
            result=results[0],
            frame=original_image,
            source_file=str(source_path.resolve()),
            frame_index=0,
            frame_timestamp_seconds=None,
            start_detection_id=1,
            line_thickness=args.line_thickness,
        )
        inference_mode = "full_frame_tracking"

    annotated_path = run_dir / f"{source_path.stem}_annotated{source_path.suffix}"
    cv2.imwrite(str(annotated_path), original_image)
    if args.display:
        cv2.imshow("Hazard Detection", original_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return detections, annotated_path, inference_mode


def process_video(model: YOLO, source_path: Path, run_dir: Path, args: argparse.Namespace) -> tuple[list[dict[str, Any]], Path, str]:
    capture = cv2.VideoCapture(str(source_path))
    if not capture.isOpened():
        raise ValueError(f"Unable to open video: {source_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    annotated_path = run_dir / f"{source_path.stem}_annotated.mp4"
    writer = cv2.VideoWriter(
        str(annotated_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    detections: list[dict[str, Any]] = []
    next_detection_id = 1
    frame_index = 0
    sliced_memory = TrackMemory()
    inference_mode = "sliced" if args.tile_size > 0 else "full_frame_tracking"

    try:
        while True:
            success, frame = capture.read()
            if not success:
                break

            frame_timestamp_seconds = round(capture.get(cv2.CAP_PROP_POS_MSEC) / 1000.0, 3)
            preprocessed_frame = preprocess_frame_clahe(frame)

            if args.tile_size > 0:
                sliced = run_sliced_detection(model, preprocessed_frame, args, memory=sliced_memory)
                frame_records, next_detection_id = process_sliced_detections(
                    sliced,
                    frame=frame,
                    source_file=str(source_path.resolve()),
                    frame_index=frame_index,
                    frame_timestamp_seconds=frame_timestamp_seconds,
                    start_detection_id=next_detection_id,
                    line_thickness=args.line_thickness,
                )
            else:
                results = model.track(
                    source=preprocessed_frame,
                    conf=args.conf,
                    iou=args.iou,
                    device=args.device,
                    persist=True,
                    tracker=args.tracker,
                    verbose=False,
                )
                frame_records, next_detection_id = process_result(
                    result=results[0],
                    frame=frame,
                    source_file=str(source_path.resolve()),
                    frame_index=frame_index,
                    frame_timestamp_seconds=frame_timestamp_seconds,
                    start_detection_id=next_detection_id,
                    line_thickness=args.line_thickness,
                )

            detections.extend(frame_records)
            writer.write(frame)
            if args.display:
                cv2.imshow("Hazard Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            frame_index += 1
    finally:
        capture.release()
        writer.release()
        if args.display:
            cv2.destroyAllWindows()

    return detections, annotated_path, inference_mode


def main() -> None:
    args = parse_args()
    source_path = Path(args.source).resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Source file was not found: {source_path}")

    run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(args.output_dir).resolve() / f"{source_path.stem}_{run_stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    model = YOLO(args.model)
    image_suffixes = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
    if source_path.suffix.lower() in image_suffixes:
        detections, annotated_media_path, inference_mode = process_image(model, source_path, run_dir, args)
    else:
        detections, annotated_media_path, inference_mode = process_video(model, source_path, run_dir, args)

    json_path = run_dir / "detections.json"
    csv_path = run_dir / "detections.csv"
    payload = {
        "source_file": str(source_path),
        "model": str(args.model),
        "tracker": args.tracker,
        "preprocessing": "CLAHE",
        "inference_mode": inference_mode,
        "tile_size": args.tile_size,
        "tile_overlap": args.tile_overlap,
        "generated_at_utc": utc_now_iso(),
        "total_detections": len(detections),
        "annotated_media_path": str(annotated_media_path),
        "detections": detections,
    }
    save_json(json_path, payload)
    save_csv(csv_path, detections)

    summary = {
        "run_directory": str(run_dir),
        "annotated_media_path": str(annotated_media_path),
        "json_path": str(json_path),
        "csv_path": str(csv_path),
        "total_detections": len(detections),
        "inference_mode": inference_mode,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
