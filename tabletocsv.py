import streamlit as st
import pdfplumber
import pandas as pd

st.title("📄 PDF 표 ➝ CSV 변환기 (디버깅 모드)")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        all_tables = []
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            st.write(f"📄 {page_num+1}쪽에서 {len(tables)}개의 표 감지됨")
            for table_num, table in enumerate(tables):
                st.write(f"🔹 원본 표 {table_num+1}:")
                st.write(table)  # 추출된 원시 데이터 확인
                all_tables.append(table)

        if not all_tables:
            st.warning("⚠️ 어떤 페이지에서도 표를 감지하지 못했습니다.")
        else:
            st.success("표 추출 성공. 위의 표 원본 데이터를 확인하세요.")
