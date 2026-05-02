# EcoTrack – How to Run

## 1. Start the Backend Server
Open a terminal in the project folder and run:

cd CodeXEnergy-Hackathon-StarterKit-main\api_template
..\..\..\.venv\Scripts\activate   # or .venv\Scripts\activate if you are in the root
uvicorn app:app --reload --port 8000

The server is now running at: http://127.0.0.1:8000/docs

## 2. Start the Dashboard (Frontend)
In another terminal:

cd CodeXEnergy-Hackathon-StarterKit-main
..\..\..\.venv\Scripts\activate   # or .venv\Scripts\activate
python -m streamlit run dashboard_template\dashboard.py or
python -m streamlit run CodeXEnergy-Hackathon-StarterKit-main\dashboard_template\dashboard.py
The browser will open automatically at: http://localhost:8501

## 3. Using the System
- Choose **Student Mode** and enter a Student ID.
- Upload a photo of any item to be identified.
- Complete the details and click **Submit & Earn Points**.
- Switch to **Admin Dashboard** to view live statistics.