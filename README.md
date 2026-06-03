# 🧊 Smart Refrigerator Digital Twin

A full-stack IoT monitoring platform that simulates a smart refrigerator using 11 virtual sensors. It detects anomalies in real time, fires severity-graded alerts, and sends HTML email notifications — all through a live web dashboard.

---

## Overview

This project is a **digital twin** of a smart refrigerator — a software replica that mirrors physical sensor behaviour without requiring real hardware. Sensor values can be updated via the REST API (or simulated with built-in demo scenarios), and a background rule engine continuously evaluates every reading against safety thresholds. When a rule triggers, an alert is created and, if configured, an email notification is dispatched.

The system is designed to demonstrate end-to-end IoT monitoring: live data ingestion → rule evaluation → alert management → email notification → dashboard visualisation.

---

## Features

- **11 live sensor streams** — temperature, humidity, ammonia (MQ-137), air quality (MQ-135), LPG, CO, weight, door state, ambient light, milk level, and atmospheric pressure
- **Background rule engine** that evaluates thresholds every 3 seconds and auto-resolves alerts when readings return to normal
- **Two-tier alert severity** — `Warning` and `Critical` — with deduplication to prevent alert spam
- **Door-open timer** that escalates to a Critical alert after 30 seconds
- **Combined smart rule** — door open AND high ambient light triggers an energy-waste warning
- **HTML email notifications** via Gmail SMTP with per-sensor suggested actions, togglable from the dashboard
- **5 one-click demo scenarios** — Spoilage, Gas Leak, Door Open, Low Stock, and Reset
- **Live charts** for temperature and ammonia trends (Chart.js, last 20 readings)
- **System log** (capped at 200 entries) with a clear option
- **REST API** for full external control — suitable for connecting real IoT hardware

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Templating | Jinja2 |
| Frontend | Vanilla JS, Chart.js |
| Styling | Custom CSS |
| Email | smtplib, Gmail SMTP (TLS) |
| Configuration | python-dotenv |

---

## Folder Structure

```
smart-fridge/
├── backend/
│   ├── app.py          # Flask app, API routes, background engine thread
│   ├── rules.py        # Threshold rule engine + overall status logic
│   ├── state.py        # In-memory sensor state, alerts, logs, settings
│   └── mail.py         # HTML email alert dispatcher (Gmail SMTP)
├── frontend/
│   ├── templates/
│   │   ├── base.html       # Shared layout and navigation
│   │   ├── index.html      # Dashboard (live stats, charts, demo scenarios)
│   │   ├── sensors.html    # Manual sensor controls
│   │   ├── alerts.html     # Alert list with resolve actions
│   │   ├── logs.html       # System event log
│   │   └── settings.html   # Email configuration
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── .env                # SMTP credentials (not committed)
├── .gitignore
└── requirements.txt
```

---

## Installation

**Prerequisites:** Python 3.8+

```bash
# 1. Clone the repository
git clone https://github.com/your-username/smart-fridge.git
cd smart-fridge

# 2. (Recommended) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
cd backend
python app.py
```

Open your browser at **http://localhost:5000**

---

## Configuration

Email alerts are optional and disabled by default.

1. Create a `.env` file in the project root (already gitignored):

```env
SMTP_USER=your-gmail@gmail.com
SMTP_PASS=your-app-password
```

2. Generate a Gmail App Password: **Google Account → Security → 2-Step Verification → App Passwords**

3. In the running app, go to **Settings**, enter the recipient email address, and enable alerts.

> Email alerts are only sent when a new alert is triggered. Duplicate active alerts for the same sensor are suppressed.

---

## Usage

### Dashboard

The dashboard auto-refreshes every 3 seconds and shows:
- Overall system status banner (Normal / Warning / Critical)
- Live counts for active sensors, active alerts, and critical alerts
- Door status and current temperature
- Live sensor snapshot widgets (colour-coded by state)
- Temperature and Ammonia trend charts
- Recent alerts feed

### Demo Scenarios

