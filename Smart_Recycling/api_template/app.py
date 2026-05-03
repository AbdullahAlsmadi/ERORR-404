from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import os
from db import (
    add_green_points,
    get_user,
    load_db,
    get_recent_scans,
    get_student_scans,
    redeem_item,
    get_redemptions
)

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

# ---- QR Scan ----
class ScanRequest(BaseModel):
    student_id: str
    item_details: dict = None
    name: Optional[dict] = None   # Fix for 422 error

@app.post("/scan")
def scan_qr(req: ScanRequest):
    sid = req.student_id.strip()
    if not sid:
        raise HTTPException(status_code=400, detail="Student ID empty.")
    updated = add_green_points(
        sid,
        item_details=req.item_details,
        name=req.name
    )
    return {"message": f"Points added for {sid}", "student": updated}

# ---- Student profile ----
@app.get("/student/{student_id}")
def student_profile(student_id: str):
    sid = student_id.strip()
    user = get_user(sid)
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    recent_ops = get_student_scans(sid, limit=5)
    return {
        **user,
        "recent_scans": recent_ops
    }

# ---- Admin stats ----
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

# ---- Recent scans ----
@app.get("/scans")
def recent_scans(limit: int = 10):
    return get_recent_scans(limit)

# ==================== REWARDS ====================

class RedeemRequest(BaseModel):
    student_id: str
    reward_name: str
    cost: int

@app.post("/redeem")
def redeem(req: RedeemRequest):
    code, result = redeem_item(
        req.student_id.strip(),
        req.reward_name,
        req.cost
    )
    if code is None:
        raise HTTPException(status_code=400, detail=result)
    return {"code": code, "new_points": result}

@app.get("/redemptions/{student_id}")
def get_student_redemptions(student_id: str):
    return get_redemptions(student_id.strip())

# ---- Server runner ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)