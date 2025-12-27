import os
from ultralytics import YOLO
from django.conf import settings

class YoloDetector:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            model_path = os.path.join(settings.BASE_DIR, 'ai_engine', 'models', 'best.pt')
            print(f"Loading YOLO model from: {model_path}")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"YOLO model not found at {model_path}")
            cls._model = YOLO(model_path)
        return cls._model

    def detect(self, image_path):
        """
        Runs YOLOv8 detection on the image.
        Returns a list of dictionaries with:
        {
            'label': str,
            'confidence': float,
            'bbox': {'x': float, 'y': float, 'w': float, 'h': float} 
        }
        """
        model = self.get_model()
        
        # Run inference
        results = model(image_path)
        
        detections = []
        for r in results:
            for box in r.boxes:
                # Extract class and confidence
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Use user's custom class names to match their original script
                # Original script: ['Runway', 'vehicle', 'birds', 'undefined', 'aircraft']
                custom_names = ['Runway', 'vehicle', 'birds', 'undefined', 'aircraft']
                
                if 0 <= cls_id < len(custom_names):
                    label = custom_names[cls_id]
                else:
                    label = model.names[cls_id] # Fallback
                    
                # Extract normalized bounding box (x_center, y_center, width, height)
                # YOLOv8 box.xywhn gives normalized xywh
                x, y, w, h = box.xywhn[0].tolist()
                
                detections.append({
                    'label': label,
                    'confidence': conf,
                    'bbox': {
                        'x': x,
                        'y': y,
                        'w': w,
                        'h': h
                    }
                })
        
        return detections

    def detect_video(self, video_path, output_dir_base):
        """
        Runs YOLOv8 detection on a video file.
        Extracts frames with detections and saves them.
        Returns a list of dictionaries with:
        {
            'frame_path': str,
            'timestamp': float,
            'detections': [list of detections in this frame]
        }
        """
        import cv2
        import time
        import os
        
        model = self.get_model()
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error opening video: {video_path}")
            return []
            
        frame_results = []
        frame_count = 0
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        
        # Process every Nth frame to speed up (e.g., every 0.5 seconds)
        # frame_skip = int(fps * 0.5) 
        # Actually for accuracy lets process every 10th frame for now or just sequential if fast enough.
        # Let's do every 5th frame for balance.
        frame_skip = 5
        
        while True:
            success, img = cap.read()
            if not success:
                break
                
            frame_count += 1
            if frame_count % frame_skip != 0:
                continue
                
            # Run inference
            results = model(img, verbose=False)
            
            frame_detections = []
            has_relevant_detection = False
            
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    label = model.names[cls_id]
                    
                    # Filter low confidence
                    if conf < 0.4:
                        continue
                        
                    frame_detections.append({
                        'label': label,
                        'confidence': conf,
                        'bbox': box.xywhn[0].tolist()
                    })
                    
                    # If we found something interesting, we want to save this frame
                    # Filter out 'Runway' if that's the only thing, maybe? 
                    # User wants to see hazards.
                    if label.lower() != 'runway': 
                         has_relevant_detection = True
            
            if has_relevant_detection:
                # Save Frame
                timestamp = frame_count / fps
                filename = f"frame_{int(time.time())}_{frame_count}.jpg"
                
                # We need a place to save. api_views will provide a base dir.
                # Usually media/inspections/processed/...
                # But here we just return the image data or save to a temp path?
                # Better to save directly to the output path provided.
                
                if not os.path.exists(output_dir_base):
                    os.makedirs(output_dir_base)
                    
                save_path = os.path.join(output_dir_base, filename)
                
                # Draw boxes for the user to see clearly
                # Using the existing results object to plot is easiest
                plotted_img = results[0].plot()
                cv2.imwrite(save_path, plotted_img)
                
                frame_results.append({
                    'frame_path': save_path,
                    'timestamp': timestamp,
                    'detections': frame_detections
                })
                
        cap.release()
        return frame_results
