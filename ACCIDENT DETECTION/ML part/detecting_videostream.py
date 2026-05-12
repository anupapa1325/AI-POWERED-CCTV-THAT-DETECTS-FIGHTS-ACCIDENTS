from ultralytics import YOLO
import cv2
import winsound
import os

# Load model
model = YOLO("best.pt")

# Frame size
frame_width = 640
frame_height = 480

# Traffic live stream URL
stream_url = "http://kamera.mikulov.cz:8888/mjpg/video.mjpg"

# Create temp folder if not exists
os.makedirs("temp", exist_ok=True)

cap = cv2.VideoCapture(stream_url)

alert_triggered = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (frame_width, frame_height))

    temp_image_path = "temp/temp.jpg"
    cv2.imwrite(temp_image_path, frame)

    # Run detection
    results = model.predict(source=temp_image_path, show=True)

    for r in results:
        if r.boxes is not None:
            for box in r.boxes:
                class_id = r.names[box.cls[0].item()]
                conf = round(box.conf[0].item(), 2)

                if class_id == "severe" and conf > 0.5 and not alert_triggered:
                    print("⚠️ ALERT: Severe accident detected!")
                    winsound.Beep(1200, 1000)
                    alert_triggered = True

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
