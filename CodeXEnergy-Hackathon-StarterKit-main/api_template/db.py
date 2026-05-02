import json
import os

DB_PATH = os.path.join("data", "users.json")

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
    return db[student_id]