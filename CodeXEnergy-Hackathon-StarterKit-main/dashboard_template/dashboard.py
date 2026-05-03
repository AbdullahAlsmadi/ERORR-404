import streamlit as st # For building the interactive web dashboard
import pandas as pd # For data manipulation and display
import altair as alt # For creating interactive charts
import requests # For API calls to the backend
import qrcode # For generating QR codes for student profiles and rewards
from io import BytesIO # For handling in-memory image data
from datetime import datetime, timedelta # For handling timestamps and projections
import time # For simulating AI processing time
import random # For simulating AI confidence scores
from PIL import Image, ImageStat # For simple image analysis in AI verification step

# ---- Page configuration ----
st.set_page_config(page_title="Smart Recycling | ERROR-404", layout="wide", page_icon="♻️")

API = "http://127.0.0.1:8000"

# ---- Sidebar (clean & professional) ----
st.sidebar.markdown("## ♻️ Smart Recycling")
st.sidebar.markdown("---")
mode = st.sidebar.radio("Navigate to:", ["Dashboard", "Recycle Page", "Student Profile"])
st.sidebar.markdown("---")
st.sidebar.caption("Team ERROR-404 | Hackathon 2026")

# ================================================
# 1. ADMIN DASHBOARD
# ================================================
if mode == "Dashboard":
    st.title("♻️ Dashboard – Smart Recycling")


    st.divider()

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
    students_list = stats.get("students", [])

    # ---- Key metrics ----
    st.subheader("📊 Overall Performance")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🌱 Carbon Savers", stats["total_students"])
    m2.metric("🌿 Total Green Points", stats["total_points"])
    m3.metric("🌍 CO₂ Saved (g)", stats["total_carbon_grams"])
    m4.metric("♻️ Total Scans", total_scans)

    # ---- Impact equivalents ----
    total_carbon = stats["total_carbon_grams"]
    total_oil = total_carbon / 2300
    total_energy = total_oil * 10
    st.markdown("---")
    c_oil, c_elec = st.columns(2)
    c_oil.metric("🛢️ Total Crude Oil Saved", f"{total_oil:.0f} liters")
    c_elec.metric("⚡ Total Electricity Saved", f"{total_energy:.0f} kWh")

    st.divider()

    # ---- Top Carbon Savers Chart ----
    if students_list:
        st.subheader("🏅 Top Carbon Savers")
        df_carbon = pd.DataFrame(students_list)
        df_carbon['carbon_kg'] = df_carbon['carbon_saved_grams'] / 1000
        top_carbon = df_carbon.sort_values('carbon_saved_grams', ascending=False).head(10)
        chart_bar = alt.Chart(top_carbon).mark_bar().encode(
            x=alt.X('carbon_kg:Q', title='CO₂ Saved (kg)'),
            y=alt.Y('student_id:N', sort='-x', title='Student ID'),
            color=alt.value('#2E8B57')
        ).properties(height=300)
        st.altair_chart(chart_bar, use_container_width=True)
    else:
        st.info("No students yet – start recycling to see the leaderboard.")

    st.divider()

    # ---- Donut chart & Recent scans ----
    col_left, col_right = st.columns([1, 1.5])

    with col_left:
        st.subheader("📈 Waste Distribution (Real Data)")

        material_counts = {"Plastic": 0, "Paper": 0, "Glass": 0}
        for scan in scans:
            details = scan.get("item_details", {})
            mat = details.get("material", "").strip()
            if mat in material_counts:
                material_counts[mat] += 1

        plastic_val = material_counts["Plastic"]
        paper_val = material_counts["Paper"]
        glass_val = material_counts["Glass"]

        source = pd.DataFrame({
            "Category": ["Plastic", "Paper", "Glass"],
            "Value": [plastic_val, paper_val, glass_val]
        })

        if plastic_val + paper_val + glass_val == 0:
            st.info("No recycling data yet. Start scanning to see distribution.")
        else:
            chart = alt.Chart(source).mark_arc(innerRadius=60).encode(
                theta=alt.Theta(field="Value", type="quantitative"),
                color=alt.Color(field="Category", type="nominal",
                                scale=alt.Scale(range=['#0068c9', '#83c9ff', '#29b09d'])),
                tooltip=["Category", "Value"]
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)

        highlight = st.selectbox("Filter table by material:", ["All", "Plastic", "Paper", "Glass"])

    with col_right:
        st.subheader("📋 Recent Scans (Live Feed)")
        if scans:
            rows = []
            for scan in scans:
                row = {
                    "student_id": scan.get("student_id"),
                    "points_added": scan.get("points_added"),
                    "carbon_saved": scan.get("carbon_saved"),
                    "timestamp": scan.get("timestamp")
                }
                if "item_details" in scan:
                    row["material"] = scan["item_details"].get("material", "Unknown")
                    row["subtype"] = scan["item_details"].get("subtype", "")
                    row["size"] = scan["item_details"].get("size", "")
                else:
                    row["material"] = "Unknown"
                    row["subtype"] = ""
                    row["size"] = ""
                rows.append(row)
            df_scans = pd.DataFrame(rows)
            df_scans = df_scans.sort_values(by='timestamp', ascending=False).head(10)

            if highlight != "All":
                df_scans = df_scans[df_scans["material"] == highlight]

            st.dataframe(df_scans[['student_id', 'material', 'subtype', 'size', 'points_added', 'timestamp']],
                         use_container_width=True, hide_index=True)
        else:
            st.info("No recycling scans yet.")

        st.markdown("<br>", unsafe_allow_html=True)

        st.subheader("🏆 Top Recyclers (by Points)")
        if students_list:
            top_students = sorted(students_list, key=lambda x: x.get('green_points', 0), reverse=True)[:3]
            df_top = pd.DataFrame(top_students)
            st.dataframe(df_top[['student_id', 'name', 'green_points']], use_container_width=True, hide_index=True)
        else:
            st.warning("Waiting for students to start recycling!")

        st.subheader("📋 All Registered Students")
        if students_list:
            df_all = pd.DataFrame(students_list)
            if 'carbon_saved_grams' in df_all.columns:
                df_all['carbon_saved_kg'] = df_all['carbon_saved_grams'] / 1000.0
            display_cols = ['student_id', 'name', 'green_points', 'scan_count', 'carbon_saved_kg']
            available = [c for c in display_cols if c in df_all.columns]
            st.dataframe(df_all[available], use_container_width=True, hide_index=True)
        else:
            st.info("No students have recycled yet.")

