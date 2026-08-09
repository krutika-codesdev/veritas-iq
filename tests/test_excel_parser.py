import sys

sys.path.insert(0, "src")

from parser.excel_parser import extract_records_from_excel


records = extract_records_from_excel("tests/CSV_UniHack.xlsx")

print("Extracted records:")
print(records)