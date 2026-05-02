import json
import os
import datetime
import uuid

DB_PATH = os.path.join("data", "users.json")
SCANS_PATH = os.path.join("data", "scans.json")
REDEMPTIONS_PATH = os.path.join("data", "redemptions.json")

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

def get_impact_from_item(item_details):
    """
    Return (carbon_saved_grams, points) based on material, subtype and size.
    Uses realistic estimates for each recyclable item.
    """
    if not item_details or not isinstance(item_details, dict):
        return 80, 10  # default fallback

    material = item_details.get("material", "").strip().lower()
    subtype = item_details.get("subtype", "").strip().lower()
    size = item_details.get("size", "").strip().lower()

    # Mapping: (material, subtype, size) -> (carbon_g, points)
    mapping = {
        ("plastic", "plastic bottles", "1.5 l"): (120, 12),
        ("plastic", "plastic bottles", "1 l"): (80, 8),
        ("plastic", "plastic cups", "7 oz"): (30, 3),
        ("plastic", "plastic cups", "8 oz"): (30, 3),
        ("plastic", "plastic cups", "12 oz"): (30, 3),
        ("paper", "notebook", "a4"): (500, 50),
        ("paper", "notebook", "a5"): (300, 30),
        ("paper", "carton", "small"): (150, 15),
        ("paper", "carton", "medium"): (250, 25),
        ("paper", "carton", "large"): (400, 40),
        ("paper", "paper cups", "7 oz"): (20, 2),
        ("paper", "paper cups", "8 oz"): (20, 2),
        ("paper", "paper cups", "12 oz"): (20, 2),
        ("glass", "glass bottles", "330 ml"): (200, 20),
        ("glass", "glass bottles", "500 ml"): (300, 30),
        ("glass", "glass bottles", "1 l"): (500, 50),
    }

    key = (material, subtype, size)
    if key in mapping:
        return mapping[key]

    # Fallback: approximate by material if exact match not found
    if material == "plastic":
        return 80, 10
    elif material == "paper":
        return 100, 10
    elif material == "glass":
        return 150, 15
    return 80, 10

def add_green_points(student_id, points=10, carbon_saved=80, item_details=None, name=None):
    """
    Add green points and carbon saved for a student.
    Creates a new profile if student doesn't exist.
    Optionally updates the student's name if provided and currently empty.
    If item_details is provided, carbon_saved and points are calculated
    from real-world impact values, ignoring the defaults.
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
            if not db[student_id]["name"]:
                db[student_id]["name"] = f"{first} {last}"

    # Override points and carbon if item_details is available
    if item_details:
        carbon_saved, points = get_impact_from_item(item_details)

    db[student_id]["green_points"] += points
    db[student_id]["carbon_saved_grams"] += carbon_saved
    db[student_id]["scan_count"] = db[student_id].get("scan_count", 0) + 1
    save_db(db)
    log_scan(student_id, points, carbon_saved, item_details)
    return db[student_id]

# ==================== REWARDS SYSTEM ====================

def redeem_item(student_id, reward_name, cost):
    """
    Deduct points and record a redemption.
    Returns (code, new_points) or (None, error_message).
    """
    student_id = str(student_id)
    db = load_db()
    if student_id not in db:
        return None, "Student not found"
    user = db[student_id]
    if user["green_points"] < cost:
        return None, "Insufficient points"

    # Deduct points
    user["green_points"] -= cost
    save_db(db)

    # Generate unique redemption code
    code = str(uuid.uuid4())[:8].upper()

    # Record redemption
    redemption = {
        "student_id": student_id,
        "reward_name": reward_name,
        "cost": cost,
        "code": code,
        "timestamp": datetime.datetime.now().isoformat()
    }
    redemptions = []
    if os.path.exists(REDEMPTIONS_PATH):
        with open(REDEMPTIONS_PATH, "r") as f:
            redemptions = json.load(f)
    redemptions.append(redemption)
    with open(REDEMPTIONS_PATH, "w") as f:
        json.dump(redemptions, f, indent=4)

    return code, user["green_points"]

def get_redemptions(student_id):
    """Retrieve redemption history for a specific student."""
    if not os.path.exists(REDEMPTIONS_PATH):
        return []
    with open(REDEMPTIONS_PATH, "r") as f:
        all_red = json.load(f)
    return [r for r in all_red if str(r.get("student_id")) == str(student_id)]