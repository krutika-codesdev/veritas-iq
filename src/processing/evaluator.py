import csv
from pathlib import Path
from typing import Any


def load_expected_rows(
    path: str | Path,
) -> dict[str, dict[str, str]]:
    """Load expected UniHack rows indexed by Mfg_Part_Num."""

    path = Path(path)

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = csv.DictReader(file)

        return {
            row["Mfg_Part_Num"]: row
            for row in rows
            if row.get("Mfg_Part_Num")
        }


def compare_rows(
    actual: dict[str, Any],
    expected: dict[str, Any],
) -> dict[str, Any]:
    """
    Compare two delivery-format rows field by field.

    Empty fields in the expected output are ignored because the
    competition does not require every one of the 252 fields to be
    populated for every product.
    """

    compared = 0
    matched = 0
    mismatched = []

    for field, expected_value in expected.items():
        expected_value = (
            str(expected_value).strip()
            if expected_value is not None
            else ""
        )

        if not expected_value:
            continue

        compared += 1

        actual_value = actual.get(field)

        actual_value = (
            str(actual_value).strip()
            if actual_value is not None
            else ""
        )

        if actual_value == expected_value:
            matched += 1
        else:
            mismatched.append(
                {
                    "field": field,
                    "expected": expected_value,
                    "actual": actual_value,
                }
            )

    accuracy = (
        matched / compared * 100
        if compared
        else 0.0
    )

    return {
        "compared": compared,
        "matched": matched,
        "mismatched": len(mismatched),
        "accuracy": round(accuracy, 2),
        "mismatches": mismatched,
    }


def print_evaluation(result: dict[str, Any]) -> None:
    """Print a readable evaluation summary."""

    print("\n=== UniHack Evaluation ===")
    print(f"Fields compared : {result['compared']}")
    print(f"Fields matched  : {result['matched']}")
    print(f"Fields different: {result['mismatched']}")
    print(f"Accuracy        : {result['accuracy']}%")

    if result["mismatches"]:
        print("\nMismatches:")

        for item in result["mismatches"]:
            print(f"\n{item['field']}")
            print(f"  Expected: {item['expected']}")
            print(f"  Actual:   {item['actual']}")