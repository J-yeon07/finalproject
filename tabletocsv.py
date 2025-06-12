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
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

        if all_tables:
            st.success(f"{len(all_tables)}개의 표가 추출되었습니다.")
            for i, table_df in enumerate(all_tables):
                st.write(f"📄 표 {i+1}")
                st.dataframe(table_df)
                csv = table_df.to_csv(index=False).encode('utf-8')
                st.download_button(f"표 {i+1} CSV 다운로드", csv, f"table_{i+1}.csv", "text/csv")
        else:
            st.warning("표를 찾을 수 없습니다.")
