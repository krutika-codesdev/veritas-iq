from pathlib import Path

from parser.excel_parser import extract_records_from_excel


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_extract_records_from_excel():
    excel_file = PROJECT_ROOT / "tests" / "sample_products.xlsx"

    records = extract_records_from_excel(excel_file)

    assert isinstance(records, list)
    assert len(records) > 0
    assert isinstance(records[0], dict)