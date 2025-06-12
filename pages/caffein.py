import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import time

st.set_page_config(page_title="CSV ➝ 지도 시각화", layout="wide")
st.title("📍 CSV 데이터 지도 시각화 (폐업 제외)")

uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type="csv")

@st.cache_data(show_spinner=False)
def geocode_address(address):
    geolocator = Nominatim(user_agent="csv-map-app")
    try:
        location = geolocator.geocode(address, timeout=10)
        time.sleep(1)  # API 제한 우회용
        if location:
            return (location.latitude, location.longitude)
    except:
        return None
    return None

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 1. 폐업 행 제거 (F열: 인덱스 5)
    filtered_df = df[~df.iloc[:, 5].astype(str).str.contains("폐업", na=False)]

    # 2. 필요한 열 추출 (도로명 주소: Q열 = index 16, 전화번호: M열 = index 12)
    addresses = filtered_df.iloc[:, 16].astype(str)
    phones = filtered_df.iloc[:, 12].astype(str)

    st.info(f"✅ 총 {len(filtered_df)}개의 유효한 사업장이 확인되었습니다.")

    # 3. 지도 생성
    map_center = (37.5665, 126.9780)  # 서울 중심
    m = folium.Map(location=map_center, zoom_start=11)
    marker_cluster = MarkerCluster().add_to(m)

    # 4. 주소별 마커 추가
    for i in range(len(addresses)):
        address = addresses.iloc[i]
        phone = phones.iloc[i]
        coords = geocode_address(address)
        if coords:
            folium.Marker(
                location=coords,
                popup=f"{address}<br>📞 {phone}",
                tooltip="클릭하면 정보 표시",
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(marker_cluster)

    # 5. 지도 출력
    st.subheader("🗺️ 지도에서 사업장 위치 보기")
    st_data = st_folium(m, width=900, height=600)

else:
    st.warning("CSV 파일을 업로드하면 지도에 표시됩니다.")
