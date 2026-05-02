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

# ---- Auto-refresh كل 3 ثواني ----
if mode == "Admin Dashboard":
    refresh_rate = st.sidebar.slider("Auto-refresh (seconds)", 2, 10, 5)
    placeholder = st.empty()

    while True:
        with placeholder.container():
            st.title("♻️ Green Points System – Smart Campus Management")
            st.markdown("The following data is **live** from the EcoTrack server.")

            # ---- جيب البيانات من الـ API ----
            try:
                stats = requests.get(f"{API}/students").json()
            except:
                stats = {"total_students": 0, "total_points": 0, "total_carbon_grams": 0, "students": []}

            # ---- الأرقام الرئيسية ----
            st.subheader("📊 Overall Performance")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(label="🎓 Active Students", value=stats["total_students"])
            m2.metric(label="🌿 Total Green Points", value=stats["total_points"])
            m3.metric(label="🌍 CO₂ Saved (g)", value=stats["total_carbon_grams"])
            m4.metric(label="♻️ Total Scans", value=len(requests.get(f"{API}/scans?limit=1000").json()) if True else 0)

            st.divider()

            col_left, col_right = st.columns([1, 1.5])

            with col_left:
                st.subheader("📈 Waste Distribution")
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

            with col_right:
                st.subheader("🔴 Live Scan Feed")
                try:
                    scans = requests.get(f"{API}/scans?limit=10").json()
                    if scans:
                        df_scans = pd.DataFrame(scans)
                        st.dataframe(df_scans, use_container_width=True, hide_index=True)
                    else:
                        st.info("No recycling scans yet.")
                except:
                    st.warning("Could not connect to the server.")

            # ---- Leaderboard ----
            st.divider()
            st.subheader("🏆 Top Students Leaderboard")
            try:
                leaders = requests.get(f"{API}/leaderboard").json()
                if leaders:
                    df_lead = pd.DataFrame(leaders)
                    df_lead.index = df_lead.index + 1  # ابدأ من 1
                    st.dataframe(df_lead, use_container_width=True)
                else:
                    st.info("No data yet.")
            except:
                st.warning("Could not load leaderboard.")

            # ---- عداد التحديث التالي ----
            st.caption(f"⏱️ Auto-refreshing every {refresh_rate} seconds...")

        time.sleep(refresh_rate)

# ================================================
# 2. STUDENT MODE
# ================================================
else:
    st.title("🎓 My Green Card – EcoTrack")
    student_id = st.text_input("Enter your Student ID:", "2021001")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("View My Card"):
            try:
                resp = requests.get(f"{API}/student/{student_id.strip()}")
                if resp.status_code == 200:
                    user = resp.json()
                    st.success(f"Welcome, {user.get('name') or student_id}!")
                    st.metric("🌿 My Points", user["green_points"])
                    st.metric("🌍 CO₂ I Saved", f"{user['carbon_saved_grams']} g")
                else:
                    st.warning("No recycling record yet. Your starting points are 0.")
            except:
                st.error("Make sure the server is running.")

    with col2:
        qr = qrcode.make(student_id.strip())
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf, caption="Your Personal Recycling QR Code", width=250)
        st.caption("Show this code at the recycling station to earn points.")

    st.divider()
    st.subheader("♻️ Simulate a Recycling Scan")

    waste_type = st.selectbox("Select Waste Type:", ["plastic", "paper", "glass"])

    if st.button("♻️ Scan QR Now (Add Points)"):
        try:
            resp = requests.post(f"{API}/scan", json={
                "student_id": student_id.strip(),
                "waste_type": waste_type
            })
            if resp.status_code == 200:
                data = resp.json()
                st.success(f"✅ Points added! Your new balance: {data['student']['green_points']} points")
                st.balloons()
            else:
                st.error("Failed to add points.")
        except:
            st.error("Could not connect to the server.")