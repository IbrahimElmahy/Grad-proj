import cv2
from ultralytics import YOLO
import cvzone
import pandas as pd
import time
import os
import tkinter as tk
from tkinter import filedialog

# --- Project Description ---
# Project: Airport Runway Hazard Detection System
# Purpose: Detect objects (Aircraft, Vehicles, Birds, etc.) on the runway.
# Features: File Selection, Image/Video Support, Optimized Performance.
# ---------------------------

def process_frame(img, model, class_names, detection_data):
    """
    Process a single frame/image: Detect objects, draw boxes, and collect data.
    """
    # stream=True is efficient for videos, but works for images too if passed as list or single
    results = model(img)

    for r in results:
        for box in r.boxes:
            # Extract bounding box
            x1, y1, x2, y2 = int(box.xyxy[0][0]), int(box.xyxy[0][1]), int(box.xyxy[0][2]), int(box.xyxy[0][3])
            
            # Confidence and Class
            conf = float(box.conf[0])
            cls = int(box.cls[0])

            current_class = "Unknown"
            if 0 <= cls < len(class_names):
                current_class = class_names[cls]
            
            # Draw
            cvzone.cornerRect(img, (x1, y1, x2 - x1, y2 - y1), l=9, rt=1)
            cvzone.putTextRect(img, f'{current_class} {conf:.2f}', 
                               (max(0, x1), max(35, y1)), scale=1, thickness=1, offset=3)

            # Collect data
            detection_data.append({
                'Class': current_class,
                'Confidence': conf,
                'X1': x1,
                'Y1': y1,
                'X2': x2,
                'Y2': y2,
                'Timestamp': time.time()
            })
    return img

def main():
    # 1. Load Model
    # Use absolute path to the backend model
    model_path = r"f:\znu\fourth year\project\grad project\backend\ai_engine\models\best.pt"
    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found.")
        return
    
    print(f"Loading model: {model_path}...")
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Class names - UPDATED to match model metadata
    # {0: 'Runway', 1: 'aircraft', 2: 'bird', 3: 'vehicle'}
    class_names = ['Runway', 'aircraft', 'bird', 'vehicle']

    # 2. Select File via Dialog
    print("Opening file selection dialog...")
    root = tk.Tk()
    root.withdraw() # Hide the main window

    file_path = filedialog.askopenfilename(
        title="Select Video or Image for Detection",
        filetypes=[
            ("Media Files", "*.mp4 *.avi *.mov *.mkv *.jpg *.jpeg *.png *.bmp"),
            ("All Files", "*.*")
        ]
    )

    if not file_path:
        print("No file selected. Exiting.")
        return

    print(f"Selected file: {file_path}")

    # 3. Determine File Type
    ext = os.path.splitext(file_path)[1].lower()
    is_video = ext in ['.mp4', '.avi', '.mov', '.mkv']
    
    detection_data = [] 
    output_excel = "detections_result.xlsx"

    if is_video:
        # --- VIDEO PROCESSING ---
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print("Error: Could not open video source.")
            return

        prev_frame_time = 0
        new_frame_time = 0

        print("Starting video detection. Press 'q' to exit.")

        while True:
            new_frame_time = time.time()
            success, img = cap.read()

            if not success:
                print("Video finished.")
                break

            # Object Detection
            img = process_frame(img, model, class_names, detection_data)

            # FPS
            fps = 1 / (new_frame_time - prev_frame_time) if prev_frame_time != 0 else 0
            prev_frame_time = new_frame_time
            cv2.putText(img, f"FPS: {int(fps)}", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Show
            cv2.imshow("Runway Hazard Detection (Video)", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("User requested exit.")
                break
        
        cap.release()

    else:
        # --- IMAGE PROCESSING ---
        print("Processing image...")
        img = cv2.imread(file_path)
        if img is None:
            print("Error: Could not read image.")
            return

        img = process_frame(img, model, class_names, detection_data)
        
        cv2.imshow("Runway Hazard Detection (Image)", img)
        print("Press any key to close the image window...")
        cv2.waitKey(0) # Wait indefinitely for a key

    cv2.destroyAllWindows()

    # 4. Save Data
    if detection_data:
        print("Saving detections to Excel...")
        df = pd.DataFrame(detection_data)
        try:
            df.to_excel(output_excel, index=False)
            print(f"Successfully saved {len(df)} detections to '{output_excel}'.")
        except Exception as e:
            print(f"Error saving Excel file: {e}")
    else:
        print("No detections found.")
    
    print("Done.")

if __name__ == "__main__":
    main()
