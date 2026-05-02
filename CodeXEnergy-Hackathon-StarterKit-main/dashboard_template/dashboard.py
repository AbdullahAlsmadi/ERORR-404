import streamlit as st
import pandas as pd
import altair as alt

# 1. Sayfa Ayarları (إعدادات الصفحة)
st.set_page_config(page_title="Yeşil Puan | Kampüs Yönetimi", layout="wide", page_icon="♻️")

# 2. Başlık ve Açıklama (العنوان والوصف)
st.title("♻️ 'Yeşil Puan' Sistemi - Akıllı Kampüs Yönetimi")
st.markdown("""
Bu panel, üniversite yönetiminin kampüs genelindeki geri dönüşüm faaliyetlerini izlemesi için tasarlanmıştır. 
Öğrenciler QR kod okuttukça veriler anlık olarak güncellenir.
""")

st.divider()

# 3. Özet Metrikler (الإحصائيات الرئيسية)
st.subheader("📊 Genel Performans")
m1, m2, m3, m4 = st.columns(4)
m1.metric(label="Geri Dönüştürülen Toplam Atık", value="2,145 Adet", delta="+12% Bugün")
m2.metric(label="Tasarruf Edilen Karbon (CO2)", value="185.4 kg", delta="-8.2 kg")
m3.metric(label="Dağıtılan Yeşil Puan", value="21,450", delta="+1,200 اليوم")
m4.metric(label="Aktif Katılımcı Öğrenci", value="642", delta="+15 Yeni")

st.divider()

# 4. Veri Hazırlama (البيانات)
@st.cache_data
def get_final_data():
    data = {
        "Tarih": ["02.05 10:15", "02.05 11:30", "02.05 12:05", "02.05 12:45", "02.05 13:10", "02.05 13:45"],
        "Öğrenci No": ["20230199", "20220455", "20240112", "20210988", "20230777", "20240552"],
        "Atık Türü": ["Plastik", "Cam", "Kağıt", "Plastik", "Cam", "Kağıt"],
        "Miktar": ["5 Şişe", "2 Şişe", "1.2 kg", "10 Şişe", "4 Şişe", "0.8 kg"],
        "Puan": [50, 40, 30, 100, 80, 20],
        "CO2 Tasarrufu (g)": [400, 600, 1200, 800, 1200, 800]
    }
    return pd.DataFrame(data)

df = get_final_data()

# 5. Görselleştirme Bölümü (الرسوم البيانية)
col_left, col_right = st.columns([1, 1.5])

with col_left:
    st.subheader("📈 Atık Dağılımı")
    # رسم بياني دائري لتوزيع أنواع النفايات
    source = pd.DataFrame({
        "Kategori": ["Plastik", "Kağıt", "Cam"],
        "Değer": [55, 30, 15] # نسب مئوية افتراضية
    })
    
    chart = alt.Chart(source).mark_arc(innerRadius=60).encode(
        theta=alt.Theta(field="Değer", type="quantitative"),
        color=alt.Color(field="Kategori", type="nominal", 
                        scale=alt.Scale(range=['#0068c9', '#83c9ff', '#29b09d'])),
        tooltip=["Kategori", "Değer"]
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)
    st.info("💡 En çok geri dönüşüm **Plastik** kategorisinde yapılıyor.")

with col_right:
    st.subheader("📋 Son İşlemler (Canlı Akış)")
    st.dataframe(df, use_container_width=True, hide_index=True)

# 6. Footer (تذييل الصفحة)
st.sidebar.success("Sistem Durumu: Aktif 🟢")
st.sidebar.write("---")
st.sidebar.markdown("### Hedefimiz:")
st.sidebar.info("Kampüs karbon ayak izini %20 oranında azaltmak.")