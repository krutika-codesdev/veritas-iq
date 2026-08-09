import sys

sys.path.insert(0, "src")

from parser.csv_parser import extract_records_from_csv
from parser.excel_parser import extract_records_from_excel
from processing.mapper import (
    map_record_to_common_format,
    map_ai_result_to_common_format,
)
from processing.normalizer import normalize_weight
from processing.validator import validate_weight
from processing.matcher import products_match


# --------------------------------------------------
# 1. Simulated PDF / Gemini result
# --------------------------------------------------

pdf_result = {
    "product_name": "Samsung Galaxy Z Fold8 Ultra 5G",
    "brand": "Samsung",
    "weight": {
        "value": 215,
        "unit": "g",
        "qualifier": "approximate",
    },
}

pdf_common = map_ai_result_to_common_format(pdf_result)


# --------------------------------------------------
# 2. Load CSV
# --------------------------------------------------

with open("tests/sample_products.csv", "rb") as csv_file:
    csv_records = extract_records_from_csv(csv_file)

csv_common_records = [
    map_record_to_common_format(record)
    for record in csv_records
]


# --------------------------------------------------
# 3. Load Excel
# --------------------------------------------------

excel_records = extract_records_from_excel(
    "tests/sample_products.xlsx"
)

excel_common_records = [
    map_record_to_common_format(record)
    for record in excel_records
]


# --------------------------------------------------
# 4. Build a single collection of all sources
# --------------------------------------------------

all_records = [
    {
        "source": "PDF",
        "record": pdf_common,
    }
]

all_records.extend(
    {
        "source": "CSV",
        "record": record,
    }
    for record in csv_common_records
)

all_records.extend(
    {
        "source": "Excel",
        "record": record,
    }
    for record in excel_common_records
)


# --------------------------------------------------
# 5. Dynamically find a product appearing
#    across multiple sources
# --------------------------------------------------

matched_group = None

for base_item in all_records:
    base_record = base_item["record"]

    matches = []

    for candidate_item in all_records:
        candidate_record = candidate_item["record"]

        if products_match(base_record, candidate_record):
            matches.append(candidate_item)

    # We want a product represented in all 3 sources.
    sources = {
        item["source"]
        for item in matches
    }

    if {"PDF", "CSV", "Excel"}.issubset(sources):
        matched_group = matches
        break


# --------------------------------------------------
# 6. Ensure dynamic matching succeeded
# --------------------------------------------------

assert matched_group is not None, (
    "Could not dynamically match the same product "
    "across PDF, CSV and Excel."
)


# --------------------------------------------------
# 7. Collect and normalize weights
# --------------------------------------------------

weight_values = []

for item in matched_group:
    source = item["source"]
    record = item["record"]

    raw_weight = record.get("weight")

    if not raw_weight:
        continue

    # PDF weight is already represented as a structured object.
    if isinstance(raw_weight, dict):
        weight_input = raw_weight

    # CSV / Excel weights are stored as values such as "218 g".
    else:
        weight_input = {
            "value": raw_weight,
            "unit": "g",
        }

    normalized_weight = normalize_weight(weight_input)

    if normalized_weight:
        weight_values.append(
            {
                "source": source,
                "value": normalized_weight.value,
                "unit": normalized_weight.unit,
            }
        )


# --------------------------------------------------
# 8. Validate the matched product
# --------------------------------------------------

result = validate_weight(weight_values)


# --------------------------------------------------
# 9. Display result
# --------------------------------------------------

matched_product_names = [
    item["record"].get("product_name")
    for item in matched_group
]

print("Matched product names:")
for name in matched_product_names:
    print(f"- {name}")

print("\nWeight values:")
for value in weight_values:
    print(value)

print("\nValidation result:")
print(result)


# --------------------------------------------------
# 10. Expected MVP behavior
# --------------------------------------------------

assert len(weight_values) == 3, (
    "Expected weight values from PDF, CSV and Excel."
)

assert result["status"] == "conflict", (
    f"Expected conflict, got: {result}"
)

assert result["agreement_count"] == 2
assert result["source_count"] == 3