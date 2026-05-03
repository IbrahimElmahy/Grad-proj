from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from .models import ObjectType, RiskLevel


SEVERITY_RANK = {
    RiskLevel.SAFE: 0,
    RiskLevel.LOW: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def classify_detection_label(label: str) -> tuple[str, str]:
    normalized = (label or "").strip().lower()

    if "debris" in normalized:
        return ObjectType.DEBRIS, RiskLevel.HIGH
    if normalized == "fod":
        return ObjectType.FOD, RiskLevel.HIGH
    if "bird" in normalized or "wildlife" in normalized:
        return ObjectType.WILDLIFE_BIRDS, RiskLevel.HIGH
    if "vehicle" in normalized:
        return ObjectType.VEHICLE, RiskLevel.MEDIUM
    if "crack" in normalized:
        return ObjectType.CRACK, RiskLevel.MEDIUM
    if "pothole" in normalized:
        return ObjectType.POTHOLE, RiskLevel.MEDIUM
    if "fuel" in normalized or "oil spill" in normalized or "spill" in normalized:
        return ObjectType.FUEL_SPILL, RiskLevel.HIGH
    if "standing_water" in normalized or "standing water" in normalized or "puddle" in normalized:
        return ObjectType.STANDING_WATER, RiskLevel.MEDIUM
    if "tool_equipment" in normalized or "tool" in normalized or "equipment" in normalized:
        return ObjectType.TOOL_EQUIPMENT, RiskLevel.MEDIUM
    if "cone_or_barrier" in normalized or "cone" in normalized or "barrier" in normalized:
        return ObjectType.CONE_OR_BARRIER, RiskLevel.MEDIUM
    if "luggage" in normalized or "bag" in normalized:
        return ObjectType.LUGGAGE, RiskLevel.HIGH
    if "personnel" in normalized:
        return ObjectType.PERSONNEL, RiskLevel.HIGH
    if "person" in normalized or "worker" in normalized:
        return ObjectType.PERSON, RiskLevel.HIGH
    if "aircraft" in normalized or "plane" in normalized:
        return ObjectType.AIRCRAFT, RiskLevel.SAFE
    if "runway" in normalized:
        return ObjectType.RUNWAY, RiskLevel.SAFE
    return ObjectType.OTHER, RiskLevel.LOW


def fallback_suggestion(object_type: str, severity: str) -> str:
    if severity == RiskLevel.HIGH:
        if object_type in {ObjectType.DEBRIS, ObjectType.FOD, ObjectType.LUGGAGE}:
            return "Immediate action required: dispatch ground crew to remove the object and isolate the affected runway section."
        if object_type in {ObjectType.WILDLIFE_BIRDS, ObjectType.BIRD}:
            return "Immediate action required: activate wildlife deterrence measures and notify runway operations."
        if object_type == ObjectType.FUEL_SPILL:
            return "Immediate action required: stop runway traffic, isolate the spill zone, and dispatch hazmat and firefighting support."
        if object_type in {ObjectType.PERSONNEL, ObjectType.PERSON}:
            return "Immediate action required: clear personnel from the runway and verify access control."
        return "Immediate action required: secure the area and alert airport operations."

    if severity == RiskLevel.MEDIUM:
        if object_type == ObjectType.VEHICLE:
            return "Warning: verify vehicle authorization and move it clear of the runway as soon as possible."
        if object_type in {ObjectType.CRACK, ObjectType.POTHOLE}:
            return "Schedule urgent maintenance inspection and restrict traffic if the surface defect expands."
        if object_type == ObjectType.STANDING_WATER:
            return "Warning: inspect drainage and runway friction immediately to reduce hydroplaning risk."
        if object_type == ObjectType.TOOL_EQUIPMENT:
            return "Warning: remove misplaced equipment promptly and confirm maintenance crews account for missing tools."
        if object_type == ObjectType.CONE_OR_BARRIER:
            return "Warning: verify the marker placement and clear it from active runway space if unauthorized."
        return "Warning: inspect the area promptly and dispatch maintenance if needed."

    if severity == RiskLevel.LOW:
        return "Monitor the situation and confirm whether maintenance follow-up is needed."

    return ""


def highest_risk_level(levels: list[str]) -> str:
    if not levels:
        return RiskLevel.SAFE
    return max(levels, key=lambda level: SEVERITY_RANK.get(level, 0))


def is_alert_level(level: str) -> bool:
    return level in {RiskLevel.HIGH, RiskLevel.MEDIUM}


def build_detection_log_entry(
    *,
    inspection_image: Any,
    raw_label: str,
    object_type: str,
    severity: str,
    confidence: float,
    detected_at_utc: str,
    frame_index: int,
    frame_timestamp_seconds: float | None,
    bbox: dict[str, Any],
    gemini_suggestion: str,
) -> dict[str, Any]:
    return {
        "inspection_image_id": str(inspection_image.id) if inspection_image else None,
        "image_path": inspection_image.image.name if inspection_image and inspection_image.image else None,
        "processed_image_path": (
            inspection_image.processed_image.name
            if inspection_image and inspection_image.processed_image
            else None
        ),
        "raw_label": raw_label,
        "object_type": object_type,
        "hazard_severity": severity,
        "confidence": round(float(confidence), 6),
        "detected_at_utc": detected_at_utc,
        "frame_index": frame_index,
        "frame_timestamp_seconds": frame_timestamp_seconds,
        "bbox_xywh": {
            "x": bbox.get("x"),
            "y": bbox.get("y"),
            "w": bbox.get("w"),
            "h": bbox.get("h"),
        },
        "bbox_xyxy": {
            "x1": bbox.get("x1"),
            "y1": bbox.get("y1"),
            "x2": bbox.get("x2"),
            "y2": bbox.get("y2"),
        },
        "gemini_suggestion": gemini_suggestion,
    }


def build_analysis_log(
    *,
    source_type: str,
    source_name: str | None,
    detections: list[dict[str, Any]],
    detector_error: str | None = None,
) -> dict[str, Any]:
    severity_counts = Counter(item["hazard_severity"] for item in detections)
    class_counts = Counter(item["raw_label"] for item in detections)
    highest_severity = highest_risk_level(list(severity_counts.elements()))

    return {
        "generated_at_utc": utc_now_iso(),
        "source_type": source_type,
        "source_name": source_name,
        "total_detections": len(detections),
        "highest_severity": highest_severity,
        "counts_by_severity": dict(severity_counts),
        "counts_by_class": dict(class_counts),
        "detector_error": detector_error,
        "detections": detections,
    }
