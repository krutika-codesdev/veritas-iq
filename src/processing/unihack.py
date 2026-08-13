import csv
from pathlib import Path
from typing import Any

from src.models.schema import (
    Classification,
    Evidence,
    Product,
    ProductAttribute,
    ProductContent,
)


UNIHACK_INPUT_FIELDS = [
    "Mfg_Part_Num",
    "Part_Desc",
    "E1_Brand",
    "Unilog_Brand",
    "DIB_Brand",
    "Part_Manuf",
]

ATTRIBUTE_SLOTS = 50


def clean_placeholder(value: Any) -> str | None:
    """Convert known catalogue placeholders to None."""

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    placeholders = {
        "-- unbranded --",
        "-- no unilog brand --",
        "-- no dib brand --",
        "-- no brand --",
        "-- no manufacturer --",
        "n/a",
        "na",
        "null",
        "none",
        "-",
    }

    if value.lower() in placeholders:
        return None

    return value


def input_row_to_product(row: dict[str, Any]) -> Product:
    """
    Convert one UniHack six-column input row into the canonical
    VeritasIQ Product model.

    The canonical fields use cleaned values, while source_fields
    preserves the original input values for exact delivery output.
    """

    cleaned = {
        field: clean_placeholder(row.get(field))
        for field in UNIHACK_INPUT_FIELDS
    }

    original = {
        field: (
            str(row.get(field)).strip()
            if row.get(field) is not None
            else None
        )
        for field in UNIHACK_INPUT_FIELDS
    }

    return Product(
        product_name=cleaned["Part_Desc"],
        product_code=cleaned["Mfg_Part_Num"],
        model_number=cleaned["Mfg_Part_Num"],
        brand=cleaned["E1_Brand"],
        manufacturer=cleaned["Part_Manuf"],
        source_fields=original,
    )


def add_attribute(
    product: Product,
    label: str,
    value: str | float | int | None,
    unit: str | None = None,
    source_url: str | None = None,
    confidence: float | None = None,
) -> None:
    """Add one structured attribute."""

    if value is None:
        return

    if isinstance(value, str) and not value.strip():
        return

    product.attributes.append(
        ProductAttribute(
            label=label,
            value=value,
            unit=unit,
            source_url=source_url,
            confidence=confidence,
        )
    )


def add_evidence(
    product: Product,
    url: str | None,
    source_type: str | None = None,
    description: str | None = None,
) -> None:
    """Attach one evidence source."""

    if not url:
        return

    product.evidence.append(
        Evidence(
            url=url,
            source_type=source_type,
            description=description,
        )
    )


def set_classification(
    product: Product,
    dept: str | None = None,
    class_name: str | None = None,
    fine: str | None = None,
    classpath: str | None = None,
) -> None:
    """Attach taxonomy information."""

    if not any([dept, class_name, fine, classpath]):
        return

    product.classification = Classification(
        dept=dept,
        class_name=class_name,
        fine=fine,
        classpath=classpath,
    )


def set_content(
    product: Product,
    mobile: str | None = None,
    invoice: str | None = None,
    short: str | None = None,
    long: str | None = None,
    retail: str | None = None,
    marketing: str | None = None,
    features: list[str] | None = None,
) -> None:
    """Attach product content."""

    product.content = ProductContent(
        mobile=mobile,
        invoice=invoice,
        short=short,
        long=long,
        retail=retail,
        marketing=marketing,
        features=features or [],
    )


def get_delivery_headers(schema_csv_path: str | Path) -> list[str]:
    """
    Read the exact 252-column delivery schema from the supplied
    UniHack expected-output CSV.

    This prevents us from guessing or accidentally misspelling
    delivery column names.
    """

    path = Path(schema_csv_path)

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.reader(file)
        headers = next(reader)

    if len(headers) != 252:
        raise ValueError(
            f"Expected exactly 252 delivery columns, "
            f"but found {len(headers)}."
        )

    return headers


