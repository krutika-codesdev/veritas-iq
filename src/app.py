import streamlit as st

from processing.mapper import (
    map_record_to_common_format,
    map_ai_result_to_common_format,
)
from processing.matcher import products_match
from processing.validator import validate_weight

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

pdf_records = []
csv_records_common = []
excel_records_common = []

if uploaded_files:

    st.success(f"{len(uploaded_files)} source(s) uploaded")

    for uploaded_file in uploaded_files:

        st.divider()
        st.subheader(f"Source: {uploaded_file.name}")

        if uploaded_file.name.lower().endswith(".pdf"):

            extracted_text = extract_text_from_pdf(uploaded_file)

            ai_response = extract_product_information(extracted_text)

            if isinstance(ai_response, dict) and ai_response.get("status") != "error":
                pdf_common = map_ai_result_to_common_format(ai_response)
                pdf_records.append(pdf_common)

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

            common_records = [
                map_record_to_common_format(record)
                for record in records
            ]

            csv_records_common.extend(common_records)

            st.subheader("CSV Records")
            st.write(records)

        elif uploaded_file.name.lower().endswith(".xlsx"):

            records = extract_records_from_excel(uploaded_file)

            common_records = [
                map_record_to_common_format(record)
                for record in records
            ]

            excel_records_common.extend(common_records)

            st.subheader("Excel Records")
            st.write(records)

    # --------------------------------------------------
    # Product-level validation
    # --------------------------------------------------

    all_records = []

    for record in pdf_records:
        all_records.append({
        "source": "PDF",
        "record": record,
        })

    for record in csv_records_common:
        all_records.append({
        "source": "CSV",
        "record": record,
        })

    for record in excel_records_common:
        all_records.append({
        "source": "Excel",
        "record": record,
       })


    matched_group = None

    for base_item in all_records:

        base_record = base_item["record"]

        matches = []

        for candidate_item in all_records:

            candidate_record = candidate_item["record"]

            if products_match(base_record, candidate_record):
                matches.append(candidate_item)

        sources = {
            item["source"]
            for item in matches
        }

        if {"PDF", "CSV", "Excel"}.issubset(sources):
            matched_group = matches
            break


    if matched_group:

        st.divider()
        st.header("Product Validation")

        product_names = [
            item["record"].get("product_name")
            for item in matched_group
        ]

    st.subheader("Matched Product")

    st.write(" / ".join(product_names))


    # --------------------------------------------------
    # Collect weights
    # --------------------------------------------------

    weight_values = []

    for item in matched_group:

        source = item["source"]
        record = item["record"]

        raw_weight = record.get("weight")

        if not raw_weight:
            continue

        if isinstance(raw_weight, dict):
            weight_input = raw_weight
        else:
            weight_input = {
                "value": raw_weight,
                "unit": "g",
            }

        normalized_weight = normalize_weight(weight_input)

        if normalized_weight:

            weight_values.append({
                "source": source,
                "value": normalized_weight.value,
                "unit": normalized_weight.unit,
            })


    # --------------------------------------------------
    # Validate
    # --------------------------------------------------

    validation_result = validate_weight(weight_values)


    # --------------------------------------------------
    # Display validation
    # --------------------------------------------------

    st.subheader("Weight Validation")

    for item in weight_values:

        st.write(
            f"**{item['source']}** → "
            f"{item['value']} {item['unit']}"
        )


    status = validation_result.get("status")

    if status == "conflict":

        st.error("CONFLICT")

    elif status == "agreement":

        st.success("AGREEMENT")

    elif status == "missing":

        st.warning("MISSING")

    else:

        st.info(str(status))


    agreement_count = validation_result.get(
        "agreement_count"
    )

    source_count = validation_result.get(
        "source_count"
    )

    if agreement_count is not None:

        st.write(
            f"**Agreement:** "
            f"{agreement_count} / {source_count} sources"
        )


    reason = validation_result.get("reason")

    if reason:

        st.write(f"**Reason:** {reason}")


    # --------------------------------------------------
    # Evidence
    # --------------------------------------------------

    evidence = validation_result.get("evidence", [])

    if evidence:

        st.subheader("Evidence")

        for item in evidence:

            st.write(
                f"{item['source']} → "
                f"{item['value']} {item['unit']}"
            )