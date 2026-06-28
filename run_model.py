import os
import sys
import subprocess
import time

# 1. Auto-install missing dependencies
required_libs = ["ultralytics", "opencv-python", "cvzone"]
missing_libs = []

for lib in required_libs:
    try:
        if lib == "opencv-python":
            import cv2
        else:
            __import__(lib)
    except ImportError:
        missing_libs.append(lib)

if missing_libs:
    print(f"Missing libraries found: {missing_libs}")
    print("Installing them automatically using pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_libs)
        print("Installation complete! Launching the script...")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        print("Please install them manually using: pip install " + " ".join(required_libs))
        sys.exit(1)

import cv2
from ultralytics import YOLO
import cvzone

def main():
    print("==================================================")
    print("             YOLO Model Run Script                ")
    print("==================================================")

    # 2. Look for best.pt weights
    possible_paths = [
        "best.pt",
        "ai/best.pt",
        "../best.pt",
        "backend/ai_engine/models/best_unified_12c.pt",
        "backend/ai_engine/models/best.pt"
    ]
    
    model_path = None
    for path in possible_paths:
        if os.path.exists(path):
            model_path = path
            break
            
    if not model_path:
        print("[-] Error: 'best.pt' weights file not found in the current directory or subfolders.")
        print("    Please make sure you have 'best.pt' placed next to this script.")
        input("\nPress Enter to exit...")
        return
        
    print(f"[+] Found model weights at: {model_path}")
    print("[*] Loading YOLO model (this might take a few seconds)...")
    try:
        model = YOLO(model_path)
        class_names = model.names
        print(f"[+] Model loaded successfully with classes: {class_names}")
    except Exception as e:
        print(f"[-] Error loading model: {e}")
        input("\nPress Enter to exit...")
        return

    # 3. Choose input source
    print("\nSelect input source:")
    print("1. Live Webcam")
    print("2. Test Video (RVM_TEST.mp4 / YTDown.com...)")
    print("3. Custom File Path (Video or Image)")
    
    choice = input("Enter choice (1, 2, or 3): ").strip()
    
    source = 0
    if choice == '2':
        test_video_paths = [
            "ai/RVM_TEST.mp4",
            "RVM_TEST.mp4",
            "ai/YTDown.com_YouTube_Plane-Lands-On-Runway-Edge_Media_m5Vxo3uBMi8_001_1080p.mp4"
        ]
        found_video = None
        for path in test_video_paths:
            if os.path.exists(path):
                found_video = path
                break
        if found_video:
            source = found_video
            print(f"[+] Using test video: {source}")
        else:
            print("[-] Test video not found, falling back to Webcam...")
            source = 0
    elif choice == '3':
        file_path = input("Enter the full path to your video or image file: ").strip().replace('"', '')
        if os.path.exists(file_path):
            source = file_path
        else:
            print("[-] File not found, falling back to Webcam...")
            source = 0
    else:
        print("[+] Starting Live Webcam...")
        source = 0

    # 4. Detect file type (Image vs Video/Webcam)
    is_image = False
    if isinstance(source, str):
        ext = os.path.splitext(source)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
            is_image = True

    if is_image:
        # --- Handle Image File ---
        img = cv2.imread(source)
        if img is None:
            print(f"[-] Error: Could not read image {source}")
            input("\nPress Enter to exit...")
            return
            
        print("[+] Processing image...")
        results = model(img, verbose=False)
        detection_count = 0
        for r in results:
            for box in r.boxes:
                detection_count += 1
                x1, y1, x2, y2 = int(box.xyxy[0][0]), int(box.xyxy[0][1]), int(box.xyxy[0][2]), int(box.xyxy[0][3])
                w, h = x2 - x1, y2 - y1
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = class_names[cls] if class_names and cls in class_names else f"Class {cls}"

                # Draw stylized corner boxes and labels
                cvzone.cornerRect(img, (x1, y1, w, h), l=9, rt=1)
                cvzone.putTextRect(img, f'{label} {conf:.2f}', (max(0, x1), max(35, y1)), 
                                   scale=1, thickness=1, offset=3)
        
        print(f"[+] Detection completed. Found {detection_count} objects.")
        cv2.imshow("YOLO Model Inference - Image View", img)
        print("    -> Press any key on the image window to close.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print("[+] Image viewer closed.")
    else:
        # --- Handle Video Stream or Live Webcam ---
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"[-] Error: Could not open source {source}")
            input("\nPress Enter to exit...")
            return

        print("\n[+] Detection Active!")
        print("    -> Press 'q' key on the video window to EXIT.")
        
        prev_time = 0
        while True:
            success, img = cap.read()
            if not success:
                print("[*] Stream ended or frame read failed.")
                break

            # Run inference
            results = model(img, verbose=False)

            # Draw bounding boxes and labels
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = int(box.xyxy[0][0]), int(box.xyxy[0][1]), int(box.xyxy[0][2]), int(box.xyxy[0][3])
                    w, h = x2 - x1, y2 - y1
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    label = class_names[cls] if class_names and cls in class_names else f"Class {cls}"

                    cvzone.cornerRect(img, (x1, y1, w, h), l=9, rt=1)
                    cvzone.putTextRect(img, f'{label} {conf:.2f}', (max(0, x1), max(35, y1)), 
                                       scale=1, thickness=1, offset=3)

            # Calculate and display FPS
            current_time = time.time()
            fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
            prev_time = current_time
            cv2.putText(img, f"FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("YOLO Model Inference", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        print("[+] Stream closed successfully.")

if __name__ == "__main__":
    main()
