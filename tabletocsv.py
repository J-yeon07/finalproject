import streamlit as st
import pdfplumber
import pandas as pd

st.title("📄 PDF 표 ➝ CSV 변환기 (전체 표 무제한 처리)")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")

def clean_table_rows(table):
    max_len = max(len(row) for row in table if row)
    padded = [row + [""] * (max_len - len(row)) for row in table]
    return padded

def generate_columns(n):
    base = ["구분"] + [str(y) for y in range(2013, 2023)]
    extras = [f"extra_{i}" for i in range(n - len(base))]
    return base + extras

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        all_tables = []
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table_num, table in enumerate(tables):
                if not table or len(table) < 2:
                    continue

                cleaned = clean_table_rows(table)
                title = cleaned[0][0] or f"표_{page_num+1}_{table_num+1}"
                data_rows = cleaned[1:]

                num_cols = len(data_rows[0])
                columns = generate_columns(num_cols)

                try:
                    df = pd.DataFrame(data_rows, columns=columns)
                    all_tables.append((f"{title}_{page_num+1}_{table_num+1}", df))
                except Exception as e:
                    st.error(f"❌ DataFrame 변환 실패: {e}")
                    st.write("원본 데이터:", data_rows)

        if all_tables:
            st.success(f"✅ 총 {len(all_tables)}개의 표가 추출되었습니다.")
            for i, (title, df) in enumerate(all_tables):
                st.markdown(f"### 📊 {i+1}. {title}")
                st.dataframe(df)

                csv = df.to_csv(index=False).encode('utf-8')
                safe_title = title.replace(" ", "_").replace("/", "-").replace("\\", "-")
                st.download_button(
                    label=f"📥 '{title}' CSV 다운로드",
                    data=csv,
                    file_name=f"{safe_title}.csv",
                    mime='text/csv'
                )
        else:
            st.warning("⚠️ 어떤 표도 추출되지 않았습니다.")
