# ================= FULL PROJECT: Accident + Violence + Weapons Detection =================

import os
import sys
import time
import random
from time import sleep

# For Windows beep alert
import winsound

# ------------------ FORCE ALERTS ON WINDOWS ------------------
FORCE_ALERTS = True  # Set True to test WhatsApp/Email alerts on Windows

# ------------------ GPIO SETUP ------------------
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
        def output(pin, state): print(f"[SIM] GPIO Pin {pin} -> {state}")
        @staticmethod
        def cleanup(): pass

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# ------------------ BUZZER & LED PINS ------------------
buzzer = 23
redPin = 12
greenPin = 19
bluePin = 13

GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(redPin, GPIO.OUT)
GPIO.setup(greenPin, GPIO.OUT)
GPIO.setup(bluePin, GPIO.OUT)

# ------------------ EMAIL & WHATSAPP SETUP ------------------
from dotenv import load_dotenv
load_dotenv()

# Twilio WhatsApp
from twilio.rest import Client
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_whatsapp_number = os.getenv("FROM_WHATSAPP_NUMBER")
to_whatsapp_number = os.getenv("TO_WHATSAPP_NUMBER")

# Email
import smtplib
from email.message import EmailMessage
smtp_username = os.getenv("SMTP_USERNAME")
smtp_password = os.getenv("SMTP_PASSWORD")
from_email = os.getenv("FROM_EMAIL")
to_email = os.getenv("TO_EMAIL")

# ------------------ ALERT FUNCTIONS ------------------
def send_whatsapp_alert(message):
    if (IS_RPI or FORCE_ALERTS) and account_sid and auth_token:
        client = Client(account_sid, auth_token)
        try:
            client.messages.create(
                from_=f'whatsapp:{from_whatsapp_number}',
                body=message,
                to=f'whatsapp:{to_whatsapp_number}'
            )
            print("[ALERT] WhatsApp message sent!")
        except Exception as e:
            print("[ERROR] WhatsApp alert failed:", e)
    else:
        print("[SIM] WhatsApp alert:", message)

def send_email_alert(subject, body):
    if (IS_RPI or FORCE_ALERTS) and smtp_username and smtp_password:
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(smtp_username, smtp_password)
                smtp.send_message(msg)
            print("[ALERT] Email sent!")
        except Exception as e:
            print("[ERROR] Email alert failed:", e)
    else:
        print("[SIM] Email alert:", body)

# ------------------ LED FUNCTIONS ------------------
def turnOff():
    GPIO.output(redPin, GPIO.HIGH)
    GPIO.output(greenPin, GPIO.HIGH)
    GPIO.output(bluePin, GPIO.HIGH)

def red():
    GPIO.output(redPin, GPIO.LOW)
    GPIO.output(greenPin, GPIO.HIGH)
    GPIO.output(bluePin, GPIO.HIGH)

def green_led():
    GPIO.output(redPin, GPIO.HIGH)
    GPIO.output(greenPin, GPIO.LOW)
    GPIO.output(bluePin, GPIO.HIGH)

def yellow():
    GPIO.output(redPin, GPIO.LOW)
    GPIO.output(greenPin, GPIO.LOW)
    GPIO.output(bluePin, GPIO.HIGH)

def blue():
    GPIO.output(redPin, GPIO.HIGH)
    GPIO.output(greenPin, GPIO.HIGH)
    GPIO.output(bluePin, GPIO.LOW)

# ------------------ ML MODULE ------------------
# Replace this with your YOLO or ML model import
try:
    from detection_module import Detection as DetectionModel
except ModuleNotFoundError:
    print("[WARNING] ML module not found. Demo mode enabled.")
    DetectionModel = None

# ------------------ EVENT ALERT FUNCTION ------------------
def event_alert(event_type, duration=10):
    """Flash LEDs, buzzer and send alerts"""
    message = ""
    if event_type == "accident":
        message = "SEVERE ACCIDENT DETECTED!"
        led_func = red
        buzzer_interval = 0.5
    elif event_type == "moderate_accident":
        message = "MODERATE ACCIDENT DETECTED!"
        led_func = yellow
        buzzer_interval = 2
    elif event_type == "violence":
        message = "VIOLENCE / FIGHT DETECTED!"
        led_func = blue
        buzzer_interval = 1
    elif event_type == "weapons":
        message = "WEAPONS DETECTED!"
        led_func = red
        buzzer_interval = 0.5
    else:
        return

    send_whatsapp_alert(message)
    send_email_alert("Alert from CCTV System", message)

    end_time = time.time() + duration
    while time.time() < end_time:
        GPIO.output(buzzer, GPIO.HIGH)
        led_func()
        winsound.Beep(1200, 300)  # beep alert for Windows
        sleep(buzzer_interval)
        GPIO.output(buzzer, GPIO.LOW)
        turnOff()
        sleep(buzzer_interval)

# ------------------ MAIN LOOP ------------------
try:
    print("[SYSTEM] Starting detection system...")
    while True:
        turnOff()
        sleep(1)
        green_led()
        sleep(1)

        # ------------------ RUN DETECTION ------------------
        if DetectionModel:
            # Use your ML module
            # Replace 'test_image.jpg' with live camera frame path if available
            event_id, confidence = DetectionModel.prediction("test_image.jpg")
        else:
            # Demo mode
            event_id = random.choice([0,1,2,3])
            confidence = random.uniform(0.7, 1.0)

        print(f"[INFO] Event ID: {event_id}, Confidence: {confidence}")

        if confidence >= 0.5:  # Lower threshold for demo/testing
            if event_id == 0:
                event_alert("moderate_accident", duration=5)
            elif event_id == 1:
                event_alert("accident", duration=5)
            elif event_id == 2:
                event_alert("violence", duration=5)
            elif event_id == 3:
                event_alert("weapons", duration=5)

except KeyboardInterrupt:
    print("[SYSTEM] Exiting...")
    turnOff()
    GPIO.cleanup()
