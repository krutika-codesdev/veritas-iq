import streamlit as st

from parser.pdf_parser import extract_text_from_pdf


st.set_page_config(
    page_title="VeritasIQ",
    page_icon="📦",
    layout="wide"
)

st.title("VeritasIQ")
st.subheader("AI-powered Product Intelligence Platform")

st.info("Stage 1: PDF Text Extraction")

uploaded_file = st.file_uploader(
    "Upload a Product PDF",
    type=["pdf"]
)

if uploaded_file:

    st.success(f"Uploaded: {uploaded_file.name}")

    extracted_text = extract_text_from_pdf(uploaded_file)

    st.subheader("Extracted Text")

    st.text_area(
        label="PDF Content",
        value=extracted_text,
        height=400
    )