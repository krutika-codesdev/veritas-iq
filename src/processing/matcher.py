def normalize_product_name(product_name):
    """
    Normalize a product name for basic comparison.
    """

    if not product_name:
        return ""

    return (
        str(product_name)
        .lower()
        .replace("-", " ")
        .replace("_", " ")
        .strip()
    )


def products_match(record_a, record_b):
    """
    Determine whether two product records likely refer
    to the same product.

    Uses brand and product-name containment for the MVP.
    """

    brand_a = str(record_a.get("brand", "")).strip().lower()
    brand_b = str(record_b.get("brand", "")).strip().lower()

    name_a = normalize_product_name(
        record_a.get("product_name")
    )
    name_b = normalize_product_name(
        record_b.get("product_name")
    )

    if not brand_a or not brand_b:
        return False

    if brand_a != brand_b:
        return False

    if not name_a or not name_b:
        return False

    return name_a in name_b or name_b in name_a