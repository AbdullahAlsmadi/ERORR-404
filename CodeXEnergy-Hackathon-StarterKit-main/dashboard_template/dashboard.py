import streamlit as st
import pandas as pd
import altair as alt
import requests
import qrcode
from io import BytesIO

# ---- إعدادات الصفحة ----
st.set_page_config(page_title="EcoTrack | ERROR-404", layout="wide", page_icon="♻️")

API = "http://127.0.0.1:8000"

# ---- الشريط الجانبي لاختيار الوضع ----
mode = st.sidebar.radio("🔁 اختر العرض:", ["📊 لوحة الإدارة", "🎓 وضع الطالب"])
st.sidebar.markdown("---")
st.sidebar.success("حالة الخادم: متصل 🟢")
st.sidebar.info("المشروع ضمن تحدي CodeXEnergy - فريق ERROR-404")

# ================================================
# 1. وضع الإدارة (بيانات حية من API)
# ================================================
if mode == "📊 لوحة الإدارة":
    st.title("♻️ 'Yeşil Puan' Sistemi - Akıllı Kampüs Yönetimi")
    st.markdown("البيانات التالية **حية** من خادم EcoTrack.")

    # ---- جلب الإحصائيات من الخادم ----
    try:
        stats = requests.get(f"{API}/students").json()
    except:
        stats = {"total_students": 0, "total_points": 0, "total_carbon_grams": 0, "students": []}

    # ---- البطاقات الرئيسية ----
    st.subheader("📊 Genel Performans")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="👥 Aktif Katılımcı Öğrenci", value=stats["total_students"])
    m2.metric(label="🌿 Dağıtılan Yeşil Puan", value=stats["total_points"])
    m3.metric(label="🌍 Tasarruf Edilen Karbon (g)", value=stats["total_carbon_grams"])
    # يمكن استبدال هذا بقيمة حقيقية لاحقاً عند دعم نوع النفايات
    m4.metric(label="♻️ Geri Dönüştürülen Toplam Atık", value="...")

    st.divider()

    # ---- الرسم البياني الدائري (يبقى افتراضياً حالياً) ----
    col_left, col_right = st.columns([1, 1.5])
    with col_left:
        st.subheader("📈 Atık Dağılımı")
        source = pd.DataFrame({
            "Kategori": ["Plastik", "Kağıt", "Cam"],
            "Değer": [55, 30, 15]
        })
        chart = alt.Chart(source).mark_arc(innerRadius=60).encode(
            theta=alt.Theta(field="Değer", type="quantitative"),
            color=alt.Color(field="Kategori", type="nominal",
                            scale=alt.Scale(range=['#0068c9', '#83c9ff', '#29b09d'])),
            tooltip=["Kategori", "Değer"]
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
        st.info("💡 En çok geri dönüşüm **Plastik** kategorisinde yapılıyor.")

    # ---- سجل العمليات الحيّ ----
    with col_right:
        st.subheader("📋 Son İşlemler (Canlı Akış)")
        try:
            scans = requests.get(f"{API}/scans?limit=10").json()
            if scans:
                df_scans = pd.DataFrame(scans)
                st.dataframe(df_scans, use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد عمليات تدوير بعد.")
        except:
            st.warning("تعذر الاتصال بالخادم.")

# ================================================
# 2. وضع الطالب (بطاقة + كود QR)
# ================================================
else:
    st.title("🎓 بطاقتي الخضراء - EcoTrack")
    student_id = st.text_input("أدخل رقمك الجامعي:", "2021001")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 عرض بطاقتي"):
            try:
                resp = requests.get(f"{API}/student/{student_id.strip()}")
                if resp.status_code == 200:
                    user = resp.json()
                    st.success(f"أهلاً بالطالب {user.get('name') or student_id}")
                    st.metric("🌿 نقاطي", user["green_points"])
                    st.metric("🌍 الكربون الذي وفرته", f"{user['carbon_saved_grams']} جم")
                else:
                    st.warning("لا يوجد سجل تدوير بعد. النقاط 0.")
            except:
                st.error("تأكد أن الخادم يعمل.")

    with col2:
        # توليد QR من رقم الطالب
        qr = qrcode.make(student_id.strip())
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf, caption="📱 كود QR الخاص بك للتدوير", width=250)
        st.caption("اعرض هذا الكود عند محطة التدوير لربح النقاط.")

    # ---- محاكاة المسح (للتجربة) ----
    st.divider()
    st.subheader("🔄 تجربة: تنفيذ عملية تدوير (محاكاة)")
    if st.button("♻️ امسح الكود الآن (أضف نقاطاً)"):
        try:
            resp = requests.post(f"{API}/scan", json={"student_id": student_id.strip()})
            if resp.status_code == 200:
                data = resp.json()
                st.success(f"✅ تمت الإضافة! النقاط الآن: {data['student']['green_points']}")
                st.balloons()
            else:
                st.error("فشل. تأكد من الخادم.")
        except:
            st.error("تعذر الاتصال بالخادم.")