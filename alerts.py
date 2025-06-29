# alerts.py
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()

SENDER = os.getenv("SENDER_EMAIL")
RECEIVER = os.getenv("RECEIVER_EMAIL")
APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

def send_email_alert(data, score, decision):
    if decision in ["Flag for 2FA", "Escalate to Fraud Team"]:
        subject = f"🚨 Fraud Alert: {decision}"
        body = (
            f"Session flagged by ShadowTrail:\n"
            f"Risk Score: {score}\n"
            f"Decision: {decision}\n\n"
            f"Data:\n{data}"
        )

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER
        msg["To"] = RECEIVER

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER, APP_PASSWORD)
            smtp.send_message(msg)
