import time
from datetime import datetime

# Global application state
sensor_state = {
    "temperature": 4.0,
    "humidity": 55.0,
    "mq135": 400.0,
    "mq137": 100.0,
    "lpg": 200.0,
    "co": 50.0,
    "weight": 5000.0,
    "door": False,       # False = Closed
    "light": 30.0,
    "milk": 800.0,
    "pressure": 1013.0,
}

door_open_since = None   # timestamp when door was opened
alerts = []
logs = []
settings = {
    "email": "dhayaisro09@gmail.com",
    "email_alerts_enabled": False,
}

def get_state_copy():
    return dict(sensor_state)

def update_sensor(key, value):
    global door_open_since
    if key == "door":
        val = bool(value)
        if val and not sensor_state["door"]:
            door_open_since = time.time()
        elif not val:
            door_open_since = None
        sensor_state[key] = val
    else:
        sensor_state[key] = float(value)

def add_alert(message, sensor, severity):
    alert = {
        "id": len(alerts) + 1,
        "message": message,
        "sensor": sensor,
        "severity": severity,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Active"
    }
    # Avoid duplicate active alerts for same sensor+message
    for a in alerts:
        if a["message"] == message and a["sensor"] == sensor and a["status"] == "Active":
            return None
    alerts.insert(0, alert)
    add_log(f"[{severity}] {message} (Sensor: {sensor})")
    return alert

def resolve_alert(alert_id):
    for a in alerts:
        if a["id"] == alert_id:
            a["status"] = "Resolved"
            return True
    return False

def clear_alerts_for_sensor(sensor):
    for a in alerts:
        if a["sensor"] == sensor and a["status"] == "Active":
            a["status"] = "Resolved"

def add_log(message):
    log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message
    }
    logs.insert(0, log)
    if len(logs) > 200:
        logs.pop()

def clear_logs():
    logs.clear()

def get_door_open_seconds():
    if sensor_state["door"] and door_open_since is not None:
        return time.time() - door_open_since
    return 0
