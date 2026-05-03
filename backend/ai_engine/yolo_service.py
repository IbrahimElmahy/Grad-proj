import os
from datetime import datetime, timezone

import cv2
from django.conf import settings
from ultralytics import YOLO


class YoloDetector:
    _model = None

    SEVERITY_RULES = {
        "debris": "High",
        "fod": "High",
        "wildlife_birds": "High",
        "bird": "High",
        "wildlife": "High",
        "fuel_spill": "High",
        "fuel": "High",
        "spill": "High",
        "luggage": "High",
        "personnel": "High",
        "person": "High",
        "vehicle": "Medium",
        "crack": "Medium",
        "pothole": "Medium",
        "standing_water": "Medium",
        "standing water": "Medium",
        "tool_equipment": "Medium",
        "tool": "Medium",
        "cone_or_barrier": "Medium",
        "cone": "Medium",
        "barrier": "Medium",
        "runway": "Low",
        "aircraft": "High",
    }

    SEVERITY_COLORS = {
        "High": (0, 0, 255),
        "Medium": (0, 165, 255),
        "Low": (0, 200, 0),
    }

    @classmethod
    def get_model(cls):
        if cls._model is None:
            candidates = [
                os.path.join(settings.BASE_DIR, "ai_engine", "models", "best_unified_12c.pt"),
                os.path.join(settings.BASE_DIR, "ai_engine", "models", "best_unified.pt"),
                os.path.join(settings.BASE_DIR, "ai_engine", "models", "best.pt"),
            ]
            model_path = next((path for path in candidates if os.path.exists(path)), None)
            if model_path is None:
                raise FileNotFoundError(
                    f"YOLO model not found. Checked: {', '.join(candidates)}"
                )
            print(f"Loading YOLO model from: {model_path}")
            cls._model = YOLO(model_path)
        return cls._model

    @staticmethod
    def _utc_now_iso():
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    @classmethod
    def _severity_for_label(cls, label):
        normalized = (label or "").strip().lower()
        for key, severity in cls.SEVERITY_RULES.items():
            if key in normalized:
                return severity
        return "Low"

    @staticmethod
    def _preprocess_frame_clahe(frame):
        if frame is None:
            return frame
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_l = clahe.apply(l_channel)
        enhanced_lab = cv2.merge((enhanced_l, a_channel, b_channel))
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    @classmethod
    def _draw_detection(cls, frame, x1, y1, x2, y2, label, confidence, severity, track_id=None):
        color = cls.SEVERITY_COLORS.get(severity, (255, 255, 255))
        track_text = f"ID {track_id} | " if track_id is not None else ""
        text = f"{track_text}{label} | {severity} | {confidence:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        text_size, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        label_top = max(y1 - text_size[1] - baseline - 6, 0)
        label_bottom = label_top + text_size[1] + baseline + 6
        cv2.rectangle(frame, (x1, label_top), (x1 + text_size[0] + 8, label_bottom), color, -1)
        cv2.putText(
            frame,
            text,
            (x1 + 4, label_bottom - baseline - 3),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    @staticmethod
    def _save_frame(output_path, frame):
        if not output_path:
            return
        folder = os.path.dirname(output_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        cv2.imwrite(output_path, frame)

    @staticmethod
    def _resolve_class_name(result, class_id):
        names = result.names
        if isinstance(names, dict):
            return str(names.get(class_id, f"class_{class_id}"))
        if isinstance(names, list) and 0 <= class_id < len(names):
            return str(names[class_id])
        return f"class_{class_id}"

    def _process_tracking_result(self, result, annotated_frame, frame_index=0, frame_timestamp_seconds=None):
        detections = []
        for box in result.boxes:
            x1, y1, x2, y2 = [int(value) for value in box.xyxy[0].tolist()]
            class_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())
            track_id = None
            if getattr(box, "id", None) is not None:
                track_id = int(box.id[0].item())

            label = self._resolve_class_name(result, class_id)
            severity = self._severity_for_label(label)
            width = max(x2 - x1, 0)
            height = max(y2 - y1, 0)

            self._draw_detection(
                frame=annotated_frame,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                label=label,
                confidence=confidence,
                severity=severity,
                track_id=track_id,
            )

            detections.append(
                {
                    "label": label,
                    "confidence": confidence,
                    "severity": severity,
                    "track_id": track_id,
                    "detected_at_utc": self._utc_now_iso(),
                    "frame_index": frame_index,
                    "frame_timestamp_seconds": frame_timestamp_seconds,
                    "preprocessing": "CLAHE",
                    "bbox": {
                        "x": x1,
                        "y": y1,
                        "w": width,
                        "h": height,
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    },
                }
            )
        return detections

    def detect(self, image_path, output_path=None):
        frame = cv2.imread(image_path)
        if frame is None:
            raise ValueError(f"Unable to read image: {image_path}")

        model = self.get_model()
        preprocessed_frame = self._preprocess_frame_clahe(frame)
        annotated_frame = frame.copy()
        results = model.track(
            source=preprocessed_frame,
            conf=0.25,
            iou=0.45,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False,
        )

        detections = self._process_tracking_result(
            results[0],
            annotated_frame=annotated_frame,
            frame_index=0,
            frame_timestamp_seconds=None,
        )
        self._save_frame(output_path, annotated_frame)
        return detections

    def detect_video(self, video_path, output_dir_base, frame_skip=5):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error opening video: {video_path}")
            return []

        model = self.get_model()
        frame_results = []
        frame_index = -1

        try:
            while True:
                success, frame = cap.read()
                if not success:
                    break

                frame_index += 1
                if frame_skip > 1 and frame_index % frame_skip != 0:
                    continue

                frame_timestamp_seconds = round(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0, 3)
                preprocessed_frame = self._preprocess_frame_clahe(frame)
                annotated_frame = frame.copy()
                results = model.track(
                    source=preprocessed_frame,
                    conf=0.25,
                    iou=0.45,
                    persist=True,
                    tracker="bytetrack.yaml",
                    verbose=False,
                )

                detections = self._process_tracking_result(
                    results[0],
                    annotated_frame=annotated_frame,
                    frame_index=frame_index,
                    frame_timestamp_seconds=frame_timestamp_seconds,
                )
                if not detections:
                    continue

                if not os.path.exists(output_dir_base):
                    os.makedirs(output_dir_base)

                filename = f"frame_{frame_index:06d}.jpg"
                save_path = os.path.join(output_dir_base, filename)
                self._save_frame(save_path, annotated_frame)
                frame_results.append(
                    {
                        "frame_path": save_path,
                        "frame_index": frame_index,
                        "frame_timestamp_seconds": frame_timestamp_seconds,
                        "detections": detections,
                    }
                )
        finally:
            cap.release()

        return frame_results
