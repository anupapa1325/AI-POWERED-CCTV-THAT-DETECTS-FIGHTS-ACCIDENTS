import random
import winsound

# Replace this with your YOLO model import
# from ultralytics import YOLO
# model = YOLO("your_model.pt")

class Detection:
    @staticmethod
    def prediction(path):
        """
        Simulated prediction function.
        Replace with your real ML model detection.
        Returns:
            event_id: 0 - moderate accident
                      1 - severe accident
                      2 - violence/fight
                      3 - weapons
            confidence: float
        """
        # ----------------- DEMO MODE -----------------
        event_id = random.choice([0,1,2,3])
        confidence = random.uniform(0.7, 1.0)

        # Windows beep alert
        winsound.Beep(1200, 300)

        # Print detection info
        class_name = ["MODERATE ACCIDENT", "SEVERE ACCIDENT", "VIOLENCE/FIGHT", "WEAPONS"][event_id]
        print(f"\n🚨 DETECTION: {class_name}, Confidence: {round(confidence*100,2)}%")

        return [event_id, confidence]
