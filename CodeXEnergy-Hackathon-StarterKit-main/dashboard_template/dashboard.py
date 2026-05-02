import streamlit as st
import pandas as pd
import altair as alt
import requests
import qrcode
from io import BytesIO

# ---- Page configuration ----
st.set_page_config(page_title="EcoTrack | ERROR-404", layout="wide", page_icon="♻️")

API = "http://127.0.0.1:8000"

# ---- Sidebar for view selection ----
mode = st.sidebar.radio("Select View:", ["Admin Dashboard", "Student Mode"])
st.sidebar.markdown("---")
st.sidebar.success("Server Status: Connected 🟢")
st.sidebar.info("CodeXEnergy Hackathon – Team ERROR-404")

# ================================================
# 1. ADMIN DASHBOARD (Live data from API)
# ================================================
if mode == "Admin Dashboard":
    st.title("♻️ Green Points System – Smart Campus Management")
    st.markdown("The following data is **live** from the EcoTrack server.")

    # ---- Fetch statistics from the server ----
    try:
        stats = requests.get(f"{API}/students").json()
    except:
        stats = {"total_students": 0, "total_points": 0, "total_carbon_grams": 0, "students": []}

    # ---- Key metrics ----
    st.subheader("Overall Performance")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="Active Students", value=stats["total_students"])
    m2.metric(label="Total Green Points Awarded", value=stats["total_points"])
    m3.metric(label="Total CO₂ Saved (g)", value=stats["total_carbon_grams"])
    m4.metric(label="Total Items Recycled", value="...")  # Placeholder for future use

    st.divider()

    # ---- Donut chart (currently with dummy data) ----
    col_left, col_right = st.columns([1, 1.5])
    with col_left:
        st.subheader("Waste Distribution")
        source = pd.DataFrame({
            "Category": ["Plastic", "Paper", "Glass"],
            "Value": [55, 30, 15]
        })
        chart = alt.Chart(source).mark_arc(innerRadius=60).encode(
            theta=alt.Theta(field="Value", type="quantitative"),
            color=alt.Color(field="Category", type="nominal",
                            scale=alt.Scale(range=['#0068c9', '#83c9ff', '#29b09d'])),
            tooltip=["Category", "Value"]
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
        st.info("💡 Most recycling occurs in the **Plastic** category.")

    # ---- Live feed of recent scans ----
    with col_right:
        st.subheader("Recent Scans (Live Feed)")
        try:
            scans = requests.get(f"{API}/scans?limit=10").json()
            if scans:
                df_scans = pd.DataFrame(scans)
                st.dataframe(df_scans, use_container_width=True, hide_index=True)
            else:
                st.info("No recycling scans yet.")
        except:
            st.warning("Could not connect to the server.")

# ================================================
# 2. STUDENT MODE (Profile card + QR Code)
# ================================================
else:
    st.title("My Green Card – EcoTrack")
    student_id = st.text_input("Enter your Student ID:", "2021001")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("View My Card"):
            try:
                resp = requests.get(f"{API}/student/{student_id.strip()}")
                if resp.status_code == 200:
                    user = resp.json()
                    st.success(f"Welcome, {user.get('name') or student_id}!")
                    st.metric("My Points", user["green_points"])
                    st.metric("CO₂ I Saved", f"{user['carbon_saved_grams']} g")
                else:
                    st.warning("No recycling record yet. Your starting points are 0.")
            except:
                st.error("Make sure the server is running.")

    with col2:
        # Generate QR code from student ID
        qr = qrcode.make(student_id.strip())
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf, caption="Your Personal Recycling QR Code", width=250)
        st.caption("Show this code at the recycling station to earn points.")

    # ---- Simulate a scan (for testing) ----
    st.divider()
    st.subheader("Test: Simulate a Recycling Scan")
    if st.button("♻️ Scan QR Now (Add Points)"):
        try:
            resp = requests.post(f"{API}/scan", json={"student_id": student_id.strip()})
            if resp.status_code == 200:
                data = resp.json()
                st.success(f"✅ Points added! Your new balance: {data['student']['green_points']} points")
                st.balloons()
            else:
                st.error("Failed to add points. Check the server.")
        except:
            st.error("Could not connect to the server.")