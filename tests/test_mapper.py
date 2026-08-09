import sys

sys.path.insert(0, "src")

from parser.csv_parser import extract_records_from_csv
from parser.excel_parser import extract_records_from_excel
from processing.mapper import map_record_to_common_format


print("CSV")
print("=" * 50)

with open("tests/sample_products.csv", "rb") as csv_file:

    csv_records = extract_records_from_csv(csv_file)

    for record in csv_records:

        mapped_record = map_record_to_common_format(record)

        print(mapped_record)


print("\nEXCEL")
print("=" * 50)

excel_records = extract_records_from_excel(
    "tests/sample_products.xlsx"
)

for record in excel_records:

    mapped_record = map_record_to_common_format(record)

    print(mapped_record)