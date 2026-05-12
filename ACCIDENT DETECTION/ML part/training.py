from ultralytics import YOLO
import torch

print("Torch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

model = YOLO("yolov8n.pt")

model.train(
    data="data.yaml",
    epochs=50,
    imgsz=640,
    batch=4,
    device="cpu"
)

model.val()
