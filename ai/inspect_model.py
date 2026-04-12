from ultralytics import YOLO

model_path = r"f:\znu\fourth year\project\grad project\best.pt"
model = YOLO(model_path)

print("--- Model Class Names ---")
print(model.names)
print("-------------------------")
