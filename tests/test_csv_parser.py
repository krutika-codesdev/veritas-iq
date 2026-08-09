import sys

sys.path.insert(0, "src")

from parser.csv_parser import extract_records_from_csv


with open("tests/sample_products.csv", "rb") as csv_file:

    records = extract_records_from_csv(csv_file)

    print("Extracted records:")
    print(records)