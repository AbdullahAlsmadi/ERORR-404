from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
from db import add_green_points, get_user, load_db, get_recent_scans

app = FastAPI(
    title="EcoTrack API - ERROR-404",
    description="QR-based Green Points & Carbon Tracking",
)

# ---- Optional Starter Kit dataset loading ----
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "datasets", "4_smart_grid", "smart_grid_dataset.csv")
try:
    df = pd.read_csv(DATA_PATH)
except Exception as e:
    print(f"Dataset error: {e}")
    df = pd.DataFrame()

@app.get("/")
def root():
    return {"message": "Welcome to EcoTrack API. POST /scan to earn points."}

@app.get("/data")
def get_data(limit=10, skip=0):
    if df.empty:
        raise HTTPException(status_code=500, detail="Data not loaded.")
    return df.iloc[skip:skip+limit].to_dict(orient="records")

@app.get("/data/summary")
def summary():
    if df.empty:
        raise HTTPException(status_code=500, detail="Data not loaded.")
    return df.describe().to_dict()

# ---- QR Scan (core functionality) ----
class ScanRequest(BaseModel):
    student_id: str
    item_details: dict = None   # optional field for manual entry

@app.post("/scan")
def scan_qr(req: ScanRequest):
    sid = req.student_id.strip()
    if not sid:
        raise HTTPException(status_code=400, detail="Student ID empty.")
    updated = add_green_points(sid, points=10, carbon_saved=80, item_details=req.item_details)
    return {"message": f"Points added for {sid}", "student": updated}

# ---- Student profile (for Wael's dashboard) ----
@app.get("/student/{student_id}")
def student_profile(student_id: str):
    user = get_user(student_id.strip())
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    return user

# ---- General statistics for admin dashboard ----
@app.get("/students")
def get_all_students():
    db = load_db()
    total_students = len(db)
    total_points = sum(user.get("green_points", 0) for user in db.values())
    total_carbon = sum(user.get("carbon_saved_grams", 0) for user in db.values())
    return {
        "total_students": total_students,
        "total_points": total_points,
        "total_carbon_grams": total_carbon,
        "students": list(db.values())
    }

# ---- Recent scan logs ----
@app.get("/scans")
def recent_scans(limit: int = 10):
    return get_recent_scans(limit)

# ---- Server runner ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)