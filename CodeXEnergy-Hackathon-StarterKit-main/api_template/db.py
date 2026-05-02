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

def log_scan(student_id, points, carbon, item_details=None):
    """Record a scan event in scans.json, optionally with item details."""
    entry = {
        "student_id": str(student_id),
        "points_added": points,
        "carbon_saved": carbon,
        "timestamp": datetime.datetime.now().isoformat()
    }
    if item_details:
        entry["item_details"] = item_details
    scans = []
    if os.path.exists(SCANS_PATH):
        with open(SCANS_PATH, "r") as f:
            scans = json.load(f)
    scans.append(entry)
    with open(SCANS_PATH, "w") as f:
        json.dump(scans, f, indent=4)

def get_recent_scans(limit=10):
    """Retrieve the last `limit` scan records (all students)."""
    if not os.path.exists(SCANS_PATH):
        return []
    with open(SCANS_PATH, "r") as f:
        scans = json.load(f)
    return scans[-limit:]

def get_student_scans(student_id, limit=10):
    """Retrieve the last scans for a specific student."""
    if not os.path.exists(SCANS_PATH):
        return []
    with open(SCANS_PATH, "r") as f:
        all_scans = json.load(f)
    student_scans = [scan for scan in all_scans if str(scan.get("student_id")) == str(student_id)]
    return student_scans[-limit:]

def add_green_points(student_id, points=10, carbon_saved=80, item_details=None, name=None):
    """
    Add green points and carbon saved for a student.
    Creates a new profile if student doesn't exist.
    Optionally updates the student's name if provided and currently empty.
    """
    student_id = str(student_id)
    db = load_db()
    if student_id not in db:
        db[student_id] = {
            "student_id": student_id,
            "name": "",
            "green_points": 0,
            "carbon_saved_grams": 0,
            "scan_count": 0
        }

    # Update student name if provided and current name is empty
    if name and isinstance(name, dict):
        first = name.get("first", "").strip().title()
        last = name.get("last", "").strip().title()
        if first and last:
            # Only update if the current name is empty (first registration)
            if not db[student_id]["name"]:
                db[student_id]["name"] = f"{first} {last}"

    db[student_id]["green_points"] += points
    db[student_id]["carbon_saved_grams"] += carbon_saved
    db[student_id]["scan_count"] = db[student_id].get("scan_count", 0) + 1
    save_db(db)
    log_scan(student_id, points, carbon_saved, item_details)
    return db[student_id]