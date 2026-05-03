# Smart Recycling – How to Run

## 1. Start the Backend Server
Open a terminal in the project root (`ERROR-404`) and run:

cd Smart_Recycling\api_template
..\..\.venv\Scripts\activate
uvicorn app:app --reload --port 8000

The server is now running at: http://127.0.0.1:8000/docs

## 2. Start the Dashboard (Frontend)
In a second terminal, from the project root (`ERROR-404`):

.venv\Scripts\activate
streamlit run Smart_Recycling\dashboard_template\dashboard.py

Or navigate inside and run:

cd Smart_Recycling
..\.venv\Scripts\activate
streamlit run dashboard_template\dashboard.py

The dashboard will open automatically at: http://localhost:8501

## 3. Using the System
- Choose **Recycle Page** (Student Mode) and enter a Student ID.
- Upload a photo of any recyclable item – the AI will identify the material.
- Fill in the details (Material, Subtype, Size) and click **Submit & Earn Points**.
- Switch to **Dashboard** to view live campus‑wide statistics.
- Go to **Student Profile** to see your carbon footprint, points, and rewards.

## Note
- The virtual environment (`.venv`) is located in `ERROR-404`, one level above `Smart_Recycling`.
- Make sure all required packages are installed (`fastapi`, `uvicorn`, `streamlit`, `pandas`, `altair`, `requests`, `qrcode[pil]`, `Pillow`).