import sys

sys.path.insert(0, "src")

from processing.matcher import products_match


tests = [
    {
        "name": "Same product, different naming",
        "record_a": {
            "product_name": "Galaxy Z Fold8 Ultra",
            "brand": "Samsung"
        },
        "record_b": {
            "product_name": "Samsung Galaxy Z Fold8 Ultra 5G",
            "brand": "Samsung"
        },
        "expected": True
    },
    {
        "name": "Different brand",
        "record_a": {
            "product_name": "Galaxy Z Fold8 Ultra",
            "brand": "Samsung"
        },
        "record_b": {
            "product_name": "iPhone 17",
            "brand": "Apple"
        },
        "expected": False
    },
    {
        "name": "Different product",
        "record_a": {
            "product_name": "Galaxy Z Fold8 Ultra",
            "brand": "Samsung"
        },
        "record_b": {
            "product_name": "Galaxy S26",
            "brand": "Samsung"
        },
        "expected": False
    }
]


for test in tests:

    result = products_match(
        test["record_a"],
        test["record_b"]
    )

    print(test["name"])
    print(f"Expected: {test['expected']}")
    print(f"Actual:   {result}")
    print("-" * 50)