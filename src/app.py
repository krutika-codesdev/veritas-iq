import streamlit as st

from parser.pdf_parser import extract_text_from_pdf
from ai.extractor import extract_product_information
from processing.normalizer import normalize_weight

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

    ai_response = extract_product_information(extracted_text)

    if isinstance(ai_response, dict) and "weight" in ai_response:
         normalized_weight = normalize_weight(ai_response["weight"])
         ai_response["weight"] = normalized_weight.model_dump() if normalized_weight else None

    st.subheader("Extracted Text")

    st.text_area(
        label="PDF Content",
        value=extracted_text,
        height=400
    )

    st.subheader("AI Extraction")

    if isinstance(ai_response, dict) and ai_response.get("status") == "error":
         st.warning("Gemini API is currently unavailable.")
         st.text(ai_response["message"])
    else:
         st.json(ai_response)