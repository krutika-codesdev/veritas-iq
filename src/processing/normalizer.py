import re

from models.schema import Measurement


def normalize_weight(weight: dict | None) -> Measurement | None:
    if weight is None:
        return None

    raw_value = weight.get("value")
    unit = weight.get("unit")

    if raw_value is None:
        return None

    value_text = str(raw_value)

    match = re.search(r"\d+(?:\.\d+)?", value_text)

    if not match:
        return None

    numeric_value = float(match.group())

    qualifier = None

    if "approx" in value_text.lower():
        qualifier = "approximate"

    return Measurement(
        value=numeric_value,
        unit=unit,
        qualifier=qualifier
    )