Use the Quick Demo buttons on the dashboard to trigger pre-configured sensor states:

| Scenario | What It Does |
|---|---|
| Spoilage Detection | Sets ammonia (MQ-137) to 3000 ppm → Critical alert |
| Gas Leak Alert | Sets LPG to 3500 ppm → Critical alert |
| Door Open Alert | Opens the door → Critical alert after 30 seconds |
| Low Stock Alert | Sets weight to 500 g → Warning alert |
| Reset All | Restores all sensors to safe default values |

### Sending Sensor Data from External Hardware

```bash
curl -X POST http://localhost:5000/api/update \
  -H "Content-Type: application/json" \
  -d '{"temperature": 9.5, "humidity": 75.0}'
```

Any triggered alerts are evaluated and returned in the response.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/status` | Full sensor state, alert counts, recent alerts, door timer |
| `POST` | `/api/update` | Update one or more sensor values |
| `GET` | `/api/alerts` | Full alert list |
| `POST` | `/api/alerts/<id>/resolve` | Mark a specific alert as Resolved |
| `GET` | `/api/logs` | System event log |
| `POST` | `/api/logs/clear` | Clear all log entries |
| `GET` | `/api/settings` | Get current email settings |
| `POST` | `/api/settings` | Update email address or toggle alerts |
| `POST` | `/api/simulate/<scenario>` | Trigger a demo scenario (`spoilage`, `gasleak`, `door`, `lowstock`, `reset`) |

### Example — `/api/status` Response

```json
{
  "sensors": { "temperature": 4.0, "humidity": 55.0, "door": false, "..." },
  "overall_status": "Normal",
  "alert_count": 0,
  "critical_count": 0,
  "door_open_seconds": 0,
  "recent_alerts": []
}
```

---

## Alert Rules

The rule engine in `rules.py` evaluates every sensor on each cycle. Alerts auto-resolve when the reading returns to a safe range.

| Sensor | Trigger Condition | Severity |
|---|---|---|
| Temperature | > 8 °C or < 1 °C | Warning |
| Humidity | > 80 % or < 30 % | Warning |
| Ammonia (MQ-137) | > 2500 ppm | Critical |
| LPG | > 3000 ppm | Critical |
| CO | > 200 ppm | Critical |
| Air Quality (MQ-135) | > 2500 ppm | Warning |
| Weight | < 1000 g | Warning |
| Pressure | < 1000 hPa | Warning |
| Milk Level | < 500 ml | Warning |
| Door | Open for > 30 seconds | Critical |
| Door + Light | Door open AND light > 70 % | Warning |

---

## How It Works

```
Sensor Update (API or demo)
        │
        ▼
  state.py  ──── updates in-memory sensor_state dict
        │
        ▼
  rules.py  ──── evaluates all 11 thresholds
        │
   ┌────┴────┐
   ▼         ▼
New alert   No change
created     (or alert auto-resolved)
   │
   ▼
mail.py ──── sends HTML email (if enabled)
   │
   ▼
Dashboard polls /api/status every 3 s → UI updates
```

The background engine thread runs this loop automatically every 3 seconds, independently of any incoming API request.

---

## Security Notes

- **Never commit `.env`** — it is listed in `.gitignore`. Store SMTP credentials only in environment variables.
- The current state store is in-memory only; a server restart resets all sensor values, alerts, and logs.
- There is no authentication on the API endpoints. For any deployment beyond localhost, add an auth layer.

---

## Future Enhancements

- Persistent storage (SQLite or PostgreSQL) so history survives restarts
- WebSocket push instead of polling for true real-time updates
- Authentication for the web dashboard and API
- Integration with real microcontroller sensors (ESP32/Arduino via serial or MQTT)
- Mobile push notifications as an alternative to email
- Historical data charts and exportable CSV logs

---

## License

This project is open source.

---

## Contact

Built by **Dhayanidhi** — [dhayaisro09@gmail.com](mailto:dhayaisro09@gmail.com)
