import state

def run_rules():
    s = state.sensor_state
    triggered = []

    # --- Temperature ---
    if s["temperature"] > 8:
        a = state.add_alert("Temperature too HIGH – Risk of food spoilage", "temperature", "Warning")
        if a: triggered.append(a)
    elif s["temperature"] < 1:
        a = state.add_alert("Temperature too LOW – Risk of freezing", "temperature", "Warning")
        if a: triggered.append(a)
    else:
        state.clear_alerts_for_sensor("temperature")

    # --- Humidity ---
    if s["humidity"] > 80:
        a = state.add_alert("Humidity too HIGH – Mold risk", "humidity", "Warning")
        if a: triggered.append(a)
    elif s["humidity"] < 30:
        a = state.add_alert("Humidity too LOW – Food may dry out", "humidity", "Warning")
        if a: triggered.append(a)
    else:
        state.clear_alerts_for_sensor("humidity")

    # --- Ammonia (MQ-137) – Spoilage ---
    if s["mq137"] > 2500:
        a = state.add_alert("SPOILAGE DETECTED – Ammonia level critical", "mq137", "Critical")
        if a: triggered.append(a)
    else:
        state.clear_alerts_for_sensor("mq137")

    # --- LPG ---
    if s["lpg"] > 3000:
        a = state.add_alert("GAS LEAK DETECTED – LPG level critical", "lpg", "Critical")
        if a: triggered.append(a)
    else:
        state.clear_alerts_for_sensor("lpg")

    # --- CO ---
    if s["co"] > 200:
        a = state.add_alert("CARBON MONOXIDE level critical – Danger!", "co", "Critical")
        if a: triggered.append(a)
    else:
        state.clear_alerts_for_sensor("co")

    # --- Air Quality (MQ-135) ---
    if s["mq135"] > 2500:
        a = state.add_alert("Poor Air Quality detected inside fridge", "mq135", "Warning")
        if a: triggered.append(a)
    else:
        state.clear_alerts_for_sensor("mq135")

    # --- Weight ---
    if s["weight"] < 1000:
        a = state.add_alert("Low food stock – Weight below threshold", "weight", "Warning")
        if a: triggered.append(a)
    else:
        state.clear_alerts_for_sensor("weight")

    # --- Pressure ---
    if s["pressure"] < 1000:
        a = state.add_alert("Low pressure detected – Seal may be broken", "pressure", "Warning")
        if a: triggered.append(a)
    else:
        state.clear_alerts_for_sensor("pressure")

    # --- Milk ---
    if s["milk"] < 500:
        a = state.add_alert("Low milk level – Please refill", "milk", "Warning")
        if a: triggered.append(a)
    else:
        state.clear_alerts_for_sensor("milk")

    # --- Door open too long ---
    door_secs = state.get_door_open_seconds()
    if door_secs > 30:
        a = state.add_alert(f"Door has been OPEN for {int(door_secs)}s – Close immediately!", "door", "Critical")
        if a: triggered.append(a)
    elif not s["door"]:
        state.clear_alerts_for_sensor("door")

    # --- Smart Combined Rule: Door open + High light ---
    if s["door"] and s["light"] > 70:
        a = state.add_alert("Door open with high light level – Energy waste", "light", "Warning")
        if a: triggered.append(a)
    else:
        state.clear_alerts_for_sensor("light")

    return triggered

def get_overall_status():
    active = [a for a in state.alerts if a["status"] == "Active"]
    if any(a["severity"] == "Critical" for a in active):
        return "Critical"
    elif any(a["severity"] == "Warning" for a in active):
        return "Warning"
    return "Normal"
