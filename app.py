"""RakshakAlert - scratch build, Phase 1 + 2 + 3.

Team AlertNova, PCCOE International Grand Challenge 2026.
Flask + SQLite, plain HTML/CSS/JS. No build step.

Phase 1: public home with live tower map + active alerts + GPS
  nearest tower, admin login, 3-step broadcast, alert history +
  simulated-SMS delivery log.
Phase 2: citizen reports (no login, photo + GPS, tracking ID),
  SOS + SAFE/HELP check-ins, simulated-SMS fallback layer
  (services/sms.py), IoT sensor simulator with auto-trigger,
  admin Incident Queue with duplicate clustering + urgency score.
Phase 3: admin analytics dashboard (live DB counts + CSS bars),
  CSV export (alerts / reports / deliveries), PWA (manifest +
  service worker), multilingual UI for 9 languages (working
  subset: nav, hero, SOS / Report / GPS / Active alerts, footer).

Citizens NEVER log in. Only the Admin logs in. All SMS in Phase 1 is
SIMULATED and labelled as such - no real SMS gateway, no real email.

Run:
  python -m venv .venv
  .venv/bin/pip install -r requirements.txt
  .venv/bin/python app.py --init-db     # creates + seeds instance/rakshakalert.db
  .venv/bin/python app.py              # http://localhost:5000
Admin login: admin / admin123 (see .env.example)
"""

import csv
import io
import math
import os
import sqlite3
import sys
from datetime import datetime, timezone
from functools import wraps

from flask import (
    Flask, Response, flash, g, jsonify, redirect, render_template, request,
    send_from_directory, session, url_for,
)

from services.seed_data import TOWERS, TOWER_RADIUS_KM, generate_citizens
from services import sms as sms_service
from services.i18n import LANGS, get_text
from services.safety import SAFETY
from services import chatbot as chatbot_service
import random
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "rakshakalert.db")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_IDLE_SECONDS = 300  # 5 minute admin auto-logout (Extras)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

SEVERITY_ORDER = {"Green": 0, "Yellow": 1, "Orange": 2, "Red": 3}
SEVERITY_COLOURS = {
    "Green": "#15803d",
    "Yellow": "#ca8a04",
    "Orange": "#ea580c",
    "Red": "#dc2626",
}

# disaster_type -> (suggested severity, template message)
# {area} is replaced in the browser with the selected tower cities.
DISASTER_TYPES = {
    "Flood": ("Orange",
              "FLOOD ALERT for {area}: Heavy flooding is expected in your area. "
              "Move to higher ground now. Avoid flooded roads and underpasses. "
              "Stay indoors unless told to evacuate. Helpline: 112."),
    "Earthquake": ("Red",
                   "EARTHQUAKE ALERT for {area}: A strong earthquake has been reported. "
                   "Drop, cover and hold on. Stay away from buildings, walls and power lines. "
                   "Do not use lifts. Helpline: 112."),
    "Cyclone": ("Red",
                "CYCLONE ALERT for {area}: A severe cyclone is approaching. "
                "Stay indoors, keep away from windows, and secure loose objects. "
                "Do not travel. Follow official evacuation orders. Helpline: 112."),
    "Landslide": ("Orange",
                  "LANDSLIDE ALERT for {area}: Landslide risk is high in your area. "
                  "Avoid hillsides and steep slopes. Move to safe ground if you hear "
                  "cracking sounds or see falling rocks. Helpline: 112."),
    "Wildfire": ("Orange",
                 "WILDFIRE ALERT for {area}: A wildfire is spreading near your area. "
                 "Close windows and doors, stay indoors, and be ready to evacuate. "
                 "Do not enter smoke-filled areas. Helpline: 112."),
    "Heatwave": ("Yellow",
                 "HEATWAVE ALERT for {area}: Extreme heat is expected. Drink water "
                 "regularly, avoid going out between 12 noon and 3 pm, and check on "
                 "elderly neighbours. Helpline: 112."),
    "Tsunami": ("Red",
                "TSUNAMI ALERT for {area}: A tsunami warning is in effect. Move to "
                "high ground or inland immediately. Do not go to the coast to watch. "
                "Helpline: 112."),
    "Heavy Rainfall": ("Yellow",
                       "HEAVY RAINFALL ALERT for {area}: Very heavy rain is expected. "
                       "Avoid low-lying roads, do not drive through waterlogged areas, "
                       "and stay updated with official alerts. Helpline: 112."),
}

# sensor_type -> (unit, threshold, disaster_type, base value)
SENSOR_TYPES = {
    "water_level": ("m", 2.5, "Flood", 0.8),
    "rainfall": ("mm/hr", 50.0, "Heavy Rainfall", 5.0),
    "tremor": ("magnitude", 5.0, "Earthquake", 1.2),
    "temperature": ("C", 45.0, "Heatwave", 32.0),
    # Live wind (Phase 2): simulated IoT readings, no real weather API.
    # wind_direction threshold 360 means it can never cross it, so wind
    # direction alone never auto-triggers an alert.
    "wind_speed": ("km/h", 60.0, "Cyclone", 12.0),
    "wind_direction": ("deg", 360.0, "Cyclone", 90.0),
}
SEVERITY_POINTS = {"Green": 5, "Yellow": 10, "Orange": 20, "Red": 30}

def urgency_score(report_count, sos_count, help_count, safe_count, severity):
    """Urgency = 10*reports + 25*SOS + 15*HELP + severity_points - 5*SAFE (min 0)."""
    return max(0, 10 * report_count + 25 * sos_count + 15 * help_count
               + SEVERITY_POINTS.get(severity, 5) - 5 * safe_count)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "rakshakalert-phase1-dev-key")
app.config["DATABASE"] = DB_PATH
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB photo limit
ALLOWED_PHOTO_EXTS = {"png", "jpg", "jpeg", "webp"}


# ---------------------------------------------------------------- i18n (Phase 3)

def current_lang():
    lang = request.cookies.get("lang", "en")
    return lang if lang in LANGS else "en"


@app.context_processor
def inject_i18n():
    lang = current_lang()
    return {
        "lang": lang,
        "langs": LANGS,
        "t": lambda key: get_text(lang, key),
    }


@app.route("/lang/<code>")
def set_language(code):
    """Language switcher: sets a cookie, English fallback for bad codes."""
    lang = code if code in LANGS else "en"
    target = request.referrer or url_for("home")
    resp = redirect(target)
    resp.set_cookie("lang", lang, max_age=365 * 24 * 3600, samesite="Lax")
    return resp


