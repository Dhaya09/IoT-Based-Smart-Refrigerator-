from flask import Flask, jsonify, request, render_template
import state, rules, mail
import threading
import time

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")

# ─── Background rule runner ───────────────────────────────────────────────────
def background_engine():
    while True:
        triggered = rules.run_rules()
        for alert in triggered:
            mail.send_alert_email(alert)
        time.sleep(3)

engine_thread = threading.Thread(target=background_engine, daemon=True)
engine_thread.start()

# ─── Page Routes ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sensors")
def sensors():
    return render_template("sensors.html")

@app.route("/alerts")
def alerts_page():
    return render_template("alerts.html")

@app.route("/logs")
def logs_page():
    return render_template("logs.html")

@app.route("/settings")
def settings_page():
    return render_template("settings.html")

# ─── API Endpoints ────────────────────────────────────────────────────────────
@app.route("/api/status", methods=["GET"])
def api_status():
    s = state.get_state_copy()
    active_alerts = [a for a in state.alerts if a["status"] == "Active"]
    critical_count = sum(1 for a in active_alerts if a["severity"] == "Critical")
    return jsonify({
        "sensors": s,
        "overall_status": rules.get_overall_status(),
        "alert_count": len(active_alerts),
        "critical_count": critical_count,
        "door_open_seconds": state.get_door_open_seconds(),
        "recent_alerts": state.alerts[:5],
    })

@app.route("/api/update", methods=["POST"])
def api_update():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    for key, val in data.items():
        if key in state.sensor_state:
            state.update_sensor(key, val)
    state.add_log(f"Sensor update: {data}")
    triggered = rules.run_rules()
    for alert in triggered:
        mail.send_alert_email(alert)
    return jsonify({"status": "ok", "triggered_alerts": len(triggered)})

@app.route("/api/alerts", methods=["GET"])
def api_alerts():
    return jsonify(state.alerts)

@app.route("/api/alerts/<int:alert_id>/resolve", methods=["POST"])
def api_resolve(alert_id):
    ok = state.resolve_alert(alert_id)
    return jsonify({"resolved": ok})

@app.route("/api/logs", methods=["GET"])
def api_logs():
    return jsonify(state.logs)

@app.route("/api/logs/clear", methods=["POST"])
def api_clear_logs():
    state.clear_logs()
    return jsonify({"status": "cleared"})

@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "POST":
        data = request.get_json()
        if "email" in data:
            state.settings["email"] = data["email"]
        if "email_alerts_enabled" in data:
            state.settings["email_alerts_enabled"] = bool(data["email_alerts_enabled"])
        state.add_log(f"Settings updated: email={state.settings['email']}, alerts_enabled={state.settings['email_alerts_enabled']}")
        return jsonify({"status": "saved"})
    return jsonify(state.settings)

@app.route("/api/simulate/<scenario>", methods=["POST"])
def simulate(scenario):
    """Quick demo scenarios"""
    if scenario == "spoilage":
        state.update_sensor("mq137", 3000)
        state.add_log("Demo: Spoilage scenario triggered")
    elif scenario == "gasleak":
        state.update_sensor("lpg", 3500)
        state.add_log("Demo: Gas leak scenario triggered")
    elif scenario == "door":
        state.update_sensor("door", True)
        state.add_log("Demo: Door open scenario triggered")
    elif scenario == "lowstock":
        state.update_sensor("weight", 500)
        state.add_log("Demo: Low stock scenario triggered")
    elif scenario == "reset":
        for k, v in {"temperature":4.0,"humidity":55.0,"mq135":400.0,"mq137":100.0,
                     "lpg":200.0,"co":50.0,"weight":5000.0,"door":False,
                     "light":30.0,"milk":800.0,"pressure":1013.0}.items():
            state.update_sensor(k, v)
        state.add_log("Demo: All sensors reset to normal")
    return jsonify({"status": "ok", "scenario": scenario})

if __name__ == "__main__":
    state.add_log("Smart Refrigerator Digital Twin started.")
    app.run(debug=True, port=5000)
