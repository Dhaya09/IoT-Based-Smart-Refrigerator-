import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import state
import os
from dotenv import load_dotenv

load_dotenv()

# Configure these with your SMTP credentials
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")   # <-- Replace with sender Gmail
SMTP_PASS = os.getenv("SMTP_PASS")       # <-- Replace with Gmail App Password

def send_alert_email(alert):
    cfg = state.settings
    if not cfg.get("email_alerts_enabled"):
        return False
    recipient = cfg.get("email", "").strip()
    if not recipient:
        return False

    subject = f"🚨 Smart Refrigerator Alert – {alert['severity']}"

    action_map = {
        "temperature": "Check and adjust fridge temperature settings.",
        "humidity":    "Inspect door seal and ventilation.",
        "mq137":       "Remove and inspect stored food items immediately.",
        "lpg":         "Check for gas leaks, ventilate the area.",
        "co":          "Carbon monoxide hazard – ventilate immediately and call support.",
        "mq135":       "Check for spoiled items or air contamination.",
        "weight":      "Restock the refrigerator.",
        "pressure":    "Inspect the door seal and compressor.",
        "milk":        "Refill the milk compartment.",
        "door":        "Close the refrigerator door immediately.",
        "light":       "Close the door to save energy.",
    }
    action = action_map.get(alert["sensor"], "Inspect the refrigerator.")

    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;background:#f4f6fa;padding:20px;">
    <div style="max-width:500px;margin:auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.1);">
      <div style="background:{'#dc3545' if alert['severity']=='Critical' else '#ffc107'};padding:20px;color:{'#fff' if alert['severity']=='Critical' else '#333'};">
        <h2 style="margin:0;">Smart Refrigerator Alert 🧊</h2>
        <p style="margin:5px 0 0;">Severity: <strong>{alert['severity']}</strong></p>
      </div>
      <div style="padding:20px;">
        <table style="width:100%;border-collapse:collapse;">
          <tr><td style="padding:8px;font-weight:bold;color:#555;">Alert</td><td style="padding:8px;">{alert['message']}</td></tr>
          <tr style="background:#f9f9f9;"><td style="padding:8px;font-weight:bold;color:#555;">Sensor</td><td style="padding:8px;">{alert['sensor'].upper()}</td></tr>
          <tr><td style="padding:8px;font-weight:bold;color:#555;">Time</td><td style="padding:8px;">{alert['timestamp']}</td></tr>
          <tr style="background:#f9f9f9;"><td style="padding:8px;font-weight:bold;color:#555;">Suggested Action</td><td style="padding:8px;color:#1a73e8;">{action}</td></tr>
        </table>
      </div>
      <div style="background:#f4f6fa;padding:15px;text-align:center;font-size:12px;color:#888;">
        This is an automated alert from your Smart Refrigerator Digital Twin System.
      </div>
    </div>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, recipient, msg.as_string())
        state.add_log(f"Email alert sent to {recipient} for: {alert['message']}")
        return True
    except Exception as e:
        state.add_log(f"Email send FAILED: {str(e)}")
        return False