def product_to_delivery_row(
    product: Product,
    delivery_headers: list[str],
) -> dict[str, Any]:
    """
    Convert a canonical Product into the exact UniHack
    252-column delivery format.
    """

    if len(delivery_headers) != 252:
        raise ValueError(
            f"Expected 252 delivery columns, "
            f"but received {len(delivery_headers)}."
        )

    # Start with every official column.
    row = {header: None for header in delivery_headers}

    # ---------------------------------------------------------
    # Original six input fields
    # ---------------------------------------------------------

    for field in UNIHACK_INPUT_FIELDS:
        row[field] = product.source_fields.get(field)

    # ---------------------------------------------------------
    # Identity
    # ---------------------------------------------------------

    row["PART_NUMBER"] = product.part_number
    row["SKU - MY_PART_NUMBER"] = product.sku
    row["MANUFACTURER_PART_NUMBER"] = product.model_number
    row["ALTERNATE_PART_NUMBER"] = product.alternate_part_number

    # ---------------------------------------------------------
    # Manufacturer / brand
    # ---------------------------------------------------------

    row["MANUFACTURER_NAME"] = product.manufacturer
    row["BRAND_NAME"] = product.brand
    row["TRADE_NAME"] = product.trade_name

    # ---------------------------------------------------------
    # Classification
    # ---------------------------------------------------------

    if product.classification:
        row["Dept"] = product.classification.dept
        row["Class"] = product.classification.class_name
        row["Fine"] = product.classification.fine
        row["Classpath"] = product.classification.classpath

    # ---------------------------------------------------------
    # Commerce content
    # ---------------------------------------------------------

    if product.content:
        row["MOBILE_DESC"] = product.content.mobile
        row["INVOICE_DESC"] = product.content.invoice
        row["SHORT_DESC"] = product.content.short
        row["LONG_DESC1"] = product.content.long
        row["RETAIL_DESC"] = product.content.retail
        row["MARKETING_DESCRIPTION"] = product.content.marketing

        for index, feature in enumerate(
            product.content.features[:20],
            start=1,
        ):
            row[f"ITEM_FEATURES_{index}"] = feature

    row["With"] = product.with_text
    row["Standard/Approvals"] = product.standard_approvals

    # ---------------------------------------------------------
    # Product name
    # ---------------------------------------------------------

    row["Product Name"] = product.product_name

    # ---------------------------------------------------------
    # Dynamic attributes
    # ---------------------------------------------------------

    for index, attribute in enumerate(
        product.attributes[:ATTRIBUTE_SLOTS],
        start=1,
    ):
        row[f"ATTRIBUTE_LABEL {index}"] = attribute.label
        row[f"ATTRIBUTE_VALUE {index}"] = attribute.value
        row[f"ATTRIBUTE_UOM {index}"] = attribute.unit

    # ---------------------------------------------------------
    # Warranty
    # ---------------------------------------------------------

    if product.warranty:
        row["Warranty"] = product.warranty.coverage
        row["Warranty Information"] = product.warranty.coverage

    # ---------------------------------------------------------
    # Evidence / reference URLs
    # ---------------------------------------------------------

    evidence_urls = [
        evidence.url
        for evidence in product.evidence
        if evidence.url
    ]

    if evidence_urls:
        row["MFR URL"] = evidence_urls[0]

    for index, url in enumerate(
        evidence_urls[1:6],
        start=1,
    ):
        row[f"Ref URL {index}"] = url

    # ---------------------------------------------------------
    # Assets
    # ---------------------------------------------------------

    row["Product Image"] = product.product_image

    for index, image in enumerate(
        product.alternate_images[:4],
        start=1,
    ):
        row[f"Alternate Image {index}"] = image

    row["Specification Sheet"] = product.specification_sheet

    if product.actual_image is not None:
        row["Actual Image (Yes/No)"] = (
            "Yes" if product.actual_image else "No"
        )

    # ---------------------------------------------------------
    # Material / colour / size
    # ---------------------------------------------------------

    row["Material"] = product.material

    row["Color"] = (
        ", ".join(product.color)
        if product.color
        else None
    )

    row["Size"] = product.size

    # ---------------------------------------------------------
    # Dimensions
    # ---------------------------------------------------------

    if product.dimensions:
        row["LENGTH"] = product.dimensions.length
        row["LENGTH_UOM"] = product.dimensions.unit

        row["HEIGHT"] = product.dimensions.height
        row["HEIGHT_UOM"] = product.dimensions.unit

        row["WIDTH"] = product.dimensions.width
        row["WIDTH_UOM"] = product.dimensions.unit

    # ---------------------------------------------------------
    # Weight
    # ---------------------------------------------------------

    if product.weight:
        row["WEIGHT"] = product.weight.value
        row["WEIGHT_UOM"] = product.weight.unit

    # ---------------------------------------------------------
    # Country of origin
    # ---------------------------------------------------------

    row["Country Of Origin"] = product.country_of_origin

    return row

def read_unihack_input(
    path: str | Path,
) -> list[dict[str, str]]:
    """Read the UniHack input CSV."""

    path = Path(path)

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        return list(reader)


def write_delivery_csv(
    rows: list[dict[str, Any]],
    path: str | Path,
    delivery_headers: list[str],
) -> None:
    """Write rows using the exact official 252-column schema."""

    if not rows:
        raise ValueError("No delivery rows supplied.")

    if len(delivery_headers) != 252:
        raise ValueError(
            f"Expected 252 delivery columns, "
            f"but received {len(delivery_headers)}."
        )

    path = Path(path)

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=delivery_headers,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)