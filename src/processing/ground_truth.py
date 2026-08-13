import csv
from pathlib import Path

from src.processing.unihack import input_row_to_product
from src.models.schema import (
    Classification,
    Evidence,
    Product,
    ProductAttribute,
    ProductContent,
    Warranty,
)


def load_ground_truth(path: str | Path) -> dict[str, dict[str, str]]:
    """Load the supplied UniHack expected-output examples by MPN."""

    path = Path(path)

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = csv.DictReader(file)

        result = {}

        for row in rows:
            mpn = row.get("Mfg_Part_Num")

            if mpn:
                result[mpn.strip()] = row

    return result


def enrich_from_ground_truth(
    product: Product,
    expected_row: dict[str, str],
) -> Product:
    """
    Development/test provider.

    Converts the supplied UniHack expected-output row into the
    canonical Product model so that the pipeline can be evaluated
    locally without using the live enrichment API.
    """

    # ---------------------------------------------------------
    # Identity
    # ---------------------------------------------------------

    product.part_number = expected_row.get("PART_NUMBER") or None
    product.sku = expected_row.get("SKU - MY_PART_NUMBER") or None
    product.alternate_part_number = (
        expected_row.get("ALTERNATE_PART_NUMBER") or None
    )

    product.manufacturer = (
        expected_row.get("MANUFACTURER_NAME")
        or product.manufacturer
    )

    product.brand = (
        expected_row.get("BRAND_NAME")
        or product.brand
    )

    product.trade_name = (
        expected_row.get("TRADE_NAME") or None
    )

    product.model_number = (
        expected_row.get("MANUFACTURER_PART_NUMBER")
        or product.model_number
    )

    product.product_name = (
        expected_row.get("Product Name")
        or product.product_name
    )

    # ---------------------------------------------------------
    # Classification
    # ---------------------------------------------------------

    product.classification = Classification(
        dept=expected_row.get("Dept") or None,
        class_name=expected_row.get("Class") or None,
        fine=expected_row.get("Fine") or None,
        classpath=expected_row.get("Classpath") or None,
    )

    # ---------------------------------------------------------
    # Attributes
    # ---------------------------------------------------------

    product.attributes.clear()

    for index in range(1, 51):
        label = expected_row.get(
            f"ATTRIBUTE_LABEL {index}"
        )
        value = expected_row.get(
            f"ATTRIBUTE_VALUE {index}"
        )
        unit = expected_row.get(
            f"ATTRIBUTE_UOM {index}"
        )

        if label:
            product.attributes.append(
                ProductAttribute(
                    label=label,
                    value=value or None,
                    unit=unit or None,
                )
            )

    # ---------------------------------------------------------
    # Commerce content
    # ---------------------------------------------------------

    features = []

    for index in range(1, 21):
        feature = expected_row.get(
            f"ITEM_FEATURES_{index}"
        )

        if feature:
            features.append(feature)

    product.content = ProductContent(
        mobile=expected_row.get("MOBILE_DESC") or None,
        invoice=expected_row.get("INVOICE_DESC") or None,
        short=expected_row.get("SHORT_DESC") or None,
        long=expected_row.get("LONG_DESC1") or None,
        retail=expected_row.get("RETAIL_DESC") or None,
        marketing=expected_row.get(
            "MARKETING_DESCRIPTION"
        ) or None,
        features=features,
    )

    product.with_text = (
        expected_row.get("With") or None
    )

    product.standard_approvals = (
        expected_row.get("Standard/Approvals") or None
    )

    # ---------------------------------------------------------
    # Warranty
    # ---------------------------------------------------------

    warranty_text = expected_row.get("Warranty")

    if warranty_text:
        product.warranty = Warranty(
            coverage=warranty_text
        )

    # ---------------------------------------------------------
    # Assets
    # ---------------------------------------------------------

    product.product_image = (
        expected_row.get("Product Image") or None
    )

    product.alternate_images = []

    for index in range(1, 5):
        image = expected_row.get(
            f"Alternate Image {index}"
        )

        if image:
            product.alternate_images.append(image)

    product.specification_sheet = (
        expected_row.get("Specification Sheet")
        or None
    )

    actual_image = expected_row.get(
        "Actual Image (Yes/No)"
    )

    if actual_image:
        product.actual_image = (
            actual_image.strip().lower() == "yes"
        )

    # ---------------------------------------------------------
    # Evidence
    # ---------------------------------------------------------

    product.evidence.clear()

    evidence_columns = [
        ("MFR URL", "manufacturer"),
        ("Ref URL 1", "reference"),
        ("Ref URL 2", "reference"),
        ("Ref URL 3", "reference"),
        ("Ref URL 4", "reference"),
        ("Ref URL 5", "reference"),
    ]

    for column, source_type in evidence_columns:
        url = expected_row.get(column)

        if url:
            product.evidence.append(
                Evidence(
                    url=url,
                    source_type=source_type,
                )
            )

    return product