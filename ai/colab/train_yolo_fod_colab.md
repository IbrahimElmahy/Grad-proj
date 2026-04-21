# Google Colab Training Cells

Use the following cells in order to train `ai/scripts/train_yolo_fod.py` on Google Colab with GPU.

Before running the notebook:
- In Colab, set `Runtime -> Change runtime type -> GPU`.
- Upload your project folder to Google Drive, or clone it from GitHub into Drive.
- Make sure your dataset `data.yaml` points to the dataset location available in Colab.

## 1. Mount Google Drive

```python
from google.colab import drive
drive.mount("/content/drive")
```

## 2. Check the GPU

```bash
!nvidia-smi
```

## 3. Define Project Paths

```python
from pathlib import Path

DRIVE_ROOT = Path("/content/drive/MyDrive")
PROJECT_ROOT = DRIVE_ROOT / "grad_project"
WORK_ROOT = Path("/content/grad_project")

print("Drive project:", PROJECT_ROOT)
print("Working copy:", WORK_ROOT)
```

## 4. Copy the Project from Drive to Colab Local Storage

Training is faster from `/content` than directly from Google Drive.

```bash
!rm -rf /content/grad_project
!cp -r "/content/drive/MyDrive/grad_project" /content/grad_project
```

## 5. Install Dependencies

```bash
!python -m pip install --upgrade pip
!pip install -U ultralytics albumentations roboflow kaggle opencv-python-headless PyYAML
!pip install -r /content/grad_project/ai/requirements.txt
```

## 6. Verify the Training Script Exists

```bash
!ls /content/grad_project/ai/scripts
```

## 7. Set the Dataset and Weights Paths

Adjust these paths to match your Drive layout.

```python
DATA_YAML = "/content/grad_project/ai/configs/fod_data.yaml"
BASE_WEIGHTS = "/content/grad_project/backend/ai_engine/models/best.pt"
OUTPUT_PROJECT = "/content/drive/MyDrive/grad_project/ai/outputs/training"

print(DATA_YAML)
print(BASE_WEIGHTS)
print(OUTPUT_PROJECT)
```

## 8. Launch YOLO Training on GPU

```bash
!python /content/grad_project/ai/scripts/train_yolo_fod.py \
    --data "/content/grad_project/ai/configs/fod_data.yaml" \
    --weights "/content/grad_project/backend/ai_engine/models/best.pt" \
    --epochs 100 \
    --imgsz 1280 \
    --batch 16 \
    --device 0 \
    --workers 4 \
    --project "/content/drive/MyDrive/grad_project/ai/outputs/training" \
    --name "colab_fod_run" \
    --optimizer AdamW \
    --lr0 0.001 \
    --patience 20 \
    --cache
```

## 9. Inspect Saved Weights

```bash
!ls "/content/drive/MyDrive/grad_project/ai/outputs/training/colab_fod_run/weights"
```

## 10. Optional: Copy Any Local Run Artifacts Back to Drive

```bash
!rsync -av /content/grad_project/ai/outputs/ "/content/drive/MyDrive/grad_project/ai/outputs/"
```
