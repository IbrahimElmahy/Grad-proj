# RVMS Backend API Documentation

## Base URLs

- Local HTTP base: `http://127.0.0.1:8000`
- Local WebSocket base: `ws://127.0.0.1:8000`

## WebSocket Live Alerts

- URL: `ws://127.0.0.1:8000/ws/alerts/`
- Consumer group: `runway_alerts`
- Purpose: stream high-severity runway alerts to the frontend dashboard in near real time

### Connection Lifecycle

On successful connection, the backend sends:

```json
{
  "type": "connection.established",
  "group": "runway_alerts",
  "message": "Subscribed to runway hazard alerts."
}
```

The client may optionally send:

```json
{
  "type": "ping"
}
```

The server replies with:

```json
{
  "type": "pong"
}
```

### Hazard Alert Payload

Critical runway events are broadcast as:

```json
{
  "type": "hazard.alert",
  "inspection_id": "2a0b15b5-9cc7-42fd-94c7-8fe40b0f4871",
  "camera_id": "CAM-07",
  "inspection_status": "ALERT",
  "inspection_risk_level": "HIGH",
  "timestamp": "2026-04-09T16:30:12.812345+00:00",
  "critical_detection_count": 2,
  "detections": [
    {
      "inspection_image_id": "84b22073-b7c8-49ab-b61b-f64a34b7cb4d",
      "image_path": "inspections/raw/2026/04/09/frame_000123.jpg",
      "processed_image_path": "inspections/processed/2026/04/09/inspection_123_frame_000123.jpg",
      "raw_label": "Fuel_Spill",
      "object_type": "FUEL_SPILL",
      "hazard_severity": "HIGH",
      "confidence": 0.947321,
      "detected_at_utc": "2026-04-09T16:30:12.701Z",
      "frame_index": 123,
      "frame_timestamp_seconds": 4.92,
      "bbox_xywh": {
        "x": 418,
        "y": 251,
        "w": 162,
        "h": 84
      },
      "bbox_xyxy": {
        "x1": 418,
        "y1": 251,
        "x2": 580,
        "y2": 335
      },
      "gemini_suggestion": "Immediate action required: stop runway traffic, isolate the spill zone, and dispatch hazmat and firefighting support."
    }
  ]
}
```

### Frontend Notes

- Treat `inspection_risk_level` as the overall alert severity for the card/banner state.
- Treat `detections` as the per-object list to render rows, chips, or overlays.
- The current backend persists severity, timestamps, and bounding boxes. `track_id` is available in the inference layer but is not yet exposed in the persisted REST/WebSocket payloads.

## REST Endpoints

### 1. Upload New Inspection

- Method: `POST`
- URL: `/api/upload/`
- Content type: `multipart/form-data`

#### Form Fields

- `camera_id`: string, optional, defaults to `"Unknown Camera"`
- `image`: file, optional when `video` is provided
- `video`: file, optional when `image` is provided

At least one of `image` or `video` is required.

#### Example cURL

```bash
curl -X POST "http://127.0.0.1:8000/api/upload/" \
  -F "camera_id=CAM-07" \
  -F "image=@sample_runway.jpg"
```

#### Response Shape

```json
{
  "id": "2a0b15b5-9cc7-42fd-94c7-8fe40b0f4871",
  "camera_id": "CAM-07",
  "timestamp": "2026-04-09 16:30:12",
  "status": "ALERT",
  "risk_level": "HIGH",
  "analysis_log": {
    "generated_at_utc": "2026-04-09T16:30:12.821Z",
    "source_type": "image",
    "source_name": "sample_runway.jpg",
    "total_detections": 2,
    "highest_severity": "HIGH",
    "counts_by_severity": {
      "HIGH": 2
    },
    "counts_by_class": {
      "Fuel_Spill": 1,
      "Personnel": 1
    },
    "detector_error": null,
    "detections": []
  },
  "video": null,
  "images": [
    {
      "id": "84b22073-b7c8-49ab-b61b-f64a34b7cb4d",
      "image": "/media/inspections/raw/2026/04/09/sample_runway.jpg",
      "processed_image": "/media/inspections/processed/2026/04/09/inspection_123_sample_runway.jpg",
      "created_at": "2026-04-09T16:30:12.700000Z",
      "detected_objects": [
        {
          "id": "fcfb8fca-90cc-4d0a-a8f1-95d9ac814f30",
          "raw_label": "Fuel_Spill",
          "object_type": "FUEL_SPILL",
          "confidence": 0.947321,
          "severity": "HIGH",
          "detected_at": "2026-04-09T16:30:12.701000Z",
          "frame_index": 0,
          "frame_timestamp_seconds": null,
          "bbox_x": 418,
          "bbox_y": 251,
          "bbox_w": 162,
          "bbox_h": 84,
          "bbox_x1": 418,
          "bbox_y1": 251,
          "bbox_x2": 580,
          "bbox_y2": 335,
          "bbox_xywh": {
            "x": 418,
            "y": 251,
            "w": 162,
            "h": 84
          },
          "bbox_xyxy": {
            "x1": 418,
            "y1": 251,
            "x2": 580,
            "y2": 335
          },
          "bbox_data": {
            "x": 418,
            "y": 251,
            "w": 162,
            "h": 84,
            "x1": 418,
            "y1": 251,
            "x2": 580,
            "y2": 335
          },
          "gemini_suggestion": "Immediate action required: stop runway traffic, isolate the spill zone, and dispatch hazmat and firefighting support."
        }
      ]
    }
  ]
}
```

### 2. List Historical Inspections

- Method: `GET`
- URL: `/api/inspections/`
- Purpose: fetch the historical inspection feed for dashboards, timelines, and reports

#### Response

- Returns an array of `InspectionSerializer` objects
- Ordered newest first

### 3. Inspection Detail

- Method: `GET`
- URL: `/api/inspections/{inspection_id}/`
- Purpose: fetch the full detail of one inspection, including processed images and all detected objects

### 4. OpenAPI Schema

- Method: `GET`
- URL: `/api/schema/`

### 5. Swagger UI

- Method: `GET`
- URL: `/api/docs/`

## Key Enums

### Inspection Status

- `PROCESSING`
- `COMPLETED`
- `ALERT`

### Risk Levels

- `SAFE`
- `LOW`
- `MEDIUM`
- `HIGH`

### Common Object Types

- `DEBRIS`
- `WILDLIFE_BIRDS`
- `VEHICLE`
- `CRACK`
- `POTHOLE`
- `LUGGAGE`
- `PERSONNEL`
- `AIRCRAFT`
- `FUEL_SPILL`
- `STANDING_WATER`
- `TOOL_EQUIPMENT`
- `CONE_OR_BARRIER`

## Frontend Integration Checklist

- Connect once to `ws://127.0.0.1:8000/ws/alerts/`
- Show every incoming `hazard.alert` as a live card or toast
- Use `/api/inspections/` for historical feed and pagination on the dashboard
- Use `/api/inspections/{id}/` for the alert detail drawer or modal
- Use `bbox_xyxy` for image overlays and `bbox_xywh` for tabular display
