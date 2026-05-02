import json
import os
import datetime

DB_PATH = os.path.join("data", "users.json")
SCANS_PATH = os.path.join("data", "scans.json")

def load_db():
    """Load the database from file. Create empty if not exists."""
    if not os.path.exists(DB_PATH):
        os.makedirs("data", exist_ok=True)
        with open(DB_PATH, "w") as f:
            json.dump({}, f)
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(data):
    """Save the database dictionary to JSON file."""
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

def get_user(student_id):
    """Retrieve user data by student_id. Returns None if not found."""
    db = load_db()
    return db.get(str(student_id))

def log_scan(student_id, points, carbon):
    """Record a scan event in scans.json."""
    entry = {
        "student_id": str(student_id),
        "points_added": points,
        "carbon_saved": carbon,
        "timestamp": datetime.datetime.now().isoformat()
    }
    scans = []
    if os.path.exists(SCANS_PATH):
        with open(SCANS_PATH, "r") as f:
            scans = json.load(f)
    scans.append(entry)
    with open(SCANS_PATH, "w") as f:
        json.dump(scans, f, indent=4)

def get_recent_scans(limit=10):
    """Retrieve the last `limit` scan records."""
    if not os.path.exists(SCANS_PATH):
        return []
    with open(SCANS_PATH, "r") as f:
        scans = json.load(f)
    return scans[-limit:]

def add_green_points(student_id, points=10, carbon_saved=80):
    """
    Add green points and carbon saved for a student.
    Creates a new profile if student doesn't exist.
    """
    student_id = str(student_id)
    db = load_db()
    if student_id not in db:
        db[student_id] = {
            "student_id": student_id,
            "name": "",
            "green_points": 0,
            "carbon_saved_grams": 0
        }
    db[student_id]["green_points"] += points
    db[student_id]["carbon_saved_grams"] += carbon_saved
    save_db(db)
    log_scan(student_id, points, carbon_saved)  # تسجيل العملية
    return db[student_id]