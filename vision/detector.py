from ultralytics import YOLO
from gesture import GestureController
from controller import LightController
from client import WemosClient
import cv2

MODEL_PATH = "models/hand-gesture-yolo11n.pt"

model = YOLO(MODEL_PATH)

gesture_controller = GestureController(confidence=0.75, buffer_size=3, cooldown=2.5)
light_controller = LightController()
wemos = WemosClient()

cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

if not cap.isOpened():
    raise RuntimeError("Cannot open webcam")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    results = model.predict(frame, conf=0.7, verbose=False)
    annotated = results[0].plot()
    boxes = results[0].boxes

    if wemos.connected:
        status = "WEMOS: CONNECTED"
    else:
        status = "WEMOS: SEARCHING..."

    cv2.putText(annotated, status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0,255,0) if wemos.connected else (0,0,255), 2)

    if len(boxes):
        idx = boxes.conf.argmax()

        gesture = model.names[int(boxes.cls[idx])]
        confidence = float(boxes.conf[idx])

        action = gesture_controller.update(gesture, confidence)

        if action:
            command = light_controller.handle(action)
            if command:
                print("GESTURE:", action, "->", command)
                wemos.send(command)

    cv2.imshow("Gesture Detector", annotated)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()