import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

# Sayfa Yapılandırması
st.set_page_config(page_title="NASA Uzay & Gözlem Portalı", page_icon="🚀", layout="wide")

API_KEY = "8nkkMMdRqBgFJqPpRmRzhPgFCqPGKcHFdFr6TKFH"

st.title("🚀 NASA Canlı Uzay & Gözlem Portalı")

# Sekmeler
tab_asteroit, tab_iss, tab_epic, tab_donki, tab_apod, tab_mars = st.tabs([
    "🛰️ Asteroit Radarı", 
    "🌍 ISS Canlı Harita", 
    "🔵 EPIC Dünya Görüntüsü",
    "☀️ Uzay Hava Durumu (DONKI)",
    "🌌 Günün Fotoğrafı (APOD)", 
    "🔴 Mars Rover"
])

# ---------------------------------------------------------
# 1. SEKME: ASTEROİT RADARI & TEHLİKE ALARMI
# ---------------------------------------------------------
with tab_asteroit:
    st.subheader("Dünya'ya Yaklaşan Gök Taşları")
    secilen_tarih = st.date_input("İncelenecek Tarih", value=date.today(), key="ast_tarih")
    tarih_str = secilen_tarih.strftime("%Y-%m-%d")
    
    with st.spinner("NASA asteroit radarı taranıyor..."):
        url = "https://api.nasa.gov/neo/rest/v1/feed"
        params = {"start_date": tarih_str, "end_date": tarih_str, "api_key": API_KEY}
        cevap = requests.get(url, params=params)
    
    if cevap.status_code == 200:
        veri = cevap.json()
        toplam = veri.get("element_count", 0)
        asteroitler = veri["near_earth_objects"].get(tarih_str, [])
        
        kritik_cisimler = []
        tablo = []
        
        if asteroitler:
            for ast in asteroitler:
                isim = ast["name"]
                cap_min = ast["estimated_diameter"]["meters"]["estimated_diameter_min"]
                cap_max = ast["estimated_diameter"]["meters"]["estimated_diameter_max"]
                ort_cap = round((cap_min + cap_max) / 2, 2)
                
                yak = ast["close_approach_data"][0]
                hiz = round(float(yak["relative_velocity"]["kilometers_per_hour"]), 2)
                mesafe_km = round(float(yak["miss_distance"]["kilometers"]), 2)
                mesafe_ld = round(float(yak["miss_distance"]["lunar"]), 2)
                tehlike = ast["is_potentially_hazardous_asteroid"]
                
                # Kritik alarm kontrolü: 1 Ay mesafesinden yakın VEYA (tehlikeli ve 100m'den büyük)
                if mesafe_ld < 1.0 or (tehlike and ort_cap > 100):
                    kritik_cisimler.append((isim, ort_cap, mesafe_ld, hiz))
                
                if ort_cap < 15:
                    olcek = "Otobüs boyutu"
                elif ort_cap < 70:
                    olcek = "Yolcu uçağı boyutu"
                elif ort_cap < 300:
                    olcek = "Futbol sahası boyutu"
                else:
                    olcek = "Gökdelen / Dağ boyutu"
                
                tablo.append({
                    "İsim": isim,
                    "Ort. Çap (m)": ort_cap,
                    "Ölçek": olcek,
                    "Hız (km/sa)": hiz,
                    "Mesafe (km)": mesafe_km,
                    "Mesafe (Ay Katı)": mesafe_ld,
                    "Tehlikeli mi?": "Evet ⚠️" if tehlike else "Hayır ✅"
                })
            
            # Alarm Çubuğu
            if kritik_cisimler:
                st.error(f"🚨 KRİTİK YAKINLAŞMA ALARMI! Bugün Ay mesafesinden yakın veya 100m'den büyük {len(kritik_cisimler)} tehlikeli gök taşı tespit edildi!")
                for c_isim, c_cap, c_ld, c_hiz in kritik_cisimler:
                    st.warning(f"⚠️ **{c_isim}** | Çap: ~{c_cap}m | Mesafe: {c_ld} Lunar (Ay Mesafesi) | Hız: {c_hiz} km/sa")
            else:
                st.success("✅ Seçilen tarihte kritik yakınlaşma alarmı yok.")

            col1, col2 = st.columns(2)
            col1.metric("Toplam Asteroit", toplam)
            col2.metric("Alarm Seviyesindeki Cisimler", len(kritik_cisimler))
            
            df = pd.DataFrame(tablo)
            fig = px.scatter(
                df,
                x="Mesafe (km)",
                y="Ort. Çap (m)",
                size="Ort. Çap (m)",
                color="Tehlikeli mi?",
                hover_name="İsim",
                hover_data=["Hız (km/sa)", "Ölçek", "Mesafe (Ay Katı)"],
                color_discrete_map={"Evet ⚠️": "red", "Hayır ✅": "green"},
                title="Yeşil: Güvenli | Kırmızı: Potansiyel Tehlikeli"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Bu tarihte Dünya'ya yaklaşan asteroit kaydı bulunamadı.")
    else:
        st.error(f"NASA verisi alınamadı (Kod: {cevap.status_code})")

# ---------------------------------------------------------
# 2. SEKME: ISS CANLI HARİTA TAKİBİ
# ---------------------------------------------------------
with tab_iss:
    st.subheader("Uluslararası Uzay İstasyonu (ISS) Canlı Takip")
    if st.button("📡 Konumu Güncelle"):
        st.rerun()
        
    try:
        iss_res = requests.get("https://api.wheretheiss.at/v1/satellites/25544", timeout=5)
        if iss_res.status_code == 200:
            iss_data = iss_res.json()
            lat = iss_data["latitude"]
            lon = iss_data["longitude"]
            hiz = round(iss_data["velocity"], 2)
            yukseklik = round(iss_data["altitude"], 2)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Enlem (Lat)", round(lat, 4))
            c2.metric("Boylam (Lon)", round(lon, 4))
            c3.metric("Hız (km/sa)", hiz)
            c4.metric("Yerden Yükseklik (km)", yukseklik)
            
            # Harita
            map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
            st.map(map_data, zoom=2)
        else:
            st.warning("ISS anlık koordinat servisine ulaşılamadı.")
    except Exception as e:
        st.error(f"Bağlantı hatası: {e}")

# ---------------------------------------------------------
# 3. SEKME: EPIC DÜNYA GÖRÜNTÜLERİ
# ---------------------------------------------------------
with tab_epic:
    st.subheader("1.5 Milyon Km Öteden Tam Disk Dünya (DSCOVR/EPIC)")
    with st.spinner("En güncel derin uzay Dünya fotoğrafları getiriliyor..."):
        epic_url = f"https://api.nasa.gov/EPIC/api/natural?api_key={API_KEY}"
        epic_res = requests.get(epic_url)
        
    if epic_res.status_code == 200:
        epic_data = epic_res.json()
        if epic_data:
            son_foto = epic_data[0]
            foto_tarih = son_foto["date"].split(" ")[0]
            yil, ay, gun = foto_tarih.split("-")
            resim_adi = son_foto["image"]
            resim_url = f"https://api.nasa.gov/EPIC/archive/natural/{yil}/{ay}/{gun}/png/{resim_adi}.png?api_key={API_KEY}"
            
            st.image(resim_url, caption=f"Çekim Tarihi: {son_foto['date']} (UTC)", use_column_width=True)
            st.caption(f"Kamera: EPIC | Koordinat: {son_foto.get('centroid_coordinates', {})}")
        else:
            st.info("Son 48 saate ait işlenmiş EPIC fotoğrafı bulunamadı.")
    else:
        st.error("EPIC servisine ulaşılamadı.")

# ---------------------------------------------------------
# 4. SEKME: DONKI UZAY HAVA DURUMU (GÜNEŞ PATLAMALARI)
# ---------------------------------------------------------
with tab_donki:
    st.subheader("Güneş Fırtınaları ve Koronal Kütle Atımları (CME)")
    bugun = date.today()
    yedi_gun_once = bugun - timedelta(days=14)
    
    with st.spinner("Güneş patlamaları taranıyor..."):
        donki_url = "https://api.nasa.gov/DONKI/CME"
        params_donki = {
            "startDate": yedi_gun_once.strftime("%Y-%m-%d"),
            "endDate": bugun.strftime("%Y-%m-%d"),
            "api_key": API_KEY
        }
        donki_res = requests.get(donki_url, params=params_donki)
        
    if donki_res.status_code == 200:
        patlamalar = donki_res.json()
        if patlamalar:
            st.warning(f"Son 14 günde Güneş'te toplam {len(patlamalar)} büyük patlama kaydedildi.")
            for p in patlamalar[:5]:  # Son 5 patlama
                st.markdown(f"**⚡ Patlama Zamanı:** {p.get('startTime')}")
                st.write(f"Not: {p.get('note', 'Açıklama girilmemiş.')}")
                st.divider()
        else:
            st.success("Son 14 günde kayda değer büyük bir Güneş patlaması tespit edilmedi.")
    else:
        st.error("DONKI veri servisine ulaşılamadı.")

# ---------------------------------------------------------
# 5. SEKME: APOD
# ---------------------------------------------------------
with tab_apod:
    st.subheader("Astronomy Picture of the Day")
    secilen_apod_tarihi = st.date_input("Tarih Seçin", value=date.today(), key="apod_tarih")
    
    apod_url = "https://api.nasa.gov/planetary/apod"
    res_apod = requests.get(apod_url, params={"date": secilen_apod_tarihi.strftime("%Y-%m-%d"), "api_key": API_KEY})
        
    if res_apod.status_code == 200:
        apod_data = res_apod.json()
        st.markdown(f"### {apod_data.get('title', 'Başlıksız')}")
        if apod_data.get("media_type") == "image":
            st.image(apod_data.get("url"), caption=apod_data.get("title"), use_column_width=True)
        elif apod_data.get("media_type") == "video":
            st.video(apod_data.get("url"))
        with st.expander("Açıklama"):
            st.write(apod_data.get("explanation", ""))

# ---------------------------------------------------------
# 6. SEKME: MARS ROVER
# ---------------------------------------------------------
with tab_mars:
    st.subheader("Curiosity Keşif Aracı Fotoğrafları")
    sol = st.slider("Mars Günü (Sol)", min_value=1, max_value=3000, value=1000)
    
    mars_url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
    mars_res = requests.get(mars_url, params={"sol": sol, "api_key": API_KEY})
        
    if mars_res.status_code == 200:
        fotolar = mars_res.json().get("photos", [])
        if fotolar:
            st.success(f"{sol}. güne ait {len(fotolar)} fotoğraf bulundu.")
            c1, c2, c3 = st.columns(3)
            for idx, foto in enumerate(fotolar[:6]):
                col = [c1, c2, c3][idx % 3]
                col.image(foto["img_src"], caption=foto["camera"]["full_name"], use_column_width=True)
        else:
            st.info("Bu Mars gününe ait fotoğraf bulunamadı.")
