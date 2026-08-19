from collections import Counter
from typing import Any

def validate_weight(weight_values):
    """
    Compare normalized weight values from multiple sources.

    Parameters:
        weight_values: list of dictionaries containing:
            {
                "source": str,
                "value": float,
                "unit": str
            }

    Returns:
        dict: Validation result.
    """

    available_values = [
        item for item in weight_values
        if item.get("value") is not None
        and item.get("unit") is not None
    ]

    if not available_values:
        return {
            "status": "missing",
            "reason": "No source provided a valid weight.",
            "evidence": []
        }

    normalized_values = [
        (
            item["value"],
            item["unit"].lower()
        )
        for item in available_values
    ]

    counts = Counter(normalized_values)

    most_common_value, agreement_count = counts.most_common(1)[0]

    if len(counts) == 1:
        status = "agreement"
        reason = "All available sources agree on the weight."

    else:
        status = "conflict"
        reason = "Sources provide different weight values."

    return {
        "status": status,
        "agreement_count": agreement_count,
        "source_count": len(available_values),
        "value": {
            "value": most_common_value[0],
            "unit": most_common_value[1]
        },
        "reason": reason,
        "evidence": available_values
    }

def _normalize_text(value: Any) -> str | None:
    """Normalize textual values for comparison."""

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return " ".join(value.lower().split())


def _normalize_identifier(value: Any) -> str | None:
    """Normalize identifiers without changing their meaning."""

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value.upper().replace(" ", "")


def _normalize_value(field: str, value: Any) -> Any:
    """Apply field-specific normalization."""

    if value is None:
        return None

    identifier_fields = {
        "model_number",
        "product_code",
        "upc",
        "ean",
        "gtin",
        "sku",
    }

    if field in identifier_fields:
        return _normalize_identifier(value)

    return _normalize_text(value)


def validate_field(field: str, observations: list[dict]) -> dict:
    """
    Validate one product field across multiple source observations.

    Each observation should contain:
        {
            "field": str,
            "value": Any,
            "unit": str | None,
            "source_url": str | None,
            "source_type": str | None
        }
    """

    available = [
        item
        for item in observations
        if _normalize_value(field, item.get("value")) is not None
    ]

    if not available:
        return {
            "field": field,
            "status": "missing",
            "value": None,
            "agreement_count": 0,
            "source_count": 0,
            "confidence": 0.0,
            "reason": "No source provided a valid value.",
            "evidence": observations,
        }

    normalized_values = [
        _normalize_value(field, item.get("value"))
        for item in available
    ]

    counts = Counter(normalized_values)

    most_common_value, agreement_count = counts.most_common(1)[0]

    source_count = len(available)

    if len(counts) == 1:
        if source_count == 1:
            status = "partial"
            reason = (
                "Only one source provided a value; "
                "independent source agreement could not be established."
            )
        else:
            status = "agreement"
            reason = (
                "All available sources agree on the field value."
            )
    else:
        status = "conflict"
        reason = (
            "Sources provide different values for this field."
        )

    confidence = agreement_count / source_count

    selected_value = next(
        item.get("value")
        for item in available
        if _normalize_value(field, item.get("value")) == most_common_value
    )

    selected_unit = next(
        (
            item.get("unit")
            for item in available
            if _normalize_value(field, item.get("value"))
            == most_common_value
        ),
        None,
    )

    return {
        "field": field,
        "status": status,
        "value": selected_value,
        "unit": selected_unit,
        "agreement_count": agreement_count,
        "source_count": source_count,
        "confidence": round(confidence, 2),
        "reason": reason,
        "evidence": available,
    }

def validate_product(
    field_observations: dict[str, list[dict]],
) -> dict[str, dict]:
    """
    Validate multiple product fields.

    Parameters:
        field_observations:
            Dictionary mapping field names to source observations.

            Example:
            {
                "brand": [
                    {
                        "field": "brand",
                        "value": "Diablo",
                        "source_url": "...",
                        "source_type": "manufacturer",
                    },
                    ...
                ],
                "gtin": [
                    ...
                ],
            }

    Returns:
        Dictionary mapping each field name to its validation result.
    """

    results = {}

    for field, observations in field_observations.items():
        results[field] = validate_field(
            field,
            observations,
        )

    return results