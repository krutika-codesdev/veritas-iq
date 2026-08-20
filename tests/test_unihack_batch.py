import os
from pathlib import Path

from src.processing.health_score import calculate_product_health_score
from src.processing.unihack import (
    get_delivery_headers,
    process_unihack_records,
    read_unihack_input,
)
from src.processing.validator import validate_product_fields


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SCHEMA_PATH = (
    PROJECT_ROOT
    / "tests"
    / "Unihack_ Expected Output - Delivery Format.csv"
)

INPUT_PATH = (
    PROJECT_ROOT
    / "tests"
    / "Unihack_ Sample Dataset - Input.csv"
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


def test_unihack_batch_fixture_mode(monkeypatch):
    monkeypatch.setenv(
        "UNIHACK_PROVIDER",
        "fixture",
    )

    records = read_unihack_input(INPUT_PATH)

    # Only use the existing fixture-backed 3M product.
    records = [
        record
        for record in records
        if record.get("Mfg_Part_Num")
        == "3MABR-7100075678"
    ]

    assert len(records) == 1

    delivery_headers = get_delivery_headers(
        SCHEMA_PATH
    )

    delivery_rows = process_unihack_records(
        records=records,
        delivery_headers=delivery_headers,
        validation_fields=VALIDATION_FIELDS,
    )

    assert len(delivery_rows) == 1

    row = delivery_rows[0]

    assert len(row) == 252
    assert row["Mfg_Part_Num"] == "3MABR-7100075678"
    assert row["Part_Desc"]
    assert row["Part_Manuf"]