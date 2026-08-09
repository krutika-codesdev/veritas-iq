import sys

sys.path.insert(0, "src")

from processing.normalizer import normalize_weight
from processing.validator import validate_weight


weights = [
    {"source": "PDF", "weight": {"value": "215", "unit": "g"}},
    {"source": "CSV", "weight": {"value": "0.215", "unit": "kg"}},
    {"source": "Excel", "weight": {"value": "215000", "unit": "mg"}},
]


normalized_weights = []

for item in weights:
    result = normalize_weight(item["weight"])

    if result:
        normalized_weights.append({
            "source": item["source"],
            "value": result.value,
            "unit": result.unit,
        })


print("Normalized values:")

for item in normalized_weights:
    print(item)


print("\nValidation result:")

result = validate_weight(normalized_weights)

print(result)

assert result["status"] == "agreement"
assert result["agreement_count"] == 3
assert result["source_count"] == 3
assert result["value"]["value"] == 215.0
assert result["value"]["unit"] == "g"

print("\nPASS: mixed weight units correctly validate as agreement.")

print("\n--- Conflict case ---")

conflict_weights = [
    {"source": "PDF", "weight": {"value": "215", "unit": "g"}},
    {"source": "CSV", "weight": {"value": "0.218", "unit": "kg"}},
    {"source": "Excel", "weight": {"value": "215000", "unit": "mg"}},
]


normalized_conflict = []

for item in conflict_weights:
    result = normalize_weight(item["weight"])

    if result:
        normalized_conflict.append({
            "source": item["source"],
            "value": result.value,
            "unit": result.unit,
        })


print("Normalized conflict values:")

for item in normalized_conflict:
    print(item)


conflict_result = validate_weight(normalized_conflict)

print("\nConflict validation result:")
print(conflict_result)


assert conflict_result["status"] == "conflict"
assert conflict_result["agreement_count"] == 2
assert conflict_result["source_count"] == 3
assert conflict_result["value"]["value"] == 215.0
assert conflict_result["value"]["unit"] == "g"

print("\nPASS: mixed-unit conflict correctly detected.")