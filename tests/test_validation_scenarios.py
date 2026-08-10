import sys

sys.path.insert(0, "src")

from processing.normalizer import normalize_weight
from processing.validator import validate_weight
from processing.health_score import calculate_health_score


def build_weight_values(raw_weights):
    normalized = []

    for source, weight in raw_weights:
        result = normalize_weight(weight)

        if result:
            normalized.append(
                {
                    "source": source,
                    "value": result.value,
                    "unit": result.unit,
                }
            )

    return normalized


def run_scenario(name, raw_weights, expected_status, expected_score):
    weight_values = build_weight_values(raw_weights)

    validation_result = validate_weight(weight_values)

    health_score = calculate_health_score(
        weight_values,
        validation_result,
        expected_source_count=3,
    )

    print(f"\n--- {name} ---")

    print("Normalized values:")
    for item in weight_values:
        print(item)

    print("\nValidation:")
    print(validation_result)

    print("\nHealth Score:")
    print(health_score)

    assert validation_result["status"] == expected_status
    assert health_score["score"] == expected_score

    print(f"PASS: {name}")


# ==================================================
# Scenario 1: Agreement
# ==================================================

run_scenario(
    "Agreement",
    [
        ("PDF", {"value": "215", "unit": "g"}),
        ("CSV", {"value": "0.215", "unit": "kg"}),
        ("Excel", {"value": "215000", "unit": "mg"}),
    ],
    expected_status="agreement",
    expected_score=100.0,
)


# ==================================================
# Scenario 2: Conflict
# ==================================================

run_scenario(
    "Conflict",
    [
        ("PDF", {"value": "215", "unit": "g"}),
        ("CSV", {"value": "0.218", "unit": "kg"}),
        ("Excel", {"value": "215000", "unit": "mg"}),
    ],
    expected_status="conflict",
    expected_score=86.7,
)


# ==================================================
# Scenario 3: Missing source
# ==================================================

run_scenario(
    "Missing source",
    [
        ("PDF", {"value": "215", "unit": "g"}),
        ("CSV", {"value": "0.215", "unit": "kg"}),
        ("Excel", {"value": "Unknown", "unit": "g"}),
    ],
    expected_status="agreement",
    expected_score=90.0,
)


print("\nAll validation scenarios passed.")