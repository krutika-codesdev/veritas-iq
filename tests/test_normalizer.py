import sys

sys.path.insert(0, "src")

from processing.normalizer import normalize_weight


test_cases = [
    (
        {"value": "215", "unit": "g"},
        215.0,
        "g",
        None,
    ),
    (
        {"value": "215 grams", "unit": "grams"},
        215.0,
        "g",
        None,
    ),
    (
        {"value": "0.215", "unit": "kg"},
        215.0,
        "g",
        None,
    ),
    (
        {"value": "215000", "unit": "mg"},
        215.0,
        "g",
        None,
    ),
    (
        {"value": "Approx. 215", "unit": "g"},
        215.0,
        "g",
        "approximate",
    ),
]


for weight, expected_value, expected_unit, expected_qualifier in test_cases:

    result = normalize_weight(weight)

    assert result is not None

    assert result.value == expected_value
    assert result.unit == expected_unit
    assert result.qualifier == expected_qualifier

    print(f"PASS: {weight} → {result}")


invalid_cases = [
    {"value": "Unknown", "unit": "g"},
    {"value": "215", "unit": "lb"},
    {"value": "215", "unit": "oz"},
]


for weight in invalid_cases:

    result = normalize_weight(weight)

    assert result is None

    print(f"PASS: invalid input rejected → {weight}")