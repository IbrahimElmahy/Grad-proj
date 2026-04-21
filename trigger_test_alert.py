from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import django
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


REPO_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = REPO_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rvms_backend.settings")
django.setup()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def main() -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        raise RuntimeError("Channel layer is not configured.")

    payload = {
        "type": "hazard.alert",
        "inspection_id": "test-aircraft-incursion-001",
        "camera_id": "SIM-CAM-ALPHA",
        "inspection_status": "ALERT",
        "inspection_risk_level": "HIGH",
        "timestamp": utc_now_iso(),
        "critical_detection_count": 1,
        "detections": [
            {
                "inspection_image_id": None,
                "image_path": None,
                "processed_image_path": None,
                "raw_label": "Aircraft",
                "object_type": "AIRCRAFT",
                "hazard_severity": "HIGH",
                "confidence": 0.9932,
                "detected_at_utc": utc_now_iso(),
                "frame_index": 42,
                "frame_timestamp_seconds": 3.417,
                "track_id": 7,
                "bbox_xywh": {"x": 188, "y": 122, "w": 246, "h": 118},
                "bbox_xyxy": {"x1": 188, "y1": 122, "x2": 434, "y2": 240},
                "gemini_suggestion": "Immediate action required: stop runway operations and coordinate with tower to clear the aircraft incursion.",
            }
        ],
    }

    async_to_sync(channel_layer.group_send)(
        "runway_alerts",
        {
            "type": "alert.message",
            "payload": payload,
        },
    )

    print("Test alert sent to WebSocket group 'runway_alerts':")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
