import streamlit as st
import pdfplumber
import pandas as pd

st.title("📄 PDF 표 ➝ CSV 변환기 (깨진 표 자동 복구)")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")

def clean_table_rows(table):
    # 가장 긴 행 길이에 맞춰 나머지를 패딩
    max_len = max(len(row) for row in table if row)
    padded = [row + [""] * (max_len - len(row)) for row in table]
    return padded

def generate_columns(n):
    # 열 이름 자동 생성 (구분, 2013~2022, 남는 건 extra_1, extra_2...)
    base = ["구분"] + [str(y) for y in range(2013, 2023)]
    extras = [f"extra_{i}" for i in range(n - len(base))]
    return base + extras

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        all_tables = []

        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue

                cleaned = clean_table_rows(table)
                title = cleaned[0][0] or "제목없음"
                data_rows = cleaned[1:]

                num_cols = len(data_rows[0])
                columns = generate_columns(num_cols)

                try:
                    df = pd.DataFrame(data_rows, columns=columns)
                    all_tables.append((title.strip(), df))
                except Exception as e:
                    st.error(f"❌ DataFrame 변환 실패: {e}")
                    st.write("원본 데이터:", data_rows)

        if all_tables:
            st.success(f"{len(all_tables)}개의 표가 추출되어 CSV로 저장할 수 있습니다.")
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
            st.warning("⚠️ 추출할 수 있는 표가 없습니다.")
