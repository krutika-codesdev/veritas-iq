import re

from models.schema import Measurement


WEIGHT_CONVERSIONS_TO_GRAMS = {
    "g": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "kg": 1000.0,
    "kilogram": 1000.0,
    "kilograms": 1000.0,
    "mg": 0.001,
    "milligram": 0.001,
    "milligrams": 0.001,
}


def normalize_weight(weight: dict | None) -> Measurement | None:
    if weight is None:
        return None

    raw_value = weight.get("value")
    raw_unit = weight.get("unit")

    if raw_value is None or raw_unit is None:
        return None

    value_text = str(raw_value).strip()

    match = re.search(r"\d+(?:\.\d+)?", value_text)

    if not match:
        return None

    numeric_value = float(match.group())

    unit = str(raw_unit).strip().lower()

    conversion_factor = WEIGHT_CONVERSIONS_TO_GRAMS.get(unit)

    if conversion_factor is None:
        return None

    normalized_value = numeric_value * conversion_factor

    qualifier = None

    if "approx" in value_text.lower():
        qualifier = "approximate"

    return Measurement(
        value=normalized_value,
        unit="g",
        qualifier=qualifier,
    )