import streamlit as st
import pdfplumber
import pandas as pd

st.title("📄 PDF 표 ➝ CSV 변환기 (개별 표 제목 기반 저장)")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")

def extract_table_with_title(table):
    """
    표에서 제목과 본문 데이터를 분리합니다.
    왼쪽 상단 셀을 제목으로 사용하고, 나머지 행은 데이터로 처리.
    """
    title = table[0][0] if table[0] and table[0][0] else "제목없음"

    # 실제 데이터는 제목 이후 행부터 시작
    data_rows = table[1:]
    if not data_rows:
        return title, None

    # 열 이름은 연도 (2013~2022)
    columns = ["구분"] + [str(year) for year in range(2013, 2023)]

    try:
        df = pd.DataFrame(data_rows, columns=columns)
        return title.strip(), df
    except Exception as e:
        return title.strip(), None

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        extracted_tables = []

        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                title, df = extract_table_with_title(table)
                if df is not None:
                    extracted_tables.append((title, df))

        if extracted_tables:
            st.success(f"{len(extracted_tables)}개의 표가 추출되었습니다.")

            for i, (title, df) in enumerate(extracted_tables):
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
            st.warning("추출 가능한 표가 없습니다.")
