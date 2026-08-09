import sys

sys.path.insert(0, "src")

from processing.mapper import map_ai_result_to_common_format


ai_result = {
    "product_name": "Samsung Galaxy Z Fold8 Ultra 5G",
    "brand": "Samsung",
    "manufacturer": None,
    "model_number": None,
    "product_code": None,
    "category": None,
    "weight": {
        "value": 215,
        "unit": "g",
        "qualifier": "approximate"
    }
}


result = map_ai_result_to_common_format(ai_result)

print("AI result:")
print(ai_result)

print("\nCommon representation:")
print(result)