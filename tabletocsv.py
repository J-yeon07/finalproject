import streamlit as st
import pdfplumber
import pandas as pd

st.title("PDF 표 ➝ CSV 변환기")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        all_tables = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                try:
                    if not table or len(table) < 2:
                        continue  # 헤더 + 최소 한 줄 이상만 포함된 것만
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_tables.append(df)
                except Exception as e:
                    st.warning(f"표 처리 중 오류 발생: {e}")
                    continue

        if all_tables:
            st.success(f"{len(all_tables)}개의 표가 추출되었습니다.")
            for i, table_df in enumerate(all_tables):
                st.markdown(f"### 📄 표 {i+1}")
                try:
                    st.dataframe(table_df)
                    csv = table_df.to_csv(index=False).encode('utf-8')
                    st.download_button(f"표 {i+1} CSV 다운로드", csv, f"table_{i+1}.csv", "text/csv")
                except Exception as e:
                    st.error(f"표 {i+1}를 표시하는 중 오류가 발생했습니다: {e}")
        else:
            st.warning("표를 찾을 수 없습니다.")
