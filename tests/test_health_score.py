import sys

sys.path.insert(0, "src")

from processing.health_score import calculate_health_score


# ==================================================
# Scenario 1: Full agreement
# ==================================================

agreement_weights = [
    {"source": "PDF", "value": 215.0, "unit": "g"},
    {"source": "CSV", "value": 215.0, "unit": "g"},
    {"source": "Excel", "value": 215.0, "unit": "g"},
]

agreement_result = {
    "status": "agreement",
    "agreement_count": 3,
    "source_count": 3,
    "evidence": [
        {"source": "PDF", "value": 215.0, "unit": "g"},
        {"source": "CSV", "value": 215.0, "unit": "g"},
        {"source": "Excel", "value": 215.0, "unit": "g"},
    ],
}


agreement_score = calculate_health_score(
    agreement_weights,
    agreement_result,
    expected_source_count=3,
)

print("# Full Agreement")
print(agreement_score)

assert agreement_score["score"] == 100.0
assert agreement_score["components"]["agreement"] == 100.0
assert agreement_score["components"]["completeness"] == 100.0
assert agreement_score["components"]["evidence"] == 100.0


# ==================================================
# Scenario 2: Conflict
# ==================================================

conflict_weights = [
    {"source": "PDF", "value": 215.0, "unit": "g"},
    {"source": "CSV", "value": 218.0, "unit": "g"},
    {"source": "Excel", "value": 215.0, "unit": "g"},
]

conflict_result = {
    "status": "conflict",
    "agreement_count": 2,
    "source_count": 3,
    "evidence": [
        {"source": "PDF", "value": 215.0, "unit": "g"},
        {"source": "CSV", "value": 218.0, "unit": "g"},
        {"source": "Excel", "value": 215.0, "unit": "g"},
    ],
}


conflict_score = calculate_health_score(
    conflict_weights,
    conflict_result,
    expected_source_count=3,
)

print("\n# Conflict")
print(conflict_score)

assert conflict_score["score"] == 86.7
assert conflict_score["components"]["agreement"] == 66.7
assert conflict_score["components"]["completeness"] == 100.0
assert conflict_score["components"]["evidence"] == 100.0


# ==================================================
# Scenario 3: Missing source
# ==================================================

missing_weights = [
    {"source": "PDF", "value": 215.0, "unit": "g"},
    {"source": "CSV", "value": 215.0, "unit": "g"},
]

missing_result = {
    "status": "agreement",
    "agreement_count": 2,
    "source_count": 2,
    "evidence": [
        {"source": "PDF", "value": 215.0, "unit": "g"},
        {"source": "CSV", "value": 215.0, "unit": "g"},
    ],
}


missing_score = calculate_health_score(
    missing_weights,
    missing_result,
    expected_source_count=3,
)

print("\n# Missing Source")
print(missing_score)

assert missing_score["score"] == 90.0
assert missing_score["components"]["agreement"] == 100.0
assert missing_score["components"]["completeness"] == 66.7
assert missing_score["components"]["evidence"] == 100.0


# ==================================================
# Scenario 4: No valid observations
# ==================================================

empty_result = {
    "status": "missing",
    "reason": "No source provided a valid weight.",
    "evidence": [],
}


empty_score = calculate_health_score(
    [],
    empty_result,
    expected_source_count=3,
)

print("\n# No Valid Observations")
print(empty_score)

assert empty_score["score"] == 0.0
assert empty_score["components"]["agreement"] == 0.0
assert empty_score["components"]["completeness"] == 0.0
assert empty_score["components"]["evidence"] == 0.0


print("\nAll Health Score tests passed.")