from collections import Counter


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