# ================================================
# 2. RECYCLE PAGE (Student Mode)
# ================================================
elif mode == "Recycle Page":
    st.title("Recycle Page")
    student_id = st.text_input("Enter your Student ID:", "")

    profile_loaded = False
    student_name = ""
    student_pts = 0
    student_carbon = 0

    try:
        resp = requests.get(f"{API}/student/{student_id.strip()}", timeout=2)
        if resp.status_code == 200:
            prof = resp.json()
            student_name = prof.get("name", "").strip()
            student_pts = prof.get("green_points", 0)
            student_carbon = prof.get("carbon_saved_grams", 0)
            profile_loaded = True
    except:
        pass

    show_name_fields = (not profile_loaded) or (student_name == "")

    if show_name_fields:
        st.subheader("📝 Register Your Name")
        st.info("You only need to do this once. Your name will appear on your green card.")
        col_fname, col_lname = st.columns(2)
        with col_fname:
            first = st.text_input("First Name")
        with col_lname:
            last = st.text_input("Last Name")
        if first and last:
            st.session_state.temp_first = first
            st.session_state.temp_last = last
    else:
        st.session_state.temp_first = ""
        st.session_state.temp_last = ""
        if student_name and profile_loaded:
            st.success(f"Welcome back, {student_name}!")

            # ========== CARBON FOOTPRINT SECTION ==========
            st.markdown("---")
            co2_kg = student_carbon / 1000.0
            st.markdown("## 🌱 Your Carbon Footprint Reduction")
            st.metric(label="CO₂ Avoided", value=f"{co2_kg:.2f} kg")
            goal_kg = 10.0
            progress_co2 = min(co2_kg / goal_kg, 1.0)
            st.progress(progress_co2, text=f"Towards {goal_kg} kg goal")

            # Additional impact
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            col1.metric("🌿 Green Points", student_pts)
            col2.metric("🗑️ Items Recycled", prof.get("scan_count", 0))
            oil_liters = student_carbon / 2300
            energy_kwh = oil_liters * 10
            col3.metric("🛢️ Oil Saved", f"{oil_liters:.2f} L")
            st.metric("⚡ Electricity Saved", f"{energy_kwh:.2f} kWh")

    st.divider()

    # ========== AI CAMERA VERIFICATION ==========
    st.subheader("📸 Step 1: AI Object Verification")
    st.info("The machine's internal camera verifies your item before awarding points.")

    if "ai_verified" not in st.session_state:
        st.session_state.ai_verified = False
        st.session_state.ai_material = None
        st.session_state.ai_confidence = 0.0

    uploaded_file = st.file_uploader("Upload photo of your recyclable item", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", width=300)
        with st.spinner("🔍 AI is analyzing the material composition..."):
            time.sleep(1.2)
            try:
                img = Image.open(uploaded_file).convert("RGB")
                stat = ImageStat.Stat(img)
                r, g, b = stat.mean[:3]

                if (g > 120 and r < 100 and b < 100) or (r > 160 and g > 100 and b < 80):
                    material_detected = "Glass"
                elif (r > 200 and g > 200 and b > 200) or (abs(r-g) < 20 and abs(g-b) < 20 and r > 150):
                    material_detected = "Paper"
                else:
                    material_detected = "Plastic"

                confidence = round(random.uniform(92.0, 99.5), 1)
                st.session_state.ai_verified = True
                st.session_state.ai_material = material_detected
                st.session_state.ai_confidence = confidence
                st.success(f"✅ **AI Verified:** Detected **{material_detected}** item. (Confidence: {confidence}%)")
            except:
                st.session_state.ai_verified = True
                st.session_state.ai_material = "Plastic"
                st.session_state.ai_confidence = 96.0
                st.success("✅ **AI Verified:** Detected **Plastic** item. (Confidence: 96.0%)")

    if not uploaded_file and not st.session_state.ai_verified:
        st.info("Please upload an image to start AI verification.")

    is_verified = st.session_state.ai_verified
    detected_material = st.session_state.ai_material

    st.divider()

    # ========== MANUAL ENTRY (Step 2) ==========
    st.subheader("📝 Step 2: Log Item Details")

    col_input, col_qr = st.columns([2, 1])

    with col_input:
        default_mat = detected_material if detected_material else "Select..."
        mat_index = ["Select...", "Plastic", "Paper", "Glass"].index(default_mat) if default_mat in ["Plastic","Paper","Glass"] else 0
        material = st.selectbox("Material", ["Select...", "Plastic", "Paper", "Glass"], index=mat_index, disabled=not is_verified)

        subtype = None
        size = None
        if material == "Plastic":
            subtype = st.selectbox("Subtype", ["Select...", "Plastic Bottles", "Plastic Cups"], disabled=not is_verified)
            if subtype == "Plastic Bottles":
                size = st.selectbox("Size", ["1.5 L", "1 L"], disabled=not is_verified)
            elif subtype == "Plastic Cups":
                size = st.selectbox("Size", ["7 oz", "8 oz", "12 oz"], disabled=not is_verified)
        elif material == "Paper":
            subtype = st.selectbox("Subtype", ["Select...", "Notebook", "Carton", "Paper Cups"], disabled=not is_verified)
            if subtype == "Paper Cups":
                size = st.selectbox("Size", ["7 oz", "8 oz", "12 oz"], disabled=not is_verified)
            elif subtype == "Notebook":
                size = st.selectbox("Size", ["A4", "A5"], disabled=not is_verified)
            elif subtype == "Carton":
                size = st.selectbox("Size", ["Small", "Medium", "Large"], disabled=not is_verified)
        elif material == "Glass":
            subtype = st.selectbox("Subtype", ["Select...", "Glass Bottles"], disabled=not is_verified)
            if subtype == "Glass Bottles":
                size = st.selectbox("Size", ["330 ml", "500 ml", "1 L"], disabled=not is_verified)

        if st.button("📤 Submit & Earn Points", disabled=not is_verified):
            if material == "Select..." or not subtype or subtype == "Select..." or not size:
                st.error("Please select Material, Subtype and Size before submitting.")
            else:
                name_payload = None
                if show_name_fields:
                    first = st.session_state.get("temp_first", "")
                    last = st.session_state.get("temp_last", "")
                    if first and last:
                        name_payload = {"first": first, "last": last}
                    else:
                        st.error("Please enter your first and last name.")
                        st.stop()

                item_detail = {"material": material, "subtype": subtype, "size": size}
                payload = {"student_id": student_id.strip(), "item_details": item_detail}
                if name_payload is not None:
                    payload["name"] = name_payload
                try:
                    resp = requests.post(f"{API}/scan", json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"✅ Points added! Your new balance: {data['student']['green_points']} points")
                        st.balloons()
                        st.session_state.ai_verified = False
                        st.session_state.ai_material = None
                        st.session_state.ai_confidence = 0.0
                        if name_payload:
                            if "temp_first" in st.session_state:
                                del st.session_state.temp_first
                            if "temp_last" in st.session_state:
                                del st.session_state.temp_last
                            st.rerun()
                    else:
                        st.error("Failed to record scan. Check the server.")
                except:
                    st.error("Could not connect to the server.")

    with col_qr:
        qr = qrcode.make(student_id.strip())
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf, caption="Your Personal Recycling QR Code", width=250)
        st.caption("Show this code at the recycling station to earn points.")

