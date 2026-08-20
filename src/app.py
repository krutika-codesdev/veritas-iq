from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv
import io
import streamlit as st

from src.ai.unihack_provider import enrich_unihack_product
from src.processing.health_score import calculate_product_health_score

from src.processing.unihack import (
    get_delivery_headers,
    process_unihack_records,
    product_to_delivery_row,
    read_unihack_input,
    write_delivery_csv,
)
from src.parser.csv_parser import extract_records_from_csv
from src.parser.excel_parser import extract_records_from_excel

from src.processing.validator import validate_product_fields
from src.storage.database import init_db, save_product


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SCHEMA_PATH = (
    PROJECT_ROOT
    / "tests"
    / "Unihack_ Expected Output - Delivery Format.csv"
)

VALIDATION_FIELDS = [
    "product_name",
    "manufacturer",
    "brand",
    "model_number",
    "upc",
    "ean",
    "gtin",
    "weight",
]


st.set_page_config(
    page_title="VeritasIQ",
    page_icon="📦",
    layout="wide",
)


init_db()


st.title("VeritasIQ")
st.subheader("AI-Powered Product Intelligence for Industrial Commerce")

st.markdown(
    """
Turn sparse industrial product information into structured,
validated and evidence-backed product intelligence.
"""
)

st.divider()

st.header("1. Product Input")

input_mode = st.radio(
    "Choose input method",
    ["Manual Product", "CSV / XLSX Catalog"],
    horizontal=True,
)

if input_mode == "CSV / XLSX Catalog":

    uploaded_file = st.file_uploader(
        "Upload product catalog",
        type=["csv", "xlsx"],
        help=(
            "Expected fields include Mfg_Part_Num, Part_Desc, "
            "and Part_Manuf."
        ),
    )

    if uploaded_file is not None:

        if uploaded_file.name.lower().endswith(".csv"):
            records = extract_records_from_csv(uploaded_file)
        else:
            records = extract_records_from_excel(uploaded_file)

        st.info(
            f"Loaded {len(records)} product records."
        )

        process_catalog_clicked = st.button(
            "Process Catalog",
            type="primary",
            use_container_width=True,
        )

        if process_catalog_clicked:

            try:
                delivery_headers = get_delivery_headers(
                    SCHEMA_PATH
                )

                with st.spinner(
                    "Processing catalog..."
                ):
                    delivery_rows = process_unihack_records(
                        records=records,
                        delivery_headers=delivery_headers,
                        validation_fields=VALIDATION_FIELDS,
                    )

                st.session_state[
                    "batch_delivery_rows"
                ] = delivery_rows

                st.success(
                    f"Successfully processed "
                    f"{len(delivery_rows)} products."
                )

            except Exception as exc:
                st.error(
                    "Catalog processing is currently unavailable."
                )
                st.caption(
                    "No fixture or mocked result was substituted."
                )
                st.code(str(exc))

        if "batch_delivery_rows" in st.session_state:

            delivery_rows = st.session_state[
                "batch_delivery_rows"
            ]

            st.subheader("Catalog Results")

            st.metric(
                "Products Processed",
                len(delivery_rows),
            )

            output = io.StringIO()

            writer = csv.DictWriter(
                output,
                fieldnames=delivery_headers,
            )

            writer.writeheader()
            writer.writerows(delivery_rows)

            st.download_button(
                "Download 252-Column Catalog",
                data=output.getvalue(),
                file_name="veritasiq_catalog_delivery.csv",
                mime="text/csv",
                use_container_width=True,
            )

