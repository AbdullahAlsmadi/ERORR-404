import streamlit as st
import pandas as pd
import altair as alt

# 1. Sayfa Ayarları (إعدادات الصفحة)
st.set_page_config(page_title="Yeşil Puan Dashboard", layout="wide", page_icon="♻️")

# 2. Başlık ve Açıklama (العنوان والوصف)
st.title("♻️ 'Yeşil Puan' Sistemi - Kapsamlı Geri Dönüşüm")
st.markdown("Plastik, cam, kağıt ve metal geri dönüşüm istatistiklerini takip etmek ve kampüsün karbon ayak izini azaltmak için üniversite yönetimi kontrol paneli.")

st.divider() # خط فاصل

# 3. Hızlı İstatistikler (إحصائيات سريعة للجامعة)
st.subheader("📊 Günlük Kampüs İstatistikleri")
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Toplanan Toplam Atık", value="3.450 Adet", delta="+420 Bugün")
col2.metric(label="Tasarruf Edilen Karbon (CO2)", value="345 kg", delta="-45 kg (İyileşme)")
col3.metric(label="Dağıtılan Toplam Puan", value="34.500 Puan", delta="+4.200 Bugün")
col4.metric(label="Aktif Öğrenci Sayısı", value="850", delta="+12 Yeni")

st.divider()

# 4. Sahte Veri Tablosu (جدول البيانات الوهمي لعمليات الـ QR بأنواع مختلفة)
@st.cache_data
def load_mock_data():
    data = {
        "Tarih ve Saat": ["2026-05-02 10:15", "2026-05-02 11:30", "2026-05-02 12:05", "2026-05-02 12:45", "2026-05-02 13:10"],
        "Öğrenci Numarası": ["20230199", "20220455", "20240112", "20210988", "20230777"],
        "Atık Türü": ["Plastik", "Cam", "Kağıt/Karton", "Metal (Kutu)", "Plastik"],
        "Adet / Ağırlık": ["5 Adet", "2 Adet", "1.5 kg", "3 Adet", "10 Adet"],
        "Kazanılan Puan": [50, 40, 30, 60, 100],
        "Tasarruf Edilen Karbon (gram)": [400, 600, 1500, 900, 800]
    }
    return pd.DataFrame(data)

df = load_mock_data()

# 5. Görselleştirme ve Tabloyu Yan Yana Gösterme (عرض الرسم البياني والجدول)
col_chart, col_table = st.columns([1, 1.5]) # تقسيم الشاشة لعمودين

with col_chart:
    st.subheader("📈 Atık Türlerine Göre Dağılım")
    # بيانات الرسم البياني
    chart_data = pd.DataFrame({
        'Atık Türü': ['Plastik', 'Cam', 'Kağıt', 'Metal'],
        'Toplanan Miktar': [1200, 450, 900, 600]
    })
    
    # رسم بياني باستخدام Altair
    pie_chart = alt.Chart(chart_data).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Toplanan Miktar", type="quantitative"),
        color=alt.Color(field="Atık Türü", type="nominal", legend=alt.Legend(title="Atık Türü")),
        tooltip=['Atık Türü', 'Toplanan Miktar']
    ).properties(height=300)
    
    st.altair_chart(pie_chart, use_container_width=True)

with col_table:
    st.subheader("📋 Son İşlemler")
    st.dataframe(df, use_container_width=True)