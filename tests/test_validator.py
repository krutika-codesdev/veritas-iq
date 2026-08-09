import sys

sys.path.insert(0, "src")

from processing.validator import validate_weight


test_cases = [
    {
        "name": "Agreement",
        "values": [
            {"source": "PDF", "value": 215.0, "unit": "g"},
            {"source": "CSV", "value": 215.0, "unit": "g"},
            {"source": "Excel", "value": 215.0, "unit": "g"},
        ]
    },
    {
        "name": "Conflict",
        "values": [
            {"source": "PDF", "value": 215.0, "unit": "g"},
            {"source": "CSV", "value": 218.0, "unit": "g"},
            {"source": "Excel", "value": 215.0, "unit": "g"},
        ]
    },
    {
        "name": "Missing",
        "values": []
    }
]


for test_case in test_cases:

    print(f"\n{test_case['name']}")
    print("=" * 50)

    result = validate_weight(test_case["values"])

    print(result)