@app.route("/manifest.json")
def pwa_manifest():
    return send_from_directory(os.path.join(BASE_DIR, "static"),
                               "manifest.json", mimetype="application/manifest+json")


@app.route("/sw.js")
def pwa_sw():
    return send_from_directory(os.path.join(BASE_DIR, "static"),
                               "sw.js", mimetype="application/javascript")


# ---------------------------------------------------------------- database

def get_db():
    if "db" not in g:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables and seed the 60 demo towers + 480 citizens,
    plus exactly 2 demo active alerts (Flood/Orange Mira Road,
    Heavy Rainfall/Yellow Nashik) with simulated-SMS deliveries."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
        CREATE TABLE towers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            radius_km REAL NOT NULL,
            is_sample INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE citizens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            tower_id INTEGER NOT NULL REFERENCES towers(id)
        );
        CREATE TABLE alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            disaster_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            created_by TEXT NOT NULL DEFAULT 'admin'
        );
        CREATE TABLE alert_towers (
            alert_id INTEGER NOT NULL REFERENCES alerts(id),
            tower_id INTEGER NOT NULL REFERENCES towers(id),
            PRIMARY KEY (alert_id, tower_id)
        );
        CREATE TABLE deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER NOT NULL REFERENCES alerts(id),
            citizen_id INTEGER NOT NULL REFERENCES citizens(id),
            phone TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'SIMULATED',
            created_at TEXT NOT NULL
        );
        CREATE TABLE reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_id TEXT UNIQUE,
            disaster_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            name TEXT,
            phone TEXT,
            tower_id INTEGER NOT NULL REFERENCES towers(id),
            lat REAL,
            lng REAL,
            photo_filename TEXT,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL
        );
        CREATE TABLE sos_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tower_id INTEGER NOT NULL REFERENCES towers(id),
            alert_id INTEGER REFERENCES alerts(id),
            lat REAL,
            lng REAL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER REFERENCES alerts(id),
            tower_id INTEGER NOT NULL REFERENCES towers(id),
            kind TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tower_id INTEGER NOT NULL REFERENCES towers(id),
            sensor_type TEXT NOT NULL,
            unit TEXT NOT NULL,
            threshold REAL NOT NULL,
            current_value REAL NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id INTEGER NOT NULL REFERENCES sensors(id),
            value REAL NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE push_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT UNIQUE NOT NULL,
            p256dh TEXT,
            auth TEXT,
            tower_id INTEGER,
            created_at TEXT NOT NULL
        );
        CREATE TABLE push_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER,
            endpoint TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE sms_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            provider TEXT NOT NULL,
            related_type TEXT,
            related_id INTEGER,
            created_at TEXT NOT NULL
        );
    """)
    for code, name, city, state, lat, lng in TOWERS:
        db.execute(
            "INSERT INTO towers (code, name, city, state, lat, lng, radius_km, is_sample)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
            (code, name, city, state, lat, lng, TOWER_RADIUS_KM),
        )
    code_to_id = {
        row[0]: row[1]
        for row in db.execute("SELECT code, id FROM towers").fetchall()
    }
    for name, phone, code in generate_citizens():
        db.execute(
            "INSERT INTO citizens (name, phone, tower_id) VALUES (?, ?, ?)",
            (name, phone, code_to_id[code]),
        )
    rng = random.Random(42)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for tower_id in code_to_id.values():
        for stype, (unit, threshold, _dtype, base) in SENSOR_TYPES.items():
            val = round(base * rng.uniform(0.5, 0.9), 2)
            db.execute(
                "INSERT INTO sensors (tower_id, sensor_type, unit, threshold,"
                " current_value, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (tower_id, stype, unit, threshold, val, now),
            )
    db.commit()
    # Demo active alerts (clean demo state): exactly 2, each to one tower's
    # 8 citizens only, SIMULATED. Uses create_alert() so deliveries and
    # sms_log are written exactly as a real broadcast would.
    demo = [
        ("Flood alert - Mira Road", "Flood", "Orange", "MH-MIR-02"),
        ("Heavy Rainfall alert - Nashik", "Heavy Rainfall", "Yellow", "MH-NSK-05"),
    ]
    for title, dtype, sev, code in demo:
        tid = code_to_id[code]
        tmpl = DISASTER_TYPES[dtype][1]
        city = db.execute("SELECT city FROM towers WHERE id = ?", (tid,)).fetchone()[0]
        create_alert(db, title, dtype, sev, tmpl.replace("{area}", city),
                     [tid], "demo-seed")
    counts = db.execute(
        "SELECT (SELECT COUNT(*) FROM towers), (SELECT COUNT(*) FROM citizens)"
    ).fetchone()
    db.close()
    return counts[0], counts[1]


@app.cli.command("init-db")
def init_db_command():
    towers, citizens = init_db()
    print(f"Database seeded: {towers} towers, {citizens} citizens.")


NEW_TABLES_SQL = '''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_id TEXT UNIQUE,
            disaster_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            name TEXT,
            phone TEXT,
            tower_id INTEGER NOT NULL REFERENCES towers(id),
            lat REAL,
            lng REAL,
            photo_filename TEXT,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sos_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tower_id INTEGER NOT NULL REFERENCES towers(id),
            alert_id INTEGER REFERENCES alerts(id),
            lat REAL,
            lng REAL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER REFERENCES alerts(id),
            tower_id INTEGER NOT NULL REFERENCES towers(id),
            kind TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tower_id INTEGER NOT NULL REFERENCES towers(id),
            sensor_type TEXT NOT NULL,
            unit TEXT NOT NULL,
            threshold REAL NOT NULL,
            current_value REAL NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id INTEGER NOT NULL REFERENCES sensors(id),
            value REAL NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT UNIQUE NOT NULL,
            p256dh TEXT,
            auth TEXT,
            tower_id INTEGER,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS push_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER,
            endpoint TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sms_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            provider TEXT NOT NULL,
            related_type TEXT,
            related_id INTEGER,
            created_at TEXT NOT NULL
        );
    '''


def migrate_db():
    """Add Phase 2 tables to an existing Phase 1 DB without wiping data."""
    db = sqlite3.connect(DB_PATH)
    db.executescript(NEW_TABLES_SQL)
    rng = random.Random(42)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for (tid,) in db.execute("SELECT id FROM towers").fetchall():
        have = {r[0] for r in db.execute(
            "SELECT sensor_type FROM sensors WHERE tower_id = ?", (tid,)).fetchall()}
        for stype, (unit, threshold, _d, base) in SENSOR_TYPES.items():
            if stype in have:
                continue
            db.execute(
                "INSERT INTO sensors (tower_id, sensor_type, unit, threshold,"
                " current_value, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (tid, stype, unit, threshold, round(base * rng.uniform(0.5, 0.9), 2), now),
            )
    db.commit()
    db.close()


def ensure_db():
    if not os.path.exists(DB_PATH):
        init_db()
    else:
        migrate_db()


# ---------------------------------------------------------------- helpers

def haversine_km(lat1, lng1, lat2, lng2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login", next=request.path))
        # Admin auto-logout: 5 idle minutes (Extras).
        import time as _time
        last = session.get("last_activity")
        now_ts = _time.time()
        if last is not None and now_ts - last > ADMIN_IDLE_SECONDS:
            session.clear()
            flash("You were logged out after 5 minutes of no activity. Please log in again.", "error")
            return redirect(url_for("admin_login", next=request.path))
        session["last_activity"] = now_ts
        return view(*args, **kwargs)
    return wrapped


def tower_rows():
    db = get_db()
    return db.execute(
        "SELECT t.*, COUNT(c.id) AS citizen_count FROM towers t"
        " LEFT JOIN citizens c ON c.tower_id = t.id"
        " GROUP BY t.id ORDER BY t.state, t.city"
    ).fetchall()


def active_alerts_for_tower(db, tower_id):
    rows = db.execute(
        "SELECT a.id, a.title, a.disaster_type, a.severity, a.message, a.created_at"
        " FROM alerts a JOIN alert_towers at ON at.alert_id = a.id"
        " WHERE at.tower_id = ? ORDER BY a.created_at DESC",
        (tower_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def tower_to_dict(db, row):
    alerts = active_alerts_for_tower(db, row["id"])
    max_sev = None
    for a in alerts:
        if max_sev is None or SEVERITY_ORDER[a["severity"]] > SEVERITY_ORDER[max_sev]:
            max_sev = a["severity"]
    return {
        "id": row["id"],
        "code": row["code"],
        "name": row["name"],
        "city": row["city"],
        "state": row["state"],
        "lat": row["lat"],
        "lng": row["lng"],
        "radius_km": row["radius_km"],
        "citizen_count": row["citizen_count"],
        "active_alerts": alerts,
        "max_severity": max_sev,
    }


def create_alert(db, title, disaster_type, severity, message, tower_ids,
                 created_by="admin"):
    """Create an alert + alert_towers + simulated-SMS deliveries.

    Shared by the admin broadcast (Phase 1) and the IoT auto-trigger
    (Phase 2). Returns (alert_id, citizens_reached, sms_status).
    """
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cur = db.execute(
        "INSERT INTO alerts (title, disaster_type, severity, message,"
        " created_at, created_by) VALUES (?, ?, ?, ?, ?, ?)",
        (title, disaster_type, severity, message, now, created_by),
    )
    alert_id = cur.lastrowid
    placeholders = ",".join("?" * len(tower_ids))
    db.execute(
        f"INSERT INTO alert_towers (alert_id, tower_id)"
        f" SELECT ?, id FROM towers WHERE id IN ({placeholders})",
        (alert_id, *tower_ids),
    )
    citizens = db.execute(
        f"SELECT id, phone FROM citizens WHERE tower_id IN ({placeholders})",
        (*tower_ids,),
    ).fetchall()
    count, status, _provider = sms_service.send_to_citizens(
        db, alert_id, citizens, message, now)
    log_push_for_alert(db, alert_id, now)
    db.commit()
    return alert_id, count, status


def log_push_for_alert(db, alert_id, now):
    """Log one SIMULATED_PUSH row per push subscriber for an alert.
    No real push service is called without VAPID keys (see README)."""
    subs = db.execute("SELECT endpoint FROM push_subscriptions").fetchall()
    for sub in subs:
        db.execute(
            "INSERT INTO push_log (alert_id, endpoint, status, created_at)"
            " VALUES (?, ?, 'SIMULATED_PUSH', ?)",
            (alert_id, sub["endpoint"], now))
    return len(subs)


def sensor_severity(sensor_type, value):
    """Auto-severity from how far a reading is over its threshold."""
    threshold = SENSOR_TYPES[sensor_type][1]
    ratio = value / threshold if threshold else 0
    if ratio >= 1.5:
        return "Red"
    if ratio >= 1.0:
        return "Orange"
    if ratio >= 0.8:
        return "Yellow"
    return "Green"


def alert_summary(db, alert_id):
    alert = db.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,)).fetchone()
    towers = db.execute(
        "SELECT t.* FROM towers t JOIN alert_towers at ON at.tower_id = t.id"
        " WHERE at.alert_id = ? ORDER BY t.state, t.city",
        (alert_id,),
    ).fetchall()
    count = db.execute(
        "SELECT COUNT(*) FROM deliveries WHERE alert_id = ?", (alert_id,)
    ).fetchone()[0]
    return alert, towers, count


# ---------------------------------------------------------------- public

@app.route("/")
def home():
    ensure_db()
    db = get_db()
    stats = db.execute(
        "SELECT (SELECT COUNT(*) FROM towers) AS towers,"
        " (SELECT COUNT(*) FROM citizens) AS citizens,"
        " (SELECT COUNT(*) FROM alerts) AS alerts"
    ).fetchone()
    alerts = db.execute(
        "SELECT * FROM alerts ORDER BY created_at DESC"
    ).fetchall()
    checkin_counts = {}
    for r in db.execute(
        "SELECT alert_id, kind, COUNT(*) AS n FROM checkins"
        " GROUP BY alert_id, kind"
    ).fetchall():
        checkin_counts.setdefault(r["alert_id"], {})[r["kind"]] = r["n"]
    states = db.execute(
        "SELECT DISTINCT state FROM towers ORDER BY state"
    ).fetchall()
    return render_template(
        "index.html",
        tower_count=stats["towers"],
        citizen_count=stats["citizens"],
        alert_count=stats["alerts"],
        alerts=[dict(a) for a in alerts],
        checkin_counts=checkin_counts,
        states=[s["state"] for s in states],
        severity_colours=SEVERITY_COLOURS,
        disaster_types=DISASTER_TYPES,
    )


@app.route("/api/towers")
def api_towers():
    ensure_db()
    db = get_db()
    return jsonify([tower_to_dict(db, r) for r in tower_rows()])


@app.route("/api/towers/<int:tower_id>")
def api_tower(tower_id):
    ensure_db()
    db = get_db()
    row = db.execute(
        "SELECT t.*, COUNT(c.id) AS citizen_count FROM towers t"
        " LEFT JOIN citizens c ON c.tower_id = t.id WHERE t.id = ? GROUP BY t.id",
        (tower_id,),
    ).fetchone()
    if row is None:
        return jsonify({"error": "Tower not found"}), 404
    citizens = db.execute(
        "SELECT id, name, phone FROM citizens WHERE tower_id = ? ORDER BY name",
        (tower_id,),
    ).fetchall()
    out = tower_to_dict(db, row)
    out["citizens"] = [dict(c) for c in citizens]
    return jsonify(out)


@app.route("/api/nearest")
def api_nearest():
    """Nearest tower by haversine distance. ?lat=19.2952&lng=72.8544"""
    ensure_db()
    try:
        lat = float(request.args["lat"])
        lng = float(request.args["lng"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "Pass ?lat= and &lng= as numbers."}), 400
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return jsonify({"error": "Latitude/longitude out of range."}), 400
    db = get_db()
    best = None
    for row in tower_rows():
        d = haversine_km(lat, lng, row["lat"], row["lng"])
        if best is None or d < best[0]:
            best = (d, row)
    dist, row = best
    out = tower_to_dict(db, row)
    out["distance_km"] = round(dist, 2)
    out["your_lat"] = lat
    out["your_lng"] = lng
    return jsonify(out)


@app.route("/api/alerts/active")
def api_active_alerts():
    ensure_db()
    db = get_db()
    rows = db.execute("SELECT * FROM alerts ORDER BY created_at DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/wind/refresh", methods=["POST"])
def api_wind_refresh():
    """Drift live wind readings a little (simulated IoT, no weather API).

    Called by the public map every 30 seconds. Wind speed drifts by up
    to 3 km/h (kept below its 60 km/h alert threshold); direction drifts
    by up to 15 degrees and wraps 0-359. Returns the updated wind rows.
    """
    ensure_db()
    db = get_db()
    rng = random.Random()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for sensor in db.execute(
        "SELECT * FROM sensors WHERE sensor_type IN ('wind_speed', 'wind_direction')"
    ).fetchall():
        if sensor["sensor_type"] == "wind_speed":
            val = round(max(0.0, min(55.0, sensor["current_value"] + rng.uniform(-3, 3))), 1)
        else:
            val = round((sensor["current_value"] + rng.uniform(-15, 15)) % 360, 1)
        db.execute("UPDATE sensors SET current_value = ?, updated_at = ? WHERE id = ?",
                   (val, now, sensor["id"]))
        db.execute("INSERT INTO sensor_readings (sensor_id, value, created_at)"
                   " VALUES (?, ?, ?)", (sensor["id"], val, now))
    db.commit()
    rows = db.execute(
        "SELECT s.*, t.city FROM sensors s JOIN towers t ON t.id = s.tower_id"
        " WHERE s.sensor_type IN ('wind_speed', 'wind_direction')"
        " ORDER BY s.tower_id, s.sensor_type").fetchall()
    return jsonify([dict(r) for r in rows])


# ---------------------------------------------------------------- admin

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (request.form.get("username") == ADMIN_USERNAME
                and request.form.get("password") == ADMIN_PASSWORD):
            session["admin_logged_in"] = True
            session["admin_user"] = ADMIN_USERNAME
            import time as _time
            session["last_activity"] = _time.time()
            return redirect(request.args.get("next") or url_for("admin_broadcast"))
        flash("Wrong username or password. Demo login is admin / admin123.", "error")
    return render_template("admin_login.html")


@app.route("/admin/ping", methods=["POST"])
@login_required
def admin_ping():
    """Keeps the admin session alive while the admin is active."""
    return jsonify({"ok": True})


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/admin")
def admin_index():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_broadcast"))
    return redirect(url_for("admin_login"))


@app.route("/admin/broadcast", methods=["GET", "POST"])
@login_required
def admin_broadcast():
    ensure_db()
    db = get_db()
    if request.method == "POST":
        tower_ids = request.form.getlist("tower_ids", type=int)
        title = (request.form.get("title") or "").strip()
        disaster_type = request.form.get("disaster_type") or ""
        severity = request.form.get("severity") or ""
        message = (request.form.get("message") or "").strip()
        if not tower_ids:
            flash("Select at least one tower before broadcasting.", "error")
        elif disaster_type not in DISASTER_TYPES:
            flash("Pick a disaster type.", "error")
        elif severity not in SEVERITY_ORDER:
            flash("Pick a severity level.", "error")
        elif not title or not message:
            flash("Title and message are both required.", "error")
        else:
            alert_id, reached, _status = create_alert(
                db, title, disaster_type, severity, message, tower_ids, "admin")
            flash(
                f"Broadcast sent. {reached} citizens reached across "
                f"{len(tower_ids)} tower(s). All messages are Simulated SMS.",
                "success",
            )
            return redirect(url_for("admin_history_detail", alert_id=alert_id))
    towers = tower_rows()
    states = sorted({t["state"] for t in towers})
    return render_template(
        "admin_broadcast.html",
        towers=towers,
        states=states,
        disaster_types=DISASTER_TYPES,
        severity_colours=SEVERITY_COLOURS,
    )


@app.route("/admin/history")
@login_required
def admin_history():
    ensure_db()
    db = get_db()
    rows = db.execute("SELECT * FROM alerts ORDER BY created_at DESC").fetchall()
    items = []
    for a in rows:
        _alert, towers, count = alert_summary(db, a["id"])
        items.append({
            "alert": dict(a),
            "towers": [dict(t) for t in towers],
            "citizens_reached": count,
        })
    return render_template("admin_history.html", items=items)


@app.route("/admin/history/<int:alert_id>")
@login_required
def admin_history_detail(alert_id):
    ensure_db()
    db = get_db()
    alert, towers, count = alert_summary(db, alert_id)
    if alert is None:
        flash("Alert not found.", "error")
        return redirect(url_for("admin_history"))
    rows = db.execute(
        "SELECT d.*, c.name AS citizen_name, t.city, t.state, t.name AS tower_name"
        " FROM deliveries d JOIN citizens c ON c.id = d.citizen_id"
        " JOIN towers t ON t.id = c.tower_id"
        " WHERE d.alert_id = ? ORDER BY t.city, c.name",
        (alert_id,),
    ).fetchall()
    return render_template(
        "admin_history_detail.html",
        alert=dict(alert),
        towers=[dict(t) for t in towers],
        citizens_reached=count,
        deliveries=[dict(r) for r in rows],
        severity_colours=SEVERITY_COLOURS,
    )



# ---------------------------------------------------------------- Phase 2:
# citizen reports, SOS, SAFE/HELP, IoT sensors, Incident Queue

def _nearest_tower_id(db, lat, lng):
    best = None
    for row in tower_rows():
        d = haversine_km(lat, lng, row["lat"], row["lng"])
        if best is None or d < best[0]:
            best = (d, row["id"])
    return best[1] if best else None


def _create_report(db, disaster_type, description, tower_id, lat, lng,
                   name=None, phone=None, photo_filename=None):
    severity = DISASTER_TYPES.get(disaster_type, ("Yellow", ""))[0]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cur = db.execute(
        "INSERT INTO reports (disaster_type, severity, description, name,"
        " phone, tower_id, lat, lng, photo_filename, status, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open', ?)",
        (disaster_type, severity, description, name, phone, tower_id,
         lat, lng, photo_filename, now),
    )
    rid = cur.lastrowid
    tracking_id = f"RA-{rid:05d}"
    db.execute("UPDATE reports SET tracking_id = ? WHERE id = ?",
               (tracking_id, rid))
    db.commit()
    return rid, tracking_id


@app.route("/report", methods=["GET", "POST"])
def citizen_report():
    """Public report form, no login. GET shows the form, POST saves it."""
    ensure_db()
    db = get_db()
    if request.method == "POST":
        disaster_type = request.form.get("disaster_type") or ""
        description = (request.form.get("description") or "").strip()
        tower_id = request.form.get("tower_id", type=int)
        try:
            lat = float(request.form.get("lat")) if request.form.get("lat") else None
            lng = float(request.form.get("lng")) if request.form.get("lng") else None
        except ValueError:
            lat = lng = None
        if disaster_type not in DISASTER_TYPES:
            flash("Pick a disaster type.", "error")
        elif not description:
            flash("Please describe what you see.", "error")
        elif not tower_id:
            flash("Pick your nearest tower (use GPS or choose a city).", "error")
        else:
            if lat is not None and lng is not None:
                tower_id = _nearest_tower_id(db, lat, lng) or tower_id
            photo_filename = None
            f = request.files.get("photo")
            if f and f.filename:
                ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
                if ext in ALLOWED_PHOTO_EXTS:
                    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
                    photo_filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))
            _rid, tracking_id = _create_report(
                db, disaster_type, description, tower_id, lat, lng,
                (request.form.get("name") or "").strip() or None,
                (request.form.get("phone") or "").strip() or None,
                photo_filename)
            flash(f"Report received. Your tracking ID is {tracking_id}."
                  " Keep it to check the status.", "success")
            return redirect(url_for("track_report", tracking_id=tracking_id))
    towers = tower_rows()
    return render_template("report.html", towers=towers,
                           disaster_types=DISASTER_TYPES)


@app.route("/api/report", methods=["POST"])
def api_report():
    """JSON report endpoint (used by the offline-queue retry). No login."""
    ensure_db()
    db = get_db()
    data = request.get_json(silent=True) or {}
    disaster_type = data.get("disaster_type") or ""
    description = (data.get("description") or "").strip()
    tower_id = data.get("tower_id")
    lat, lng = data.get("lat"), data.get("lng")
    if disaster_type not in DISASTER_TYPES or not description or not tower_id:
        return jsonify({"error": "disaster_type, description and tower_id are required."}), 400
    if lat is not None and lng is not None:
        try:
            tower_id = _nearest_tower_id(db, float(lat), float(lng)) or tower_id
        except (TypeError, ValueError):
            pass
    _rid, tracking_id = _create_report(
        db, disaster_type, description, int(tower_id), lat, lng,
        data.get("name") or None, data.get("phone") or None)
    return jsonify({"tracking_id": tracking_id, "status": "Open"}), 201


@app.route("/track")
@app.route("/track/<tracking_id>")
def track_report(tracking_id=None):
    ensure_db()
    db = get_db()
    tracking_id = tracking_id or request.args.get("id") or request.args.get("tracking_id") or ""
    report = None
    if tracking_id:
        row = db.execute(
            "SELECT r.*, t.city, t.state, t.name AS tower_name FROM reports r"
            " JOIN towers t ON t.id = r.tower_id WHERE r.tracking_id = ?",
            (tracking_id.strip().upper(),)).fetchone()
        report = dict(row) if row else None
    return render_template("track.html", tracking_id=tracking_id, report=report)


@app.route("/api/track/<tracking_id>")
def api_track(tracking_id):
    ensure_db()
    db = get_db()
    row = db.execute(
        "SELECT r.*, t.city, t.state FROM reports r"
        " JOIN towers t ON t.id = r.tower_id WHERE r.tracking_id = ?",
        (tracking_id.strip().upper(),)).fetchone()
    if row is None:
        return jsonify({"error": "Tracking ID not found"}), 404
    return jsonify(dict(row))


@app.route("/api/sos", methods=["POST"])
def api_sos():
    """Public SOS, no login. Body JSON or form: tower_id and/or lat+lng."""
    ensure_db()
    db = get_db()
    data = request.get_json(silent=True) or {}
    tower_id = data.get("tower_id") or request.form.get("tower_id", type=int)
    lat = data.get("lat") or request.form.get("lat", type=float)
    lng = data.get("lng") or request.form.get("lng", type=float)
    alert_id = data.get("alert_id") or request.form.get("alert_id", type=int)
    if not tower_id and lat is not None and lng is not None:
        tower_id = _nearest_tower_id(db, lat, lng)
    if not tower_id:
        return jsonify({"error": "tower_id or lat+lng required."}), 400
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cur = db.execute(
        "INSERT INTO sos_events (tower_id, alert_id, lat, lng, created_at)"
        " VALUES (?, ?, ?, ?, ?)", (tower_id, alert_id, lat, lng, now))
    db.commit()
    return jsonify({"sos_id": cur.lastrowid, "tower_id": tower_id,
                    "message": "SOS received. Help is on the way - stay where you are if it is safe."}), 201


@app.route("/api/checkin", methods=["POST"])
def api_checkin():
    """Public SAFE / HELP check-in, no login. JSON: alert_id, tower_id, kind."""
    ensure_db()
    db = get_db()
    data = request.get_json(silent=True) or {}
    kind = (data.get("kind") or "").upper()
    alert_id = data.get("alert_id")
    tower_id = data.get("tower_id")
    if kind not in ("SAFE", "HELP"):
        return jsonify({"error": "kind must be SAFE or HELP."}), 400
    if not tower_id and alert_id:
        row = db.execute(
            "SELECT tower_id FROM alert_towers WHERE alert_id = ? LIMIT 1",
            (alert_id,)).fetchone()
        tower_id = row["tower_id"] if row else None
    if not tower_id:
        return jsonify({"error": "tower_id or alert_id required."}), 400
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    db.execute(
        "INSERT INTO checkins (alert_id, tower_id, kind, created_at)"
        " VALUES (?, ?, ?, ?)", (alert_id, tower_id, kind, now))
    db.commit()
    counts = {r["kind"]: r["n"] for r in db.execute(
        "SELECT kind, COUNT(*) AS n FROM checkins WHERE alert_id = ? GROUP BY kind",
        (alert_id,)).fetchall()} if alert_id else {}
    return jsonify({"ok": True, "kind": kind, "counts": counts}), 201


@app.route("/api/sensors")
def api_sensors():
    """Live sensor readings. ?tower_id= filters to one tower."""
    ensure_db()
    db = get_db()
    tower_id = request.args.get("tower_id", type=int)
    q = ("SELECT s.*, t.city, t.state FROM sensors s"
         " JOIN towers t ON t.id = s.tower_id")
    args = []
    if tower_id:
        q += " WHERE s.tower_id = ?"
        args.append(tower_id)
    q += " ORDER BY t.city, s.sensor_type"
    rows = db.execute(q, args).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["status"] = "warning" if d["current_value"] >= d["threshold"] else "normal"
        out.append(d)
    return jsonify(out)


@app.route("/admin/queue")
@login_required
def admin_queue():
    """Incident Queue: reports grouped by tower + disaster type."""
    ensure_db()
    db = get_db()
    groups = {}
    for r in db.execute(
        "SELECT r.*, t.city, t.state, t.name AS tower_name FROM reports r"
        " JOIN towers t ON t.id = r.tower_id ORDER BY r.created_at DESC"
    ).fetchall():
        key = (r["tower_id"], r["disaster_type"])
        g = groups.setdefault(key, {
            "tower_id": r["tower_id"], "city": r["city"], "state": r["state"],
            "tower_name": r["tower_name"], "disaster_type": r["disaster_type"],
            "reports": [], "severity": r["severity"],
            "open_count": 0, "sos_count": 0, "help_count": 0, "safe_count": 0,
            "first_at": r["created_at"], "last_at": r["created_at"],
        })
        g["reports"].append(dict(r))
        if r["status"] != "Resolved":
            g["open_count"] += 1
        if SEVERITY_ORDER.get(r["severity"], 0) > SEVERITY_ORDER.get(g["severity"], 0):
            g["severity"] = r["severity"]
        g["first_at"] = min(g["first_at"], r["created_at"])
        g["last_at"] = max(g["last_at"], r["created_at"])
    for g in groups.values():
        g["sos_count"] = db.execute(
            "SELECT COUNT(*) FROM sos_events WHERE tower_id = ?",
            (g["tower_id"],)).fetchone()[0]
        for kind in ("SAFE", "HELP"):
            g[{"SAFE": "safe_count", "HELP": "help_count"}[kind]] = db.execute(
                "SELECT COUNT(*) FROM checkins WHERE tower_id = ? AND kind = ?",
                (g["tower_id"], kind)).fetchone()[0]
        g["urgency"] = urgency_score(len(g["reports"]), g["sos_count"],
                                     g["help_count"], g["safe_count"], g["severity"])
    # SOS-only towers with no report yet also appear, urgent at top.
    sos_only = []
    for r in db.execute(
        "SELECT s.tower_id, COUNT(*) AS n, t.city, t.state FROM sos_events s"
        " JOIN towers t ON t.id = s.tower_id GROUP BY s.tower_id"
    ).fetchall():
        if not any(g["tower_id"] == r["tower_id"] for g in groups.values()):
            sos_only.append({"tower_id": r["tower_id"], "city": r["city"],
                             "state": r["state"], "disaster_type": "SOS",
                             "reports": [], "severity": "Red", "open_count": 0,
                             "sos_count": r["n"], "help_count": 0, "safe_count": 0,
                             "first_at": "", "last_at": "",
                             "urgency": urgency_score(0, r["n"], 0, 0, "Red")})
    items = sorted(list(groups.values()) + sos_only,
                   key=lambda g: (-g["urgency"], g["first_at"]))
    sos_total = db.execute("SELECT COUNT(*) FROM sos_events").fetchone()[0]
    return render_template("admin_queue.html", items=items, sos_total=sos_total)


def _set_report_status(db, report_id, status):
    row = db.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if row is None:
        return None
    db.execute("UPDATE reports SET status = ? WHERE id = ?", (status, report_id))
    db.commit()
    if row["phone"]:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        tower = db.execute("SELECT city FROM towers WHERE id = ?",
                           (row["tower_id"],)).fetchone()
        city = tower["city"] if tower else ""
        sms_service.log_single(
            db, row["phone"],
            f"RakshakAlert: your report {row['tracking_id']} ({row['disaster_type']},"
            f" {city}) is now {status}.",
            "report", report_id, now)
        db.commit()
    return dict(row)


@app.route("/admin/report/<int:report_id>/acknowledge", methods=["POST"])
@login_required
def admin_ack_report(report_id):
    ensure_db()
    db = get_db()
    if _set_report_status(db, report_id, "Acknowledged") is None:
        flash("Report not found.", "error")
    else:
        flash("Report acknowledged.", "success")
    return redirect(url_for("admin_queue"))


@app.route("/admin/report/<int:report_id>/resolve", methods=["POST"])
@login_required
def admin_resolve_report(report_id):
    ensure_db()
    db = get_db()
    if _set_report_status(db, report_id, "Resolved") is None:
        flash("Report not found.", "error")
    else:
        flash("Report resolved.", "success")
    return redirect(url_for("admin_queue"))


@app.route("/admin/queue/bulk", methods=["POST"])
@login_required
def admin_queue_bulk():
    ensure_db()
    db = get_db()
    tower_id = request.form.get("tower_id", type=int)
    disaster_type = request.form.get("disaster_type") or ""
    action = request.form.get("action") or ""
    status = {"acknowledge": "Acknowledged", "resolve": "Resolved"}.get(action)
    if not tower_id or not disaster_type or not status:
        flash("Pick a group and an action.", "error")
        return redirect(url_for("admin_queue"))
    rows = db.execute(
        "SELECT id FROM reports WHERE tower_id = ? AND disaster_type = ?"
        " AND status != ?", (tower_id, disaster_type, status)).fetchall()
    for r in rows:
        _set_report_status(db, r["id"], status)
    flash(f"{len(rows)} report(s) marked {status}.", "success")
    return redirect(url_for("admin_queue"))


@app.route("/admin/sensors")
@login_required
def admin_sensors():
    ensure_db()
    db = get_db()
    rows = db.execute(
        "SELECT s.*, t.city, t.state FROM sensors s JOIN towers t ON t.id = s.tower_id"
        " ORDER BY t.city, s.sensor_type").fetchall()
    items = []
    for r in rows:
        d = dict(r)
        d["status"] = "warning" if d["current_value"] >= d["threshold"] else "normal"
        d["severity"] = sensor_severity(d["sensor_type"], d["current_value"])
        items.append(d)
    return render_template("admin_sensors.html", items=items)


def _trigger_sensor_alert(db, sensor):
    """Auto-create an alert when a sensor crosses its threshold."""
    tower = db.execute("SELECT * FROM towers WHERE id = ?",
                       (sensor["tower_id"],)).fetchone()
    dtype = SENSOR_TYPES[sensor["sensor_type"]][2]
    sev = sensor_severity(sensor["sensor_type"], sensor["current_value"])
    title = f"{dtype} alert - {tower['city']} (IoT sensor)"
    message = (f"{dtype.upper()} ALERT for {tower['city']}: Auto-triggered by"
               f" IoT sensor ({sensor['sensor_type']} reading"
               f" {sensor['current_value']} {sensor['unit']}, threshold"
               f" {sensor['threshold']} {sensor['unit']}). Take precautions."
               " Helpline: 112.")
    alert_id, reached, _s = create_alert(
        db, title, dtype, sev, message, [sensor["tower_id"]], "iot-sensor")
    return alert_id, reached


@app.route("/admin/sensors/<int:sensor_id>/simulate", methods=["POST"])
@login_required
def admin_sensor_simulate(sensor_id):
    """Tick a sensor reading (random walk); auto-alert if over threshold."""
    ensure_db()
    db = get_db()
    sensor = db.execute("SELECT * FROM sensors WHERE id = ?", (sensor_id,)).fetchone()
    if sensor is None:
        flash("Sensor not found.", "error")
        return redirect(url_for("admin_sensors"))
    rng = random.Random()
    base = SENSOR_TYPES[sensor["sensor_type"]][3]
    new_val = round(max(0.1, sensor["current_value"] * rng.uniform(0.8, 1.35)), 2)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    db.execute("UPDATE sensors SET current_value = ?, updated_at = ? WHERE id = ?",
               (new_val, now, sensor_id))
    db.execute("INSERT INTO sensor_readings (sensor_id, value, created_at)"
               " VALUES (?, ?, ?)", (sensor_id, new_val, now))
    db.commit()
    sensor = db.execute("SELECT * FROM sensors WHERE id = ?", (sensor_id,)).fetchone()
    if new_val >= sensor["threshold"]:
        alert_id, reached = _trigger_sensor_alert(db, dict(sensor))
        flash(f"Sensor crossed its threshold. Auto-alert created ({reached} citizens reached).", "success")
        return redirect(url_for("admin_history_detail", alert_id=alert_id))
    flash(f"Sensor reading updated: {new_val} {sensor['unit']} (threshold {sensor['threshold']}). No alert - below threshold.", "success")
    return redirect(url_for("admin_sensors"))


@app.route("/admin/sensors/trigger-test", methods=["POST"])
@login_required
def admin_sensor_trigger_test():
    """Demo button: force one sensor over threshold and auto-alert."""
    ensure_db()
    db = get_db()
    tower_id = request.form.get("tower_id", type=int)
    sensor_type = request.form.get("sensor_type") or "water_level"
    if sensor_type not in SENSOR_TYPES:
        flash("Unknown sensor type.", "error")
        return redirect(url_for("admin_sensors"))
    sensor = db.execute(
        "SELECT * FROM sensors WHERE tower_id = ? AND sensor_type = ?",
        (tower_id, sensor_type)).fetchone()
    if sensor is None:
        flash("Sensor not found for that tower.", "error")
        return redirect(url_for("admin_sensors"))
    threshold = sensor["threshold"]
    new_val = round(threshold * 1.3, 2)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    db.execute("UPDATE sensors SET current_value = ?, updated_at = ? WHERE id = ?",
               (new_val, now, sensor["id"]))
    db.execute("INSERT INTO sensor_readings (sensor_id, value, created_at)"
               " VALUES (?, ?, ?)", (sensor["id"], new_val, now))
    db.commit()
    sensor = db.execute("SELECT * FROM sensors WHERE id = ?", (sensor["id"],)).fetchone()
    alert_id, reached = _trigger_sensor_alert(db, dict(sensor))
    flash(f"Test sensor event triggered. Auto-alert created ({reached} citizens reached).", "success")
    return redirect(url_for("admin_history_detail", alert_id=alert_id))


# ---------------------------------------------------------------- Phase 3:
# analytics dashboard + CSV export

def _bar_rows(rows, total):
    out = []
    for label, count in rows:
        pct = round(100 * count / total) if total else 0
        out.append({"label": label, "count": count, "pct": pct})
    return out


@app.route("/admin/analytics")
@login_required
def admin_analytics():
    """Analytics dashboard, admin only. Every number is computed live
    from the SQLite DB, nothing is hardcoded."""
    ensure_db()
    db = get_db()
    totals = {
        "alerts": db.execute("SELECT COUNT(*) FROM alerts").fetchone()[0],
        "reports": db.execute("SELECT COUNT(*) FROM reports").fetchone()[0],
        "sos": db.execute("SELECT COUNT(*) FROM sos_events").fetchone()[0],
        "deliveries": db.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0],
        "citizens": db.execute("SELECT COUNT(*) FROM citizens").fetchone()[0],
        "towers": db.execute("SELECT COUNT(*) FROM towers").fetchone()[0],
        "safe": db.execute("SELECT COUNT(*) FROM checkins WHERE kind = 'SAFE'").fetchone()[0],
        "help": db.execute("SELECT COUNT(*) FROM checkins WHERE kind = 'HELP'").fetchone()[0],
    }
    by_type = _bar_rows(db.execute(
        "SELECT disaster_type, COUNT(*) FROM alerts GROUP BY disaster_type"
        " ORDER BY COUNT(*) DESC").fetchall(), totals["alerts"])
    by_severity = _bar_rows(db.execute(
        "SELECT severity, COUNT(*) FROM alerts GROUP BY severity").fetchall(),
        totals["alerts"])
    sev_order = {"Red": 0, "Orange": 1, "Yellow": 2, "Green": 3}
    by_severity.sort(key=lambda r: sev_order.get(r["label"], 9))
    by_status = _bar_rows(db.execute(
        "SELECT status, COUNT(*) FROM reports GROUP BY status").fetchall(),
        totals["reports"])
    by_delivery_status = _bar_rows(db.execute(
        "SELECT status, COUNT(*) FROM deliveries GROUP BY status").fetchall(),
        totals["deliveries"])
    by_state = _bar_rows(db.execute(
        "SELECT t.state, COUNT(DISTINCT a.id) FROM alerts a"
        " JOIN alert_towers at ON at.alert_id = a.id"
        " JOIN towers t ON t.id = at.tower_id"
        " GROUP BY t.state ORDER BY COUNT(DISTINCT a.id) DESC LIMIT 10").fetchall(),
        totals["alerts"])
    return render_template(
        "admin_analytics.html",
        totals=totals,
        by_type=by_type,
        by_severity=by_severity,
        by_status=by_status,
        by_delivery_status=by_delivery_status,
        by_state=by_state,
    )


@app.route("/admin/export/<kind>")
@login_required
def admin_export(kind):
    """CSV export, admin only. Real DB rows, proper headers, dated file name."""
    ensure_db()
    db = get_db()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    buf = io.StringIO()
    w = csv.writer(buf)
    if kind == "alerts":
        w.writerow(["id", "title", "disaster_type", "severity", "message",
                    "towers", "citizens_reached", "created_at", "created_by"])
        for a in db.execute("SELECT * FROM alerts ORDER BY created_at DESC").fetchall():
            _alert, towers, count = alert_summary(db, a["id"])
            w.writerow([a["id"], a["title"], a["disaster_type"], a["severity"],
                        a["message"], "; ".join(t["city"] for t in towers),
                        count, a["created_at"], a["created_by"]])
    elif kind == "reports":
        w.writerow(["tracking_id", "disaster_type", "severity", "description",
                    "city", "state", "status", "name", "phone", "created_at"])
        for r in db.execute(
            "SELECT r.*, t.city, t.state FROM reports r"
            " JOIN towers t ON t.id = r.tower_id ORDER BY r.created_at DESC").fetchall():
            w.writerow([r["tracking_id"], r["disaster_type"], r["severity"],
                        r["description"], r["city"], r["state"], r["status"],
                        r["name"] or "", r["phone"] or "", r["created_at"]])
    elif kind == "deliveries":
        w.writerow(["id", "alert_id", "alert_title", "citizen_name", "phone",
                    "city", "state", "status", "created_at"])
        for d in db.execute(
            "SELECT d.*, a.title AS alert_title, c.name AS citizen_name,"
            " t.city, t.state FROM deliveries d"
            " JOIN alerts a ON a.id = d.alert_id"
            " JOIN citizens c ON c.id = d.citizen_id"
            " JOIN towers t ON t.id = c.tower_id"
            " ORDER BY d.created_at DESC").fetchall():
            w.writerow([d["id"], d["alert_id"], d["alert_title"],
                        d["citizen_name"], d["phone"], d["city"], d["state"],
                        d["status"], d["created_at"]])
    else:
        flash("Unknown export. Pick alerts, reports or deliveries.", "error")
        return redirect(url_for("admin_analytics"))
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition":
                 f'attachment; filename="rakshakalert_{kind}_{today}.csv"'},
    )



# ---------------------------------------------------------------- Extras:
# safety guides, push notifications, rule-based chatbot

@app.route("/safety")
def safety_guide():
    return render_template("safety.html", guides=SAFETY)


@app.route("/safety/<slug>")
def safety_detail(slug):
    guide = SAFETY.get(slug)
    if guide is None:
        flash("Safety guide not found.", "error")
        return redirect(url_for("safety_guide"))
    return render_template("safety_detail.html", guide=guide, slug=slug)


@app.route("/api/push/subscribe", methods=["POST"])
def api_push_subscribe():
    """Save a push subscription. No login, no personal data.
    Real Web Push needs VAPID keys; without them the subscription is
    stored and broadcast logs SIMULATED_PUSH. Returns 201."""
    ensure_db()
    db = get_db()
    data = request.get_json(silent=True) or {}
    endpoint = (data.get("endpoint") or "").strip()
    if not endpoint:
        return jsonify({"error": "endpoint is required."}), 400
    keys = data.get("keys") or {}
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    db.execute(
        "INSERT OR REPLACE INTO push_subscriptions (endpoint, p256dh, auth, tower_id, created_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (endpoint, keys.get("p256dh") or "", keys.get("auth") or "",
         data.get("tower_id"), now))
    db.commit()
    count = db.execute("SELECT COUNT(*) FROM push_subscriptions").fetchone()[0]
    return jsonify({"ok": True, "subscriptions": count}), 201


@app.route("/api/push/status")
def api_push_status():
    ensure_db()
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM push_subscriptions").fetchone()[0]
    return jsonify({"subscriptions": count})


@app.route("/api/chat/ui")
def api_chat_ui():
    """Chatbot UI strings in the current site language (cookie)."""
    lang = request.args.get("lang") or current_lang()
    if lang not in LANGS:
        lang = "en"
    return jsonify(chatbot_service.ui_strings(lang))


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Rule-based help assistant. No LLM, no external API."""
    ensure_db()
    db = get_db()
    data = request.get_json(silent=True) or {}
    lang = data.get("lang") or current_lang()
    if lang not in LANGS:
        lang = "en"
    result = chatbot_service.answer(data.get("message") or "", db, lang)
    return jsonify(result)


# ---------------------------------------------------------------- run

if __name__ == "__main__":
    if "--init-db" in sys.argv:
        towers, citizens = init_db()
        print(f"Database seeded: {towers} towers, {citizens} citizens.")
        print(f"Database file: {DB_PATH}")
        sys.exit(0)
    ensure_db()
    port = int(os.environ.get("PORT", 5000))
    print(f"RakshakAlert Phase 1+2+3 - http://0.0.0.0:{port}  (admin: admin / admin123)")
    app.run(host="0.0.0.0", port=port, debug=False)
