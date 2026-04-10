import cv2
from ultralytics import YOLO
import cvzone
import pandas as pd
import time
import os
import tkinter as tk
from tkinter import filedialog

# Explicit path to the requested model
MODEL_PATH = r"f:\znu\fourth year\project\grad project\best.pt"

def process_frame(img, model, class_names, detection_data):
    # Run inference
    results = model(img)

    for r in results:
        # Use model's internal class names if available
        names = r.names
        
        for box in r.boxes:
            x1, y1, x2, y2 = int(box.xyxy[0][0]), int(box.xyxy[0][1]), int(box.xyxy[0][2]), int(box.xyxy[0][3])
            conf = float(box.conf[0])
            cls = int(box.cls[0])

            # Resolve class name
            if names and cls in names:
                current_class = names[cls]
            elif 0 <= cls < len(class_names):
                current_class = class_names[cls]
            else:
                current_class = f"Class {cls}"
            
            # Draw bounding box and label
            cvzone.cornerRect(img, (x1, y1, x2 - x1, y2 - y1), l=9, rt=1)
            cvzone.putTextRect(img, f'{current_class} {conf:.2f}', 
                               (max(0, x1), max(35, y1)), scale=1, thickness=1, offset=3)

            detection_data.append({
                'Class': current_class,
                'Confidence': conf,
                'Box': [x1, y1, x2, y2],
                'Timestamp': time.time()
            })
    return img

def main():
    print("--- Custom Model Tester ---")
    
    # 1. Load Model
    target_model = MODEL_PATH
    if not os.path.exists(target_model):
        print(f"Warning: Designated model not found at: {target_model}")
        # Fallback to checking local dir
        local_model = os.path.join(os.path.dirname(__file__), "..", "best.pt")
        if os.path.exists(local_model):
            print(f"Found model at relative path: {local_model}")
            target_model = local_model
        else:
             print("Error: Could not find 'best.pt' in absolute or relative paths.")
             return

    print(f"Loading model: {target_model}...")
    try:
        model = YOLO(target_model)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Fallback names if model doesn't have them
    class_names = ['Runway', 'aircraft', 'bird', 'vehicle']

    # 2. Select File
    print("Opening file selection dialog...")
    root = tk.Tk()
    root.withdraw()
    
    # Try to start in the project root
    initial_dir = r"f:\znu\fourth year\project\grad project"
    if not os.path.exists(initial_dir):
        initial_dir = os.getcwd()

    file_path = filedialog.askopenfilename(
        title="Select Video or Image to Test Model",
        initialdir=initial_dir,
        filetypes=[("Media", "*.mp4 *.avi *.mkv *.jpg *.png *.jpeg"), ("All", "*.*")]
    )

    if not file_path:
        print("No file selected.")
        return

    print(f"Processing: {file_path}")
    
    detection_data = []
    
    # Check type
    ext = os.path.splitext(file_path)[1].lower()
    is_video = ext in ['.mp4', '.avi', '.mov', '.mkv']

    if is_video:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            print("Error opening video.")
            return
            
        prev_time = 0
        print("Press 'q' to stop.")
        
        while True:
            new_time = time.time()
            success, img = cap.read()
            if not success:
                break
                
            img = process_frame(img, model, class_names, detection_data)
            
            # FPS
            fps = 1 / (new_time - prev_time) if prev_time != new_time else 0
            prev_time = new_time
            cv2.putText(img, f"FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            
            cv2.imshow("Custom Model Test", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
    else:
        img = cv2.imread(file_path)
        if img is None:
            print("Error reading image.")
            return
        img = process_frame(img, model, class_names, detection_data)
        cv2.imshow("Custom Model Test", img)
        print("Press any key to close...")
        cv2.waitKey(0)

    cv2.destroyAllWindows()
    
    # Save results
    if detection_data:
        csv_path = "test_results.csv"
        try:
            pd.DataFrame(detection_data).to_csv(csv_path, index=False)
            print(f"Saved results to {csv_path}")
        except Exception as e:
            print(f"Could not save results: {e}")

if __name__ == "__main__":
    main()
