# BUZZ_LED.py
# =========================================
# Works on:
# - Windows (simulation mode)
# - Raspberry Pi (real GPIO)
# Correctly imports detection.py from ML part
# =========================================

import os
import sys
import time
from time import sleep

# ======= GPIO setup (cross-platform) =======
try:
    import RPi.GPIO as GPIO
    IS_RPI = True
except (ImportError, RuntimeError):
    # Windows simulation
    IS_RPI = False

    class GPIO:
        BCM = None
        OUT = None
        HIGH = 1
        LOW = 0

        @staticmethod
        def setwarnings(flag): pass

        @staticmethod
        def setmode(mode): pass

        @staticmethod
        def setup(pin, mode): pass

        @staticmethod
        def output(pin, state):
            print(f"[SIM] GPIO Pin {pin} -> {state}")

        @staticmethod
        def cleanup(): pass


# ======= ADD ML part TO PYTHON PATH =======
# Base directory: ACCIDENT DETECTION
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ML part folder
ML_DIR = os.path.join(BASE_DIR, "ML part")

# Add to Python path
sys.path.append(ML_DIR)

# Import detection module
try:
    from detection import Detection as d
    print("✅ Detection module loaded successfully")
except Exception as e:
    print("❌ ERROR importing detection.py:", e)
    d = None


# ======= GPIO CONFIG =======
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Pins
buzzer = 23
redPin = 12
greenPin = 19
bluePin = 13

GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(redPin, GPIO.OUT)
GPIO.setup(greenPin, GPIO.OUT)
GPIO.setup(bluePin, GPIO.OUT)


# ======= LED FUNCTIONS =======
def turnOff():
    GPIO.output(redPin, GPIO.HIGH)
    GPIO.output(greenPin, GPIO.HIGH)
    GPIO.output(bluePin, GPIO.HIGH)
    print("LEDs OFF")


def red():
    GPIO.output(redPin, GPIO.LOW)
    GPIO.output(greenPin, GPIO.HIGH)
    GPIO.output(bluePin, GPIO.HIGH)
    print("RED LED")


def green_led():
    GPIO.output(redPin, GPIO.HIGH)
    GPIO.output(greenPin, GPIO.LOW)
    GPIO.output(bluePin, GPIO.HIGH)
    print("GREEN LED")


def yellow():
    GPIO.output(redPin, GPIO.LOW)
    GPIO.output(greenPin, GPIO.LOW)
    GPIO.output(bluePin, GPIO.HIGH)
    print("YELLOW LED")


# ======= ACCIDENT ALERT =======
def accident_detected(class_id, duration=10):
    end_time = time.time() + duration

    while time.time() < end_time:
        if class_id == 1:  # SEVERE
            GPIO.output(buzzer, GPIO.HIGH)
            red()
            print("🚨 Severe Accident Alert")
            sleep(0.5)
            GPIO.output(buzzer, GPIO.LOW)
            turnOff()
            sleep(0.5)

        elif class_id == 0:  # MODERATE
            GPIO.output(buzzer, GPIO.HIGH)
            yellow()
            print("⚠️ Moderate Accident Alert")
            sleep(2)
            GPIO.output(buzzer, GPIO.LOW)
            turnOff()
            sleep(2)


# ======= MAIN PROGRAM =======
try:
    print("System started")

    if IS_RPI:
        print("Running on Raspberry Pi (LIVE MODE)")
        while True:
            turnOff()
            sleep(1)
            green_led()
            sleep(1)

            if d is not None:
                class_id, confidence = d.static_detection()
                print(f"Detected: Class={class_id}, Confidence={confidence}")

                if confidence >= 0.7:
                    accident_detected(class_id, duration=10)
            else:
                print("Detection module not loaded")
                sleep(2)

    else:
        print("Running on Windows (SIMULATION MODE)")
        end_demo = time.time() + 30  # 30 seconds demo

        while time.time() < end_demo:
            turnOff()
            sleep(1)
            green_led()
            sleep(1)

            if d is not None:
                class_id, confidence = d.static_detection()
                print(f"[SIM] Class={class_id}, Confidence={confidence}")

                if confidence >= 0.7:
                    accident_detected(class_id, duration=5)
            else:
                print("[SIM] Detection module not loaded")
                sleep(2)

except KeyboardInterrupt:
    print("Exiting safely...")

finally:
    turnOff()
    GPIO.cleanup()
