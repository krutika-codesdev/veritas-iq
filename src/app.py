import streamlit as st

from parser.pdf_parser import extract_text_from_pdf
from parser.csv_parser import extract_records_from_csv
from parser.excel_parser import extract_records_from_excel
from ai.extractor import extract_product_information
from processing.normalizer import normalize_weight

st.set_page_config(
    page_title="VeritasIQ",
    page_icon="📦",
    layout="wide"
)

st.title("VeritasIQ")
st.subheader("AI-powered Product Intelligence Platform")

st.info("Stage 1: Multi-source Product Ingestion")

uploaded_files = st.file_uploader(
    "Upload Product Sources",
    type=["pdf", "csv", "xlsx"],
    accept_multiple_files=True
)

if uploaded_files:

    st.success(f"{len(uploaded_files)} source(s) uploaded")

    for uploaded_file in uploaded_files:

        st.divider()
        st.subheader(f"Source: {uploaded_file.name}")

        if uploaded_file.name.lower().endswith(".pdf"):

            extracted_text = extract_text_from_pdf(uploaded_file)

            ai_response = extract_product_information(extracted_text)

            if isinstance(ai_response, dict) and "weight" in ai_response:
                normalized_weight = normalize_weight(ai_response["weight"])
                ai_response["weight"] = (
                    normalized_weight.model_dump()
                    if normalized_weight
                    else None
                )

            st.subheader("Extracted Text")

            st.text_area(
                label="PDF Content",
                value=extracted_text,
                height=400,
                key=f"pdf_text_{uploaded_file.name}"
            )

            st.subheader("AI Extraction")

            if isinstance(ai_response, dict) and ai_response.get("status") == "error":
                st.warning("Gemini API is currently unavailable.")
                st.text(ai_response["message"])
            else:
                st.json(ai_response)

        elif uploaded_file.name.lower().endswith(".csv"):

            records = extract_records_from_csv(uploaded_file)

            st.subheader("CSV Records")
            st.write(records)

        elif uploaded_file.name.lower().endswith(".xlsx"):

            records = extract_records_from_excel(uploaded_file)

            st.subheader("Excel Records")
            st.write(records)