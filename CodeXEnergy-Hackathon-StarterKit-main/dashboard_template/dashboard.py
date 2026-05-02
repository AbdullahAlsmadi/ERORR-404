import streamlit as st
import pandas as pd
import altair as alt
import requests
import qrcode
from io import BytesIO
from datetime import datetime

# ---- Page configuration ----
st.set_page_config(page_title="EcoTrack | ERROR-404", layout="wide", page_icon="♻️")

API = "http://127.0.0.1:8000"

# ---- Sidebar ----
st.sidebar.markdown("### ⚙️ Settings")
mode = st.sidebar.radio("Select View:", ["Admin Dashboard", "Student Mode"])
st.sidebar.markdown("---")
st.sidebar.success("Server Status: Connected 🟢")
st.sidebar.info("CodeXEnergy Hackathon – Team ERROR-404")

# ================================================
# 1. ADMIN DASHBOARD
# ================================================
if mode == "Admin Dashboard":
    st.title("♻️ Green Points System – Smart Campus")
    st.markdown("The following data is **live** from the EcoTrack server.")

    # Manual refresh button
    col_refresh, col_time = st.columns([1, 3])
    with col_refresh:
        refresh = st.button("🔄 Refresh Now")
    with col_time:
        if "last_update" not in st.session_state:
            st.session_state.last_update = None
        if refresh:
            st.session_state.last_update = datetime.now().strftime("%H:%M:%S")
        if st.session_state.last_update:
            st.caption(f"Last refreshed at: {st.session_state.last_update}")

    # ---- Fetch data with caching ----
    @st.cache_data(ttl=5)
    def fetch_stats():
        try:
            resp = requests.get(f"{API}/students", timeout=2)
            if resp.status_code == 200:
                return resp.json()
            return {"total_students": 0, "total_points": 0, "total_carbon_grams": 0, "students": []}
        except:
            return {"total_students": 0, "total_points": 0, "total_carbon_grams": 0, "students": []}

    @st.cache_data(ttl=5)
    def fetch_scans():
        try:
            resp = requests.get(f"{API}/scans?limit=1000", timeout=2)
            if resp.status_code == 200:
                return resp.json()
            return []
        except:
            return []

    stats = fetch_stats()
    scans = fetch_scans()
    total_scans = len(scans)

    # ---- Key metrics ----
    st.subheader("📊 Overall Performance")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👥 Active Students", stats["total_students"])
    m2.metric("🌿 Total Green Points", stats["total_points"])
    m3.metric("🌍 CO₂ Saved (g)", stats["total_carbon_grams"])
    m4.metric("♻️ Total Scans", total_scans)

    st.divider()

    # ---- Donut chart & Leaderboard ----
    col_left, col_right = st.columns([1, 1.5])
    
    with col_left:
        st.subheader("📈 Waste Distribution")
        plastic_val = 55 + (total_scans * 2)
        paper_val = 30 + total_scans
        glass_val = 15 + int(total_scans * 0.5)
        
        source = pd.DataFrame({
            "Category": ["Plastic", "Paper", "Glass"],
            "Value": [plastic_val, paper_val, glass_val]
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
        st.subheader("📋 Recent Scans (Live Feed)")
        if scans:
            df_scans = pd.DataFrame(scans)
            if 'timestamp' in df_scans.columns:
                df_scans = df_scans.sort_values(by='timestamp', ascending=False).head(5)
            st.dataframe(df_scans, use_container_width=True, hide_index=True)
        else:
            st.info("No recycling scans yet.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.subheader("🏆 Top Recyclers")
        students_list = stats.get("students", [])
        if students_list:
            top_students = sorted(students_list, key=lambda x: x.get('green_points', 0), reverse=True)[:3]
            df_top = pd.DataFrame(top_students)
            st.dataframe(df_top[['student_id', 'name', 'green_points']], use_container_width=True, hide_index=True)
        else:
            st.warning("Waiting for students to start recycling!")

# ================================================
# 2. STUDENT MODE (with manual entry)
# ================================================
else:
    st.title("🎓 My Green Card")
    student_id = st.text_input("Enter your Student ID:", "2021001")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 View My Card"):
            try:
                resp = requests.get(f"{API}/student/{student_id.strip()}")
                if resp.status_code == 200:
                    user = resp.json()
                    pts = user["green_points"]
                    
                    if pts < 50:
                        badge = "🌱 Eco-Apprentice"
                    elif pts < 150:
                        badge = "🌳 Nature Friend"
                    else:
                        badge = "👑 Eco-Hero"

                    st.success(f"Welcome, {user.get('name') or student_id}!")
                    st.markdown(f"**Current Rank:** {badge}")
                    
                    m1, m2 = st.columns(2)
                    m1.metric("🌿 My Points", pts)
                    m2.metric("🌍 CO₂ Saved (g)", user["carbon_saved_grams"])
                    
                    st.markdown("---")
                    st.markdown("**☕ Free Campus Coffee Goal:**")
                    goal = 100
                    progress_val = min(pts / goal, 1.0)
                    st.progress(progress_val)
                    
                    if pts < goal:
                        st.caption(f"You need **{goal - pts}** more points for a free coffee!")
                    else:
                        st.caption("🎉 Congratulations! You have enough points for a free coffee!")

                else:
                    st.warning("No recycling record yet. Your starting points are 0.")
            except:
                st.error("Could not connect to the server. Make sure the backend is running.")

    with col2:
        qr = qrcode.make(student_id.strip())
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf, caption="Your Personal Recycling QR Code", width=250)
        st.caption("Show this code at the recycling station to earn points.")

    st.divider()

    # ========== 🆕 MANUAL RECYCLING ENTRY ==========
    st.subheader("📝 Manual Recycling Entry (Demo)")
    st.markdown("Because you don’t have a physical QR scanner, you can manually log your recycling here.")

    # Material selection
    material = st.selectbox("Material", ["Select...", "Plastic", "Paper", "Glass"])

    subtype = None
    size = None

    if material != "Select...":
        if material == "Plastic":
            subtype = st.selectbox("Subtype", ["Select...", "Plastic Bottles", "Plastic Cups"])
        elif material == "Paper":
            subtype = st.selectbox("Subtype", ["Select...", "Notebook", "Carton", "Paper Cups"])
        elif material == "Glass":
            subtype = st.selectbox("Subtype", ["Select...", "Glass Bottles"])

        if subtype and subtype != "Select...":
            if subtype == "Plastic Bottles":
                size = st.selectbox("Size", ["1.5 L", "1 L"])
            elif subtype == "Plastic Cups":
                size = st.selectbox("Size", ["7 oz", "8 oz", "12 oz"])
            elif subtype == "Paper Cups":
                size = st.selectbox("Size", ["7 oz", "8 oz", "12 oz"])
            elif subtype == "Notebook":
                size = st.selectbox("Size", ["A4", "A5"])
            elif subtype == "Carton":
                size = st.selectbox("Size", ["Small", "Medium", "Large"])
            elif subtype == "Glass Bottles":
                size = st.selectbox("Size", ["330 ml", "500 ml", "1 L"])

    # Submit button
    if st.button("📤 Submit Manual Scan"):
        if material == "Select..." or not subtype or subtype == "Select..." or not size:
            st.error("Please select Material, Subtype and Size before submitting.")
        else:
            item_detail = {
                "material": material,
                "subtype": subtype,
                "size": size
            }
            try:
                resp = requests.post(f"{API}/scan", json={
                    "student_id": student_id.strip(),
                    "item_details": item_detail
                })
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"✅ Manual scan recorded! You earned 10 points. Total: {data['student']['green_points']} points")
                    st.balloons()
                else:
                    st.error("Failed to record manual scan. Check the server.")
            except:
                st.error("Could not connect to the server.")

    st.markdown("---")

    # ---- Simulate a QR scan (the old test) ----
    st.subheader("🔄 Test: Simulate a QR Scan")
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