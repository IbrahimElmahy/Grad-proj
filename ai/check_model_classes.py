from ultralytics import YOLO

model_path = r"f:/znu/fourth year/project/grad project/backend/ai_engine/models/best.pt"
model = YOLO(model_path)
print("Class Names:", model.names)
