from ultralytics import YOLO

model = YOLO("models/yolo11n-base.pt")

model.train(
    data="data/data.yaml",

    # training
    epochs=50,
    imgsz=640,
    batch=8,

    # gpu
    device="mps",

    # optim
    optimizer="AdamW",
    lr0=0.001,
    weight_decay=0.0005,
    
    patience=20,

    # augmentation
    degrees=10,
    translate=0.1,
    scale=0.5,
    fliplr=0.5,

    # output
    name="hand-gesture-yolo11n",
    plots=True
)