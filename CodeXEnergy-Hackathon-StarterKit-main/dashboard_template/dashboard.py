import streamlit as st
import pandas as pd
import altair as alt
import requests
import qrcode
from io import BytesIO
import time

# ---- Page configuration ----
st.set_page_config(page_title="EcoTrack | ERROR-404", layout="wide", page_icon="♻️")

API = "http://127.0.0.1:8000"

# ---- Sidebar ----
mode = st.sidebar.radio("Select View:", ["Admin Dashboard", "Student Mode"])
st.sidebar.markdown("---")
st.sidebar.success("Server Status: Connected 🟢")
st.sidebar.info("CodeXEnergy Hackathon – Team ERROR-404")

# ================================================
# 1. ADMIN DASHBOARD
# ================================================
if mode == "Admin Dashboard":
    refresh_rate = st.sidebar.slider("Auto-refresh (seconds)", 2, 10, 3)
    placeholder = st.empty()

    while True:
        with placeholder.container():
            st.title("♻️ Green Points System – Smart Campus Management")
            st.markdown("The following data is **live** from the EcoTrack server.")

            # ---- جيب البيانات من الـ API بأمان ----
            try:
                stats = requests.get(f"{API}/students", timeout=2).json()
            except:
                stats = {"total_students": 0, "total_points": 0, "total_carbon_grams": 0, "students": []}

            try:
                all_scans = requests.get(f"{API}/scans?limit=1000", timeout=2).json()
                total_scans = len(all_scans)
            except:
                all_scans = []
                total_scans = 0

            # ---- الأرقام الرئيسية ----
            st.subheader("📊 Overall Performance")
            m1, m2, m3, m4 = st.columns(4)