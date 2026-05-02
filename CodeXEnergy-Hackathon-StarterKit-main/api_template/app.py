from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

# Import our custom database functions
from db import add_green_points, get_user

app = FastAPI(
    title="EcoTrack API - CodeXEnergy Hackathon",
    description="API for QR-based green points tracking and carbon footprint reduction",
)

# -------------------------------
# Starter Kit Data Loading (kept unchanged for reference)
# -------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "datasets", "4_smart_grid", "smart_grid_dataset.csv")

try:
    df = pd.read_csv(DATA_PATH)
except Exception as e:
    print(f"Failed to load dataset: {e}")
    df = pd.DataFrame()

# -------------------------------
# Root & Data Endpoints (unchanged)
# -------------------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to the EcoTrack API! Scan a QR code to earn green points."}

@app.get("/data")
def get_data(limit: int = 10, skip: int = 0):
    if df.empty:
        raise HTTPException(status_code=500, detail="Data could not be loaded.")
    subset = df.iloc[skip : skip + limit]
    return subset.to_dict(orient="records")

@app.get("/data/summary")
def get_data_summary():
    if df.empty:
        raise HTTPException(status_code=500, detail="Data could not be loaded.")
    return df.describe().to_dict()

# -------------------------------
# ✅ NEW: QR Scan Endpoint (Task 1 & 2 Combined)
# -------------------------------

# Define the expected request body for the scan
class ScanRequest(BaseModel):
    student_id: str
    # Optional: you can add more fields like "item_type" later

@app.post("/scan")
def scan_qr(request: ScanRequest):
    """
    Called when a student scans their QR code at a recycling station.
    Adds 10 green points and 80g of CO₂ saved to the student's profile.
    Returns the updated profile.
    """
    student_id = request.student_id.strip()

    if not student_id:
        raise HTTPException(status_code=400, detail="Student ID cannot be empty.")

    # Call our db.py function to add points and create user if needed
    updated_user = add_green_points(student_id, points=10, carbon_saved=80)

    return {
        "message": f"Points added successfully for student {student_id}",
        "student": updated_user
    }

# -------------------------------
# 🔍 Get Student Profile Endpoint (Task 3 – for Wael's dashboard)
# -------------------------------
@app.get("/student/{student_id}")
def get_student_profile(student_id: str):
    """
    Retrieve a single student's green points and carbon saved.
    """
    user = get_user(student_id.strip())
    if not user:
        raise HTTPException(status_code=404, detail="Student not found.")
    return user

# -------------------------------
# Server Runner
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)