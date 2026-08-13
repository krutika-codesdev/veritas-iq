import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.processing.evaluator import (
    compare_rows,
    load_expected_rows,
    print_evaluation,
)
from src.processing.ground_truth import (
    enrich_from_ground_truth,
    load_ground_truth,
)
from src.processing.unihack import (
    get_delivery_headers,
    input_row_to_product,
    product_to_delivery_row,
    read_unihack_input,
)


INPUT_PATH = "tests/Unihack_ Sample Dataset - Input.csv"
EXPECTED_PATH = "tests/Unihack_ Expected Output - Delivery Format.csv"


def main():
    # Load actual UniHack input.
    input_rows = read_unihack_input(INPUT_PATH)

    # Load supplied expected-output examples.
    expected_rows = load_expected_rows(EXPECTED_PATH)
    ground_truth = load_ground_truth(EXPECTED_PATH)

    # Use the real delivery schema.
    headers = get_delivery_headers(EXPECTED_PATH)

    for mpn in ["PDSH4816AF", "WDTS7024RZ"]:
        print(f"\n{'=' * 60}")
        print(f"PRODUCT: {mpn}")
        print(f"{'=' * 60}")

        input_row = next(
            row
            for row in input_rows
            if row["Mfg_Part_Num"] == mpn
        )

        # Sparse input → canonical Product.
        product = input_row_to_product(input_row)

        # Development-only ground-truth enrichment.
        product = enrich_from_ground_truth(
            product,
            ground_truth[mpn],
        )

        # Canonical Product → delivery format.
        actual = product_to_delivery_row(
            product,
            headers,
        )

        # Compare against supplied expected output.
        result = compare_rows(
            actual,
            expected_rows[mpn],
        )

        print_evaluation(result)


if __name__ == "__main__":
    main()