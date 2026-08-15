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
from src.processing.unihack import product_to_delivery_row


SCHEMA_PATH = (
    PROJECT_ROOT
    / "tests"
    / "Unihack_ Expected Output - Delivery Format.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "tests"
    / "outputs"
    / "3m_enriched_delivery.csv"
)


SOURCE_FIELDS = {
    "Mfg_Part_Num": "3MABR-7100075678",
    "Part_Desc": "3M 775L Stikit Film P150 - Cubitron II 50 Disc/Box",
    "E1_Brand": "-- Unbranded --",
    "Unilog_Brand": "-- No Unilog Brand --",
    "DIB_Brand": "-- No DIB Brand --",
    "Part_Manuf": "Jam Industrial Supply LLC",
}


def main() -> None:
    print("Loading official 252-column schema...")

    with SCHEMA_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        headers = next(csv.reader(file))

    if len(headers) != 252:
        raise ValueError(
            f"Expected 252 headers, found {len(headers)}."
        )

    print("Running UniHack enrichment provider...")

    product = enrich_unihack_product(
        mfg_part_num=SOURCE_FIELDS["Mfg_Part_Num"],
        part_desc=SOURCE_FIELDS["Part_Desc"],
        part_manuf=SOURCE_FIELDS["Part_Manuf"],
        source_fields=SOURCE_FIELDS,
    )

    print("Building 252-column delivery row...")

    delivery_row = product_to_delivery_row(
        product,
        headers,
    )

    if len(delivery_row) != 252:
        raise ValueError(
            f"Expected 252 output columns, "
            f"found {len(delivery_row)}."
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=headers,
            extrasaction="raise",
        )

        writer.writeheader()
        writer.writerow(delivery_row)

    populated = [
        (key, value)
        for key, value in delivery_row.items()
        if value is not None
        and str(value).strip()
    ]

    print()
    print("SUCCESS")
    print("-------")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Columns: {len(delivery_row)}")
    print(f"Populated fields: {len(populated)}")
    print()

    print("PRODUCT")
    print("-------")
    print(f"Name: {product.product_name}")
    print(f"Manufacturer: {product.manufacturer}")
    print(f"Brand: {product.brand}")
    print(f"MPN: {product.model_number}")
    print(f"Attributes: {len(product.attributes)}")
    print(f"Evidence sources: {len(product.evidence)}")

    print()
    print("IMPORTANT DELIVERY FIELDS")
    print("--------------------------")

    important_fields = [
        "Mfg_Part_Num",
        "Part_Desc",
        "Part_Manuf",
        "MANUFACTURER_NAME",
        "BRAND_NAME",
        "MANUFACTURER_PART_NUMBER",
        "Product Name",
        "MFR URL",
        "Ref URL 1",
        "Ref URL 2",
        "SHORT_DESC",
        "ATTRIBUTE_LABEL 1",
        "ATTRIBUTE_VALUE 1",
        "ATTRIBUTE_LABEL 2",
        "ATTRIBUTE_VALUE 2",
        "ATTRIBUTE_UOM 2",
        "ATTRIBUTE_LABEL 3",
        "ATTRIBUTE_VALUE 3",
        "ATTRIBUTE_LABEL 4",
        "ATTRIBUTE_VALUE 4",
        "ATTRIBUTE_UOM 4",
        "ATTRIBUTE_LABEL 5",
        "ATTRIBUTE_VALUE 5",
        "ATTRIBUTE_LABEL 6",
        "ATTRIBUTE_VALUE 6",
        "WIDTH",
        "WIDTH_UOM",
    ]

    for field in important_fields:
        value = delivery_row.get(field)

        if value is not None and str(value).strip():
            print(f"{field}: {value}")


if __name__ == "__main__":
    main()