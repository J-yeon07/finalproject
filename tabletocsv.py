import streamlit as st
import pdfplumber
import pandas as pd

st.title("PDF 표 ➝ CSV 변환기")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")

def clean_headers(headers):
    cleaned = []
    used = {}
    for i, h in enumerate(headers):
        if h is None or h.strip() == "":
            h = f"Unnamed_{i}"
        if h in used:
            used[h] += 1
            h = f"{h}_{used[h]}"
        else:
            used[h] = 0
        cleaned.append(h)
    return cleaned

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        all_tables = []
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table_num, table in enumerate(tables):
                try:
                    if not table or len(table) < 2:
                        continue

                    raw_headers = table[0]
                    cleaned_headers = clean_headers(raw_headers)
                    df = pd.DataFrame(table[1:], columns=cleaned_headers)
                    all_tables.append(df)

                except Exception as e:
                    st.warning(f"{page_num+1}쪽 표 {table_num+1} 처리 중 오류: {e}")

        if all_tables:
            st.success(f"{len(all_tables)}개의 표가 추출되었습니다.")
            for i, table_df in enumerate(all_tables):
                st.markdown(f"### 📄 표 {i+1}")
                try:
                    st.dataframe(table_df)
                    csv = table_df.to_csv(index=False).encode('utf-8')
                    st.download_button(f"표 {i+1} CSV 다운로드", csv, f"table_{i+1}.csv", "text/csv")
                except Exception as e:
                    st.error(f"표 {i+1} 표시 중 오류 발생: {e}")
        else:
            st.warning("표를 찾을 수 없습니다.")
