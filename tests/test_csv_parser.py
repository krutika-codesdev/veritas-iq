from pathlib import Path

from parser.csv_parser import extract_records_from_csv


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_extract_records_from_csv():
    csv_file = PROJECT_ROOT / "tests" / "sample_products.csv"

    with csv_file.open("rb") as file:
        records = extract_records_from_csv(file)

    assert isinstance(records, list)
    assert len(records) > 0
    assert isinstance(records[0], dict)