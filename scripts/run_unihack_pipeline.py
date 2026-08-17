import csv
import sys
from pathlib import Path


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.ai.unihack_provider import enrich_unihack_product
from src.processing.unihack import (
    get_delivery_headers,
    product_to_delivery_row,
    read_unihack_input,
    write_delivery_csv,
)


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

INPUT_PATH = (
    PROJECT_ROOT
    / "tests"
    / "Unihack_ Sample Dataset - Input.csv"
)

SCHEMA_PATH = (
    PROJECT_ROOT
    / "tests"
    / "Unihack_ Expected Output - Delivery Format.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "tests"
    / "outputs"
    / "unihack_pipeline_output.csv"
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

# Start small.
# We can increase this after the pipeline passes.
MAX_ROWS = 1


def main() -> None:
    print("========================================")
    print("       VERITASIQ UNIHACK PIPELINE")
    print("========================================")
    print()

    # -----------------------------------------------------
    # Load official input
    # -----------------------------------------------------

    print("Loading official UniHack input...")

    input_rows = read_unihack_input(
        INPUT_PATH
    )

    print(f"Total input rows available: {len(input_rows)}")

    # -----------------------------------------------------
    # Load official delivery schema
    # -----------------------------------------------------

    print("Loading official delivery schema...")

    delivery_headers = get_delivery_headers(
        SCHEMA_PATH
    )

    print(
        f"Official delivery columns: "
        f"{len(delivery_headers)}"
    )

    # -----------------------------------------------------
    # Select rows
    # -----------------------------------------------------

    selected_rows = input_rows[:MAX_ROWS]

    print(
        f"Rows selected for this run: "
        f"{len(selected_rows)}"
    )

    print()

    delivery_rows = []

    # -----------------------------------------------------
    # Process each input row
    # -----------------------------------------------------

    for index, source_row in enumerate(
        selected_rows,
        start=1,
    ):
        mpn = source_row.get(
            "Mfg_Part_Num",
            "",
        )

        description = source_row.get(
            "Part_Desc",
            "",
        )

        manufacturer = source_row.get(
            "Part_Manuf",
            "",
        )

        print(
            f"[{index}/{len(selected_rows)}] "
            f"{mpn}"
        )
        print(
            f"    Description: {description}"
        )
        print(
            f"    Source/Manufacturer: "
            f"{manufacturer}"
        )

        try:
            # ---------------------------------------------
            # Enrichment
            # ---------------------------------------------

            product = enrich_unihack_product(
                mfg_part_num=mpn,
                part_desc=description,
                part_manuf=manufacturer,
                source_fields=source_row,
            )

            print(
                f"    Product: "
                f"{product.product_name}"
            )

            print(
                f"    Resolved manufacturer: "
                f"{product.manufacturer}"
            )

            print(
                f"    Attributes: "
                f"{len(product.attributes)}"
            )

            print(
                f"    Evidence sources: "
                f"{len(product.evidence)}"
            )

            # ---------------------------------------------
            # Convert to official 252-column format
            # ---------------------------------------------

            delivery_row = product_to_delivery_row(
                product,
                delivery_headers,
            )

            delivery_rows.append(
                delivery_row
            )

            print("    STATUS: SUCCESS")

        except Exception as exc:
            print(
                f"    STATUS: FAILED"
            )
            print(
                f"    ERROR: {exc}"
            )

        print()

    # -----------------------------------------------------
    # Write output
    # -----------------------------------------------------

    if not delivery_rows:
        raise RuntimeError(
            "No products were successfully enriched."
        )

    print("Writing delivery CSV...")

    write_delivery_csv(
        rows=delivery_rows,
        path=OUTPUT_PATH,
        delivery_headers=delivery_headers,
    )

    # -----------------------------------------------------
    # Final verification
    # -----------------------------------------------------

    print()
    print("========================================")
    print("              PIPELINE RESULT")
    print("========================================")
    print(
        f"Input rows available: "
        f"{len(input_rows)}"
    )
    print(
        f"Rows attempted: "
        f"{len(selected_rows)}"
    )
    print(
        f"Rows successfully enriched: "
        f"{len(delivery_rows)}"
    )
    print(
        f"Delivery columns: "
        f"{len(delivery_headers)}"
    )
    print(
        f"Output: "
        f"{OUTPUT_PATH}"
    )
    print("========================================")


if __name__ == "__main__":
    main()