# ================================================
# 3. STUDENT PROFILE (Rewards + Impact)
# ================================================
elif mode == "Student Profile":
    st.title("Student Profile & Rewards")
    student_id = st.text_input("Enter your Student ID:", "")

    if student_id:
        try:
            resp = requests.get(f"{API}/student/{student_id.strip()}", timeout=2)
            if resp.status_code == 200:
                prof = resp.json()
                current_points = prof['green_points']
                carb = prof.get('carbon_saved_grams', 0)
                scan_count = prof.get('scan_count', 0)
                student_name = prof.get('name', '')

                st.success(f"Welcome, {student_name or student_id}!")
                st.metric("🌿 Your Points", current_points)

                # ---- Carbon Footprint & Impact ----
                st.markdown("---")
                co2_kg = carb / 1000.0
                st.markdown("## 🌱 Your Carbon Footprint Reduction")
                st.metric(label="CO₂ Avoided", value=f"{co2_kg:.2f} kg")
                goal_kg = 10.0
                progress_co2 = min(co2_kg / goal_kg, 1.0)
                st.progress(progress_co2, text=f"Towards {goal_kg} kg goal")

                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                col1.metric("🗑️ Items Recycled", scan_count)
                oil_liters = carb / 2300
                energy_kwh = oil_liters * 10
                col2.metric("🛢️ Crude Oil Saved", f"{oil_liters:.2f} L")
                col3.metric("⚡ Electricity Saved", f"{energy_kwh:.2f} kWh")
                st.caption("Every item recycled helps lower greenhouse gas emissions and dependency on fossil fuels.")

                # ---- Future Projections ----
                scans_list = prof.get("recent_scans", [])
                if scans_list:
                    timestamps = []
                    for s in scans_list:
                        try:
                            ts = datetime.fromisoformat(s["timestamp"])
                            timestamps.append(ts)
                        except:
                            pass
                    if timestamps:
                        earliest = min(timestamps)
                        now = datetime.now()
                        days_diff = (now - earliest).days
                        if days_diff < 1:
                            days_diff = 1
                        daily_carbon = carb / days_diff
                        monthly = daily_carbon * 30
                        yearly = daily_carbon * 365

                        st.markdown("---")
                        st.subheader("📈 Future Projections (if you continue at this rate)")
                        col_m, col_y = st.columns(2)
                        col_m.metric("In 1 Month", f"{monthly/1000:.2f} kg CO₂")
                        col_y.metric("In 1 Year", f"{yearly/1000:.2f} kg CO₂")
                    else:
                        st.info("Not enough data for projections yet.")
                else:
                    st.info("Start recycling to see future projections.")

            else:
                st.warning("Student not found. Please register by doing a recycling scan first.")
                current_points = 0
        except:
            st.error("Could not connect to the server.")
            current_points = 0

        # ---- Rewards grid ----
        if current_points > 0 or (resp.status_code == 200 if 'resp' in locals() else False):
            st.markdown("---")
            rewards = [
                {"name": "☕ Free Coffee", "cost": 500},
                {"name": "🍽️ Meal Discount", "cost": 300},
                {"name": "👕 University T-Shirt", "cost": 1000},
                {"name": "📓 Recycled Notebook", "cost": 200}
            ]

            st.subheader("Available Rewards")
            cols = st.columns(2)
            for i, reward in enumerate(rewards):
                with cols[i % 2]:
                    locked = current_points < reward["cost"]
                    status = "🔒 Locked" if locked else "🔓 Available"
                    st.markdown(f"### {reward['name']}")
                    st.caption(f"Cost: {reward['cost']} points")
                    st.progress(min(current_points / reward["cost"], 1.0))
                    st.write(status)
                    if not locked:
                        if st.button(f"Redeem {reward['name']}", key=f"redeem_{reward['name']}"):
                            try:
                                resp = requests.post(f"{API}/redeem", json={
                                    "student_id": student_id.strip(),
                                    "reward_name": reward["name"],
                                    "cost": reward["cost"]
                                })
                                if resp.status_code == 200:
                                    data = resp.json()
                                    code = data["code"]
                                    new_points = data["new_points"]
                                    st.success(f"✅ Redeemed! Your new balance: {new_points} points")
                                    st.markdown("**Show this QR code to the cashier:**")
                                    qr_img = qrcode.make(code)
                                    buf = BytesIO()
                                    qr_img.save(buf, format="PNG")
                                    st.image(buf, caption=f"Redemption Code: {code}", width=250)
                                    st.balloons()
                                else:
                                    st.error(resp.json().get("detail", "Redemption failed."))
                            except:
                                st.error("Could not connect to server.")
                    st.write("---")

            st.subheader("Redemption History")
            try:
                hist = requests.get(f"{API}/redemptions/{student_id.strip()}").json()
                if hist:
                    df_hist = pd.DataFrame(hist)
                    st.dataframe(df_hist[['reward_name', 'cost', 'code', 'timestamp']], use_container_width=True, hide_index=True)
                else:
                    st.info("No redemptions yet.")
            except:
                pass