import sys

sys.path.insert(0, "src")

from processing.normalizer import normalize_weight


test_cases = [
    {"value": "Approx. 215", "unit": "g"},
    {"value": "500", "unit": "g"},
    {"value": "1.5", "unit": "kg"},
    {"value": "2.2", "unit": "lb"},
    {"value": "Unknown", "unit": "g"},
]

for weight in test_cases:
    result = normalize_weight(weight)

    print(f"Input: {weight}")
    print(f"Output: {result}")
    print("-" * 40)