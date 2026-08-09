FIELD_ALIASES = {
    "product_name": [
        "product_name",
        "name",
        "product",
        "item_name"
    ],
    "brand": [
        "brand",
        "brand_name"
    ],
    "manufacturer": [
        "manufacturer",
        "manufacturer_name"
    ],
    "model_number": [
        "model_number",
        "model",
        "model_no"
    ],
    "category": [
        "category",
        "product_category",
        "type"
    ],
    "weight": [
        "weight",
        "mass"
    ],
    "product_code": [
        "product_code",
        "product_id",
        "sku"
    ]
}


def normalize_column_name(column_name):
    """
    Convert a source column name into a consistent format.
    """

    return column_name.strip().lower().replace(" ", "_")


def map_record_to_common_format(record):
    """
    Map a raw CSV/Excel record into the common product representation.

    Unrecognized columns are ignored for now.
    """

    common_record = {}

    normalized_record = {
        normalize_column_name(key): value
        for key, value in record.items()
    }

    for common_field, aliases in FIELD_ALIASES.items():

        for alias in aliases:

            if alias in normalized_record:

                value = normalized_record[alias]

                if value is not None and str(value).strip() != "":
                    common_record[common_field] = value

                break

    return common_record


def map_ai_result_to_common_format(ai_result):
    """
    Map Gemini's structured product output
    into the common product representation.
    """

    common_record = {}

    fields = [
        "product_name",
        "brand",
        "manufacturer",
        "model_number",
        "product_code",
        "category"
    ]

    for field in fields:

        value = ai_result.get(field)

        if value is not None and str(value).strip() != "":
            common_record[field] = value

    if "weight" in ai_result and ai_result["weight"] is not None:
        common_record["weight"] = ai_result["weight"]

    return common_record