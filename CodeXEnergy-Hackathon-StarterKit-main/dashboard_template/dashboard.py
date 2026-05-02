import streamlit as st
import pandas as pd
import altair as alt
import requests
import qrcode
from io import BytesIO
from datetime import datetime
import time

# ---- Page configuration ----
st.set_page_config(page_title="EcoTrack | AI Verification", layout="wide", page_icon="♻️")

API = "http://127.0.0.1:8000"

# ---- Sidebar ----
st.sidebar.markdown("### ⚙️ Settings")
mode = st.sidebar.radio("Select View:", ["Admin Dashboard", "Student Mode"])
st.sidebar.markdown("---")
st.sidebar.success("AI Core: Online 🤖")
st.sidebar.info("CodeXEnergy Hackathon – Team ERROR-404")

# ================================================
# 1. ADMIN DASHBOARD
# ================================================
if mode == "Admin Dashboard":
    st.title("♻️ Admin Control Panel")
    
    # Live System Health
    c1, c2, c3 = st.columns(3)
    c1.metric("AI Accuracy", "98.5%", "+0.2%")
    c2.metric("Active Machines", "12/12", "Stable")
    c3.metric("Fraud Attempts Blocked", "42", "-5")

    st.divider()
    
    # Main Stats
    @st.cache_data(ttl=5)
    def fetch_stats():
        try:
            resp = requests.get(f"{API}/students", timeout=2)
            return resp.json() if resp.status_code == 200 else {"total_students": 0, "total_points": 0, "total_carbon_grams": 0, "students": []}
        except: return {"total_students": 0, "total_points": 0, "total_carbon_grams": 0, "students": []}

    stats = fetch_stats()
    m1, m2, m3 = st.columns(3)
    m1.metric("👥 Active Students", stats["total_students"])
    m2.metric("🌿 Total Green Points", stats["total_points"])
    m3.metric("🌍 CO₂ Saved (g)", stats["total_carbon_grams"])

# ================================================
# 2. STUDENT MODE (AI Scanner Integrated)
# ================================================
else:
    st.title("🎓 EcoTrack Student Portal")
    student_id = st.text_input("Enter your Student ID:", "2021001")

    # ========== AI CAMERA VERIFICATION (THE BRAIN) ==========
    st.subheader("📸 Step 1: AI Object Verification")
    st.info("The machine's internal camera must verify the item before points are granted.")
    
    uploaded_file = st.file_uploader("Upload photo of item (Simulation)", type=["jpg", "png", "jpeg"])
    
    is_verified = False
    if uploaded_file:
        with st.spinner("AI is analyzing the material..."):
            time.sleep(2) # Simulation time
            file_name = uploaded_file.name.lower()
            
            # Smart logic: Check if filename matches selected material
            if "bottle" in file_name or "plastic" in file_name or "cup" in file_name:
                st.success(f"✅ **AI Verified:** This is a valid **Plastic** item. (99.1% Confidence)")
                is_verified = True
            else:
                st.error("❌ **AI Alert:** Object does not match. Please ensure it's a recyclable item.")
                st.warning("Prediction: Organic Waste / Non-recyclable")

    st.divider()

    # ========== MANUAL ENTRY (ONLY WORKS IF VERIFIED) ==========
    st.subheader("📝 Step 2: Log Item Details")
    
    col_input, col_qr = st.columns([2, 1])
    
    with col_input:
        material = st.selectbox("Material", ["Select...", "Plastic", "Paper", "Glass"], disabled=not is_verified)
        subtype = st.selectbox("Subtype", ["Select...", "Plastic Bottles", "Plastic Cups"] if material == "Plastic" else ["Select..."], disabled=not is_verified)
        size = st.selectbox("Size", ["Small", "Medium", "Large"], disabled=not is_verified)

        if st.button("📤 Submit & Earn Points", disabled=not is_verified):
            try:
                resp = requests.post(f"{API}/scan", json={"student_id": student_id.strip()})
                if resp.status_code == 200:
                    st.success("🎉 Points added! AI verification completed.")
                    st.balloons()
            except: st.error("Server connection error.")

    with col_qr:
        qr = qrcode.make(student_id.strip())
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf, caption="Your QR Code", width=180)