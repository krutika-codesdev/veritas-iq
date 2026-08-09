import sys

sys.path.insert(0, "src")

from parser.csv_parser import extract_records_from_csv
from parser.excel_parser import extract_records_from_excel
from processing.mapper import (
    map_record_to_common_format,
    map_ai_result_to_common_format
)
from processing.normalizer import normalize_weight
from processing.validator import validate_weight


# --------------------------------------------------
# 1. Simulated PDF / Gemini result
# --------------------------------------------------

pdf_result = {
    "product_name": "Samsung Galaxy Z Fold8 Ultra 5G",
    "brand": "Samsung",
    "weight": {
        "value": 215,
        "unit": "g",
        "qualifier": "approximate"
    }
}

pdf_common = map_ai_result_to_common_format(pdf_result)


# --------------------------------------------------
# 2. CSV
# --------------------------------------------------

with open("tests/sample_products.csv", "rb") as csv_file:

    csv_records = extract_records_from_csv(csv_file)

    csv_common_records = [
        map_record_to_common_format(record)
        for record in csv_records
    ]


# --------------------------------------------------
# 3. Excel
# --------------------------------------------------

excel_records = extract_records_from_excel(
    "tests/sample_products.xlsx"
)

excel_common_records = [
    map_record_to_common_format(record)
    for record in excel_records
]


# --------------------------------------------------
# 4. Extract and normalize weights
# --------------------------------------------------

weight_values = []


# PDF

pdf_weight = normalize_weight(pdf_common["weight"])

if pdf_weight:
    weight_values.append({
        "source": "PDF",
        "value": pdf_weight.value,
        "unit": pdf_weight.unit
    })


# CSV

for record in csv_common_records:

    if record.get("product_name") == "Galaxy Z Fold8 Ultra":

        csv_weight = normalize_weight(
            {
                "value": record.get("weight"),
                "unit": "g"
            }
        )

        if csv_weight:
            weight_values.append({
                "source": "CSV",
                "value": csv_weight.value,
                "unit": csv_weight.unit
            })


# Excel

for record in excel_common_records:

    if record.get("product_name") == "Galaxy Z Fold8 Ultra":

        excel_weight = normalize_weight(
            {
                "value": record.get("weight"),
                "unit": "g"
            }
        )

        if excel_weight:
            weight_values.append({
                "source": "Excel",
                "value": excel_weight.value,
                "unit": excel_weight.unit
            })


# --------------------------------------------------
# 5. Validate
# --------------------------------------------------

result = validate_weight(weight_values)


print("Weight values:")
print(weight_values)

print("\nValidation result:")
print(result)