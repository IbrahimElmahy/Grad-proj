import os
from datetime import datetime, timezone

import cv2
from django.conf import settings
from ultralytics import YOLO


class YoloDetector:
    _model_4 = None
    _model_7 = None

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
    def get_models(cls):
        if cls._model_4 is None:
            path4 = os.path.join(settings.BASE_DIR, "ai_engine", "models", "best_4c.pt")
            if not os.path.exists(path4):
                path4 = os.path.join(settings.BASE_DIR, "ai_engine", "models", "best.pt")
            print(f"Loading YOLO 4-class model from: {path4}")
            cls._model_4 = YOLO(path4)

        if cls._model_7 is None:
            path7 = os.path.join(settings.BASE_DIR, "ai_engine", "models", "best_7c.pt")
            if not os.path.exists(path7):
                path7 = os.path.join(settings.BASE_DIR, "ai_engine", "models", "best.pt")
            print(f"Loading YOLO 7-class model from: {path7}")
            cls._model_7 = YOLO(path7)

        return cls._model_4, cls._model_7

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

    def _process_tracking_result(self, result, allowed_classes=None, min_confidence_mapping=None, frame_index=0, frame_timestamp_seconds=None):
        detections = []
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())
            label = self._resolve_class_name(result, class_id)
            label_lower = label.lower()

            if allowed_classes is not None and label_lower not in allowed_classes:
                continue

            min_conf = 0.25
            if min_confidence_mapping is not None and label_lower in min_confidence_mapping:
                min_conf = min_confidence_mapping[label_lower]

            x1, y1, x2, y2 = [int(value) for value in box.xyxy[0].tolist()]
            track_id = None
            if getattr(box, "id", None) is not None:
                track_id = int(box.id[0].item())

            width = max(x2 - x1, 0)
            height = max(y2 - y1, 0)

            # Heuristic: If classified as bird/wildlife but highly vertical (aspect ratio > 1.8),
            # it is almost certainly a human (personnel). Reclassify it to avoid looking silly.
            if label_lower in ["wildlife_birds", "bird"] and width > 0 and (height / width) > 1.8:
                label = "Personnel"
                label_lower = "personnel"

            # Heuristic: If classified as aircraft but has narrow/square aspect ratio,
            # or is in foreground (lower half of image) but is small in width,
            # it is likely debris (FOD) or personnel. Reclassify it to avoid false aircraft alerts.
            if label_lower == "aircraft" and getattr(result, "orig_shape", None) is not None:
                orig_h, orig_w = result.orig_shape
                is_foreground = (y2 > 0.5 * orig_h)
                is_small_in_foreground = is_foreground and (width < 0.65 * orig_w)
                is_non_aircraft_aspect = (height > 0 and width / height < 1.3)
                
                if is_small_in_foreground or is_non_aircraft_aspect:
                    if height > 0 and (height / width) > 1.2:
                        label = "Personnel"
                        label_lower = "personnel"
                    else:
                        label = "Debris"
                        label_lower = "debris"

            severity = self._severity_for_label(label)

            detections.append(
                {
                    "label": label,
                    "confidence": confidence,
                    "severity": severity,
                    "track_id": track_id,
                    "passes_conf": confidence >= min_conf,
                    "detected_at_utc": self._utc_now_iso(),
                    "frame_index": frame_index,
                    "frame_timestamp_seconds": frame_timestamp_seconds,
                    "preprocessing": "None",
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

        model4, model7 = self.get_models()
        # Disable CLAHE preprocessing to avoid washing out textures of objects like luggage and aircraft
        preprocessed_frame = frame
        annotated_frame = frame.copy()

        # Run 4-class model for Runway, Aircraft, Vehicle, Bird
        results4 = model4.predict(
            source=preprocessed_frame,
            conf=0.08,
            iou=0.45,
            verbose=False,
        )
        detections4 = self._process_tracking_result(
            result=results4[0],
            allowed_classes={"runway", "aircraft", "bird", "vehicle", "debris", "personnel"},
            min_confidence_mapping={"bird": 0.40, "aircraft": 0.20, "debris": 0.10, "personnel": 0.10},
            frame_index=0,
            frame_timestamp_seconds=None,
        )

        # Run 7-class model for Debris, Wildlife_Birds, Cracks, Luggage, Personnel
        results7 = model7.predict(
            source=preprocessed_frame,
            conf=0.08,
            iou=0.45,
            verbose=False,
        )
        detections7 = self._process_tracking_result(
            result=results7[0],
            allowed_classes={"debris", "wildlife_birds", "cracks", "luggage", "personnel", "aircraft", "vehicles"},
            min_confidence_mapping={
                "personnel": 0.55,
                "luggage": 0.10,
                "debris": 0.10,
                "cracks": 0.22,
                "wildlife_birds": 0.15,
                "aircraft": 0.20,
                "vehicles": 0.25
            },
            frame_index=0,
            frame_timestamp_seconds=None,
        )

        detections = self._resolve_conflicts(detections4 + detections7)

        # Draw resolved detections on annotated_frame
        for d in detections:
            bbox = d["bbox"]
            self._draw_detection(
                frame=annotated_frame,
                x1=bbox["x1"],
                y1=bbox["y1"],
                x2=bbox["x2"],
                y2=bbox["y2"],
                label=d["label"],
                confidence=d["confidence"],
                severity=d["severity"],
                track_id=d.get("track_id"),
            )

        self._save_frame(output_path, annotated_frame)
        return detections

    def detect_video(self, video_path, output_dir_base, output_video_path=None, frame_skip=5):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error opening video: {video_path}")
            return [], None

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

        writer = None
        if output_video_path:
            folder = os.path.dirname(output_video_path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder)
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            writer = cv2.VideoWriter(output_video_path, fourcc, fps, (w, h))

        model4, model7 = self.get_models()
        
        # Reset trackers for both models before processing a new video
        for model in [model4, model7]:
            if getattr(model, "predictor", None) is not None and hasattr(model.predictor, "trackers"):
                for tracker in model.predictor.trackers:
                    tracker.reset()

        frame_results = []
        frame_index = -1
        last_detections = []

        try:
            while True:
                success, frame = cap.read()
                if not success:
                    break

                frame_index += 1
                frame_timestamp_seconds = round(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0, 3)

                should_skip_yolo = (frame_skip > 1 and frame_index % frame_skip != 0)

                if should_skip_yolo:
                    if writer is not None:
                        # Draw last detections so bounding boxes remain visible and smooth
                        annotated_frame = frame.copy()
                        for d in last_detections:
                            bbox = d["bbox"]
                            self._draw_detection(
                                frame=annotated_frame,
                                x1=bbox["x1"],
                                y1=bbox["y1"],
                                x2=bbox["x2"],
                                y2=bbox["y2"],
                                label=d["label"],
                                confidence=d["confidence"],
                                severity=d["severity"],
                                track_id=d.get("track_id"),
                            )
                        writer.write(annotated_frame)
                    continue

                # Disable CLAHE preprocessing to avoid washing out textures of objects like luggage and aircraft
                preprocessed_frame = frame
                annotated_frame = frame.copy()

                # Run 4-class model
                results4 = model4.track(
                    source=preprocessed_frame,
                    conf=0.08,
                    iou=0.45,
                    persist=True,
                    tracker="bytetrack.yaml",
                    verbose=False,
                )
                detections4 = self._process_tracking_result(
                    result=results4[0],
                    allowed_classes={"runway", "aircraft", "bird", "vehicle", "debris", "personnel"},
                    min_confidence_mapping={"bird": 0.40, "aircraft": 0.20, "debris": 0.10, "personnel": 0.10},
                    frame_index=frame_index,
                    frame_timestamp_seconds=frame_timestamp_seconds,
                )

                # Run 7-class model
                results7 = model7.track(
                    source=preprocessed_frame,
                    conf=0.08,
                    iou=0.45,
                    persist=True,
                    tracker="bytetrack.yaml",
                    verbose=False,
                )
                detections7 = self._process_tracking_result(
                    result=results7[0],
                    allowed_classes={"debris", "wildlife_birds", "cracks", "luggage", "personnel", "aircraft", "vehicles"},
                    min_confidence_mapping={
                        "personnel": 0.55,
                        "luggage": 0.10,
                        "debris": 0.10,
                        "cracks": 0.22,
                        "wildlife_birds": 0.15,
                        "aircraft": 0.20,
                        "vehicles": 0.25
                    },
                    frame_index=frame_index,
                    frame_timestamp_seconds=frame_timestamp_seconds,
                )

                detections = self._resolve_conflicts(detections4 + detections7)
                last_detections = detections

                # Draw final resolved detections
                for d in detections:
                    bbox = d["bbox"]
                    self._draw_detection(
                        frame=annotated_frame,
                        x1=bbox["x1"],
                        y1=bbox["y1"],
                        x2=bbox["x2"],
                        y2=bbox["y2"],
                        label=d["label"],
                        confidence=d["confidence"],
                        severity=d["severity"],
                        track_id=d.get("track_id"),
                    )

                if writer is not None:
                    writer.write(annotated_frame)

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
            if writer is not None:
                writer.release()

        return frame_results, output_video_path

    @staticmethod
    def _box_iou(box1, box2):
        xA = max(box1[0], box2[0])
        yA = max(box1[1], box2[1])
        xB = min(box1[2], box2[2])
        yB = min(box1[3], box2[3])
        
        interArea = max(0, xB - xA) * max(0, yB - yA)
        if interArea == 0:
            return 0.0
            
        box1Area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2Area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        unionArea = box1Area + box2Area - interArea
        if unionArea == 0:
            return 0.0
        return interArea / unionArea

    @staticmethod
    def _box_overlap_ratio(box1, box2):
        xA = max(box1[0], box2[0])
        yA = max(box1[1], box2[1])
        xB = min(box1[2], box2[2])
        yB = min(box1[3], box2[3])
        
        interArea = max(0, xB - xA) * max(0, yB - yA)
        if interArea == 0:
            return 0.0
            
        box1Area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        if box1Area == 0:
            return 0.0
        return interArea / box1Area

    @classmethod
    def _resolve_conflicts(cls, detections):
        # 1. First, suppress birds/wildlife_birds that overlap with any non-bird detections (both passing and failing conf)
        birds_resolved = []
        birds = [d for d in detections if d["label"].lower() in ["bird", "wildlife_birds"]]
        non_birds = [d for d in detections if d["label"].lower() not in ["bird", "wildlife_birds"]]
        
        for b in birds:
            overlap = False
            box_b = [b["bbox"]["x1"], b["bbox"]["y1"], b["bbox"]["x2"], b["bbox"]["y2"]]
            for o in non_birds:
                box_o = [o["bbox"]["x1"], o["bbox"]["y1"], o["bbox"]["x2"], o["bbox"]["y2"]]
                iou = cls._box_iou(box_b, box_o)
                overlap_ratio = cls._box_overlap_ratio(box_b, box_o)
                if iou > 0.20 or overlap_ratio > 0.20:
                    overlap = True
                    break
            if not overlap:
                birds_resolved.append(b)
                
        # 2. Second, resolve conflicts between aircraft and luggage (both passing and failing conf)
        # If an aircraft box overlaps significantly with a luggage box, suppress the aircraft (since Model 4 often confuses luggage for aircraft)
        final_non_birds = []
        aircrafts = [d for d in non_birds if d["label"].lower() == "aircraft"]
        non_aircrafts = [d for d in non_birds if d["label"].lower() != "aircraft"]
        
        for a in aircrafts:
            overlap_with_luggage = False
            box_a = [a["bbox"]["x1"], a["bbox"]["y1"], a["bbox"]["x2"], a["bbox"]["y2"]]
            for o in non_aircrafts:
                if o["label"].lower() == "luggage":
                    box_o = [o["bbox"]["x1"], o["bbox"]["y1"], o["bbox"]["x2"], o["bbox"]["y2"]]
                    iou = cls._box_iou(box_a, box_o)
                    overlap_ratio = cls._box_overlap_ratio(box_o, box_a)
                    if iou > 0.20 or overlap_ratio > 0.50:
                        overlap_with_luggage = True
                        break
            if not overlap_with_luggage:
                final_non_birds.append(a)
                
        final_non_birds.extend(non_aircrafts)
        
        # Merge and only keep detections that pass confidence mapping
        all_resolved = birds_resolved + final_non_birds
        final_passed = [d for d in all_resolved if d.get("passes_conf", True)]

        # Dynamic aircraft severity based on count in this frame/image
        aircraft_detections = [d for d in final_passed if d["label"].lower() == "aircraft"]
        if len(aircraft_detections) <= 1:
            for d in aircraft_detections:
                d["severity"] = "Low"

        return final_passed
