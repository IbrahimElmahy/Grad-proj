from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import ObjectType, RiskLevel


def _critical_detections(detections: list[dict]) -> list[dict]:
    critical = []
    for detection in detections:
        severity = detection.get("hazard_severity")
        if severity == RiskLevel.HIGH:
            critical.append(detection)
    return critical


def broadcast_inspection_alert(inspection, detections: list[dict]) -> bool:
    critical_detections = _critical_detections(detections)
    if not critical_detections:
        return False

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return False

    payload = {
        "type": "hazard.alert",
        "inspection_id": str(inspection.id),
        "camera_id": inspection.camera_id,
        "inspection_status": inspection.status,
        "inspection_risk_level": inspection.risk_level,
        "timestamp": inspection.timestamp.isoformat(),
        "critical_detection_count": len(critical_detections),
        "detections": critical_detections,
    }

    async_to_sync(channel_layer.group_send)(
        "runway_alerts",
        {
            "type": "alert.message",
            "payload": payload,
        },
    )
    return True
