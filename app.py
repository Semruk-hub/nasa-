import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date

# Sayfa yapılandırması
st.set_page_config(page_title="NASA Asteroit Takip", page_icon="🛰️", layout="wide")

st.title("🛰️ NASA Canlı Asteroit Takip Paneli")
st.markdown("Dünya'ya yaklaşan gök taşlarını NASA NeoWs API üzerinden anlık takip edin.")

# NASA API Bilgileri
API_KEY = "8nkkMMdRqBgFJqPpRmRzhPgFCqPGKcHFdFr6TKFH"
BASE_URL = "https://api.nasa.gov/neo/rest/v1/feed"

# Tarih seçici
secilen_tarih = st.date_input("İncelenecek Tarihi Seçin", value=date.today())
tarih_str = secilen_tarih.strftime("%Y-%m-%d")

# Veri çekme işlemi
with st.spinner("NASA verileri taranıyor..."):
    params = {
        "start_date": tarih_str,
        "end_date": tarih_str,
        "api_key": API_KEY
    }
    cevap = requests.get(BASE_URL, params=params)

if cevap.status_code == 200:
    veri = cevap.json()
    element_sayisi = veri.get("element_count", 0)
    st.metric(label="Yaklaşan Toplam Asteroit", value=element_sayisi)
    
    asteroit_listesi = veri["near_earth_objects"].get(tarih_str, [])
    
    if asteroit_listesi:
        tablo_verisi = []
        for ast in asteroit_listesi:
            isim = ast["name"]
            cap_min = ast["estimated_diameter"]["meters"]["estimated_diameter_min"]
            cap_max = ast["estimated_diameter"]["meters"]["estimated_diameter_max"]
            ortalama_cap = round((cap_min + cap_max) / 2, 2)
            
            yakinlasma = ast["close_approach_data"][0]
            hiz = round(float(yakinlasma["relative_velocity"]["kilometers_per_hour"]), 2)
            mesafe = round(float(yakinlasma["miss_distance"]["kilometers"]), 2)
            tehlikeli = "Evet" if ast["is_potentially_hazardous_asteroid"] else "Hayır"
            
            tablo_verisi.append({
                "İsim": isim,
                "Ortalama Çap (m)": ortalama_cap,
                "Hız (km/sa)": hiz,
                "Dünya'ya Mesafe (km)": mesafe,
                "Tehlikeli mi?": tehlikeli
            })
        
        df = pd.DataFrame(tablo_verisi)
        
        # Grafik
        st.subheader("📊 Asteroit Büyüklüğü ve Dünya'ya Mesafesi")
        fig = px.scatter(
            df,
            x="Dünya'ya Mesafe (km)",
            y="Ortalama Çap (m)",
            size="Ortalama Çap (m)",
            color="Tehlikeli mi?",
            hover_name="İsim",
            color_discrete_map={"Evet": "red", "Hayır": "green"},
            title="Yeşil: Güvenli | Kırmızı: Potansiyel Tehlikeli"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tablo
        st.subheader("📋 Yaklaşan Cisimlerin Detay Listesi")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Bu tarihte Dünya'ya yaklaşan kayıtlı asteroit bulunamadı.")
else:
    st.error(f"NASA API bağlantı hatası! Kod: {cevap.status_code}")
