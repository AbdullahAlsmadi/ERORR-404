# ♻️ Smart Recycling – Gamified Campus Carbon Reduction

**Smart Recycling** is an intelligent campus recycling system that rewards students with **green points** for every recyclable item they collect. Each student scans a personal QR code, the system verifies the material using AI, and instantly calculates the environmental impact – the amount of CO₂, crude oil, and electricity saved. Earned points can be redeemed for real rewards (coffee, meals, and merchandise) at the campus canteen.

> **🏆 Hackathon Project – Team ERROR-404**  
> *CodeXEnergy 2026 · Düzce University*

---

## 🌟 Key Features

- **♻️ Gamified Recycling** – Students earn points by recycling; top performers are displayed on a live leaderboard.
- **🤖 AI Material Verification** – An uploaded photo is analyzed to detect the material (Plastic, Paper, or Glass) before points are awarded.
- **📊 Live Environmental Impact** – See exactly how much CO₂, crude oil, and electricity have been saved – both for an individual student and campus‑wide.
- **🎁 Rewards Store** – Points can be exchanged for actual campus items. Each redemption generates a unique QR code for the cashier.
- **📈 Future Projections** – Based on a student's current recycling rate, the system predicts their monthly and yearly carbon savings.
- **🧑‍💼 Admin Dashboard** – Real‑time statistics, a waste distribution chart, a live scan feed, top recyclers, and a full student registry.

---

## 🧱 Architecture

| Layer        | Technology                                     |
|--------------|------------------------------------------------|
| **Frontend** | [Streamlit](https://streamlit.io/) (Python)    |
| **Backend**  | [FastAPI](https://fastapi.tiangolo.com/)       |
| **Data Storage** | JSON files (`users.json`, `scans.json`, etc.) |
| **AI Simulation** | Pillow – Average RGB color heuristics          |
| **Charts**   | Altair + Pandas                                |
| **QR Codes** | `qrcode` library                               |

The backend provides a REST API that the Streamlit frontend consumes. The data layer is fully isolated, making it easy to switch to SQLite or PostgreSQL in the future.

---

## 📸 How It Works (Student Flow)

1. **Enter Student ID** – first‑time users also register their first and last name.
2. **Upload a photo** of the recyclable item.
3. **AI analyzes the image** – detects the material (Plastic / Paper / Glass) and shows a confidence score.
4. **Choose details** (subtype, size) and press **Submit**.
5. **Instant impact** – points are added, and carbon/oil/electricity savings are updated immediately.
6. **Redeem points** in the **Student Profile** page – a unique QR code is generated for the cashier.

---

## 📊 Admin Dashboard

- **Metrics**: total students, total points, total CO₂ saved.
- **Dynamic Donut Chart**: real‑time waste distribution (Plastic, Paper, Glass).
- **Live Feed**: recent scans, filterable by material.
- **Top Carbon Savers**: bar chart with the top 10 students.
- **Full Student Table**: every registered student with their points, scan count, and carbon savings.

---

## 📁 Project Structure


ERROR-404/
├── Smart_Recycling/
│ ├── api_template/ # FastAPI backend
│ │ ├── app.py # API endpoints
│ │ ├── db.py # Data handling (users, scans, redemptions)
│ │ └── data/ # JSON database files (auto‑created)
│ ├── dashboard_template/ # Streamlit frontend
│ │ └── dashboard.py
│ └── datasets/ # Optional starter‑kit data
├── .venv/ # Virtual environment (not tracked)
├── .gitignore
├── README.md
└── HOW-USING.md # Quick start guide


---

## 🚀 How to Run

```bash
1. Clone the repository

git clone https://github.com/AbdulhalAlsamadi/ERROR-404.git
cd ERROR-404
python -m venv .venv

2. Create and activate a virtual environment
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

3. Install the dependencies
pip install fastapi uvicorn pandas streamlit requests qrcode[pil] pillow altair

4. Start the backend server
cd Smart_Recycling\api_template
..\..\.venv\Scripts\activate
uvicorn app:app --reload --port 8000

The API documentation will be available at: http://127.0.0.1:8000/docs

5. Start the frontend dashboard
Open a second terminal, activate the virtual environment, then run:

cd Smart_Recycling
..\.venv\Scripts\activate
streamlit run dashboard_template\dashboard.py

The dashboard will open automatically at: http://localhost:8501

```
---

## 🔢 Real‑World Impact Calculations
Points and carbon savings are calculated dynamically based on the material, subtype, and size of each recycled item.

|   Item              |CO₂ Saved|Points|
|---------------------|---------|------|
|**Plastic Bottle (1.5L)**|  120 g  |	12   |
|**Notebook (A4)**        |	 500 g  |	50   |
|**Glass Bottle (1L)**	  |  500 g  |	50   |
|**Paper Cup (7oz)**	    |  20 g	  | 2    |


Conversions:

- Crude oil saved (litres) = CO₂ (grams) ÷ 2300

- Electricity saved (kWh) = Crude oil saved × 10

(All values can be adjusted inside db.py)

---

## 🧑‍🤝‍🧑 Team
ERROR-404

- **Abdullah Al Smadi** – Backend & API development

- **Vael Kuloglu** – Frontend & Dashboard design

Built with passion during CodeXEnergy Hackathon 2026.

---

## 📄 License
This project is licensed under the MIT License.