else:

    col1, col2 = st.columns(2)

    with col1:
        manufacturer = st.text_input(
            "Manufacturer / Source",
            placeholder="e.g. 3M",
        )

        mpn = st.text_input(
            "Manufacturer Part Number",
            placeholder="e.g. 3MABR-7100075678",
        )

    with col2:
        description = st.text_area(
            "Product Description",
            placeholder="Enter the available product description",
            height=120,
        )

    enrich_clicked = st.button(
        "Enrich Product",
        type="primary",
        use_container_width=True,
    )

    if enrich_clicked:

        if not mpn.strip():
            st.error(
                "Manufacturer Part Number is required."
            )
            st.stop()

        if not description.strip():
            st.error(
                "Product Description is required."
            )
            st.stop()

        source_fields = {
            "Mfg_Part_Num": mpn.strip(),
            "Part_Desc": description.strip(),
            "E1_Brand": None,
            "Unilog_Brand": None,
            "DIB_Brand": None,
            "Part_Manuf": (
                manufacturer.strip()
                or None
            ),
        }

        with st.spinner(
            "Enriching product using AI and "
            "web-grounded sources..."
        ):
            try:
                product = enrich_unihack_product(
                    mfg_part_num=mpn.strip(),
                    part_desc=description.strip(),
                    part_manuf=(
                        manufacturer.strip()
                        or None
                    ),
                    source_fields=source_fields,
                )

            except Exception as exc:
                st.error(
                    "Product enrichment is currently unavailable."
                )

                st.caption(
                    "No fixture or mocked result was used."
                )

                st.code(str(exc))

                st.stop()

        validation_results, _ = (
            validate_product_fields(
                product,
                VALIDATION_FIELDS,
            )
        )

        health_score = (
            calculate_product_health_score(
                validation_results,
                VALIDATION_FIELDS,
            )
        )

        st.session_state["product"] = product
        st.session_state[
            "validation_results"
        ] = validation_results
        st.session_state[
            "health_score"
        ] = health_score

        st.success("Product intelligence generated successfully.")

        st.subheader("Product Intelligence")

        product = st.session_state["product"]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Health Score", f"{st.session_state['health_score']:.1f}%")

        with col2:
            st.metric(
                "Evidence Sources",
                len(product.evidence),
            )

        with col3:
            st.metric(
                "Validated Fields",
                sum(
                    result.status == "validated"
                    for result in st.session_state["validation_results"]
                ),
            )

        st.write("### Core Product Information")

        product_info = {
            "Product Name": product.product_name,
            "Brand": product.brand,
            "Manufacturer": product.manufacturer,
            "Model Number": product.model_number,
            "Product Type": product.product_type,
            "Category": product.category,
            "Subcategory": product.subcategory,
            "UPC": product.upc,
            "EAN": product.ean,
            "GTIN": product.gtin,
            "Country of Origin": product.country_of_origin,
            "Intended Use": product.intended_use,
            "Material": product.material,
            "Size": product.size,
        }

        st.dataframe(
            {
                "Field": list(product_info.keys()),
                "Value": list(product_info.values()),
            },
            use_container_width=True,
            hide_index=True,
        )

        if product.classification:
            st.write("### Classification")

            st.dataframe(
                {
                    "Field": [
                        "Department",
                        "Class",
                        "Fine",
                        "Classpath",
                    ],
                    "Value": [
                        product.classification.dept,
                        product.classification.class_name,
                        product.classification.fine,
                        product.classification.classpath,
                    ],
                },
                use_container_width=True,
                hide_index=True,
            )

        if product.attributes:
            st.write("### Product Attributes")

            st.dataframe(
                [
                    {
                        "Attribute": attribute.label,
                        "Value": attribute.value,
                        "Unit": attribute.unit,
                        "Confidence": attribute.confidence,
                        "Source": attribute.source_url,
                    }
                    for attribute in product.attributes
                ],
                use_container_width=True,
                hide_index=True,
            )

        if product.content:
            st.write("### Commerce Content")

            if product.content.short:
                st.write("**Short Description**")
                st.write(product.content.short)

            if product.content.long:
                st.write("**Long Description**")
                st.write(product.content.long)

            if product.content.features:
                st.write("**Features**")
                for feature in product.content.features:
                    st.write(f"- {feature}")

        st.write("### Validation")

        validation_table = [
            {
                "Field": result.field,
                "Status": result.status,
                "Value": result.value,
                "Agreement": (
                    f"{result.agreement_count}/"
                    f"{result.source_count}"
                ),
                "Confidence": result.confidence,
                "Reason": result.reason,
            }
            for result in st.session_state["validation_results"]
        ]

        st.dataframe(
            validation_table,
            use_container_width=True,
            hide_index=True,
        )

        if product.evidence:
            st.write("### Evidence")

            for evidence in product.evidence:
                st.markdown(
                    f"**{evidence.source_type or 'Source'}** — "
                    f"{evidence.description or 'Supporting evidence'}"
                )
                st.write(evidence.url)

        st.write("### 252-Column Delivery Output")

        delivery_headers = get_delivery_headers(SCHEMA_PATH)

        delivery_row = product_to_delivery_row(
            product,
            delivery_headers,
        )

        output = io.StringIO()

        writer = csv.DictWriter(
            output,
            fieldnames=delivery_headers,
        )

        writer.writeheader()
        writer.writerow(delivery_row)

        st.download_button(
            "Download 252-Column Product",
            data=output.getvalue(),
            file_name="veritasiq_product_delivery.csv",
            mime="text/csv",
            use_container_width=True,
        )