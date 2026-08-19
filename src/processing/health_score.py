def calculate_health_score(
    weight_values: list[dict],
    validation_result: dict,
    expected_source_count: int,
) -> dict:
    """
    Calculate an explainable product health score.

    Components:
    - Agreement: 40%
    - Completeness: 30%
    - Evidence: 30%
    """

    valid_count = len(weight_values)

    # --------------------------------------------------
    # Agreement
    # --------------------------------------------------

    if valid_count > 0:
        agreement_count = validation_result.get(
            "agreement_count",
            valid_count,
        )

        agreement_score = (
            agreement_count / valid_count
        ) * 100

    else:
        agreement_score = 0.0

    # --------------------------------------------------
    # Completeness
    # --------------------------------------------------

    if expected_source_count > 0:
        completeness_score = (
            valid_count / expected_source_count
        ) * 100

    else:
        completeness_score = 0.0

    # --------------------------------------------------
    # Evidence
    # --------------------------------------------------

    evidence = validation_result.get("evidence", [])

    if valid_count > 0:
        evidence_score = (
            len(evidence) / valid_count
        ) * 100

    else:
        evidence_score = 0.0

    # --------------------------------------------------
    # Weighted score
    # --------------------------------------------------

    weighted_agreement = agreement_score * 0.40
    weighted_completeness = completeness_score * 0.30
    weighted_evidence = evidence_score * 0.30

    score = (
        weighted_agreement
        + weighted_completeness
        + weighted_evidence
    )

    # Keep score within 0–100.
    score = min(max(score, 0.0), 100.0)

    # --------------------------------------------------
    # Explanation
    # --------------------------------------------------

    if valid_count == 0:
        reason = (
            "No valid weight observations were available."
        )

    elif validation_result.get("status") == "conflict":
        reason = (
            f"{validation_result.get('agreement_count', 0)} "
            f"of {valid_count} available sources agree; "
            "the remaining source(s) report different values."
        )

    elif valid_count < expected_source_count:
        reason = (
            f"{valid_count} of {expected_source_count} "
            "expected sources provided a valid weight."
        )

    else:
        reason = (
            "All available sources agree and provide "
            "source-level evidence."
        )

    return {
        "score": round(score, 1),
        "components": {
            "agreement": round(agreement_score, 1),
            "completeness": round(completeness_score, 1),
            "evidence": round(evidence_score, 1),
        },
        "weighted_components": {
            "agreement": round(weighted_agreement, 1),
            "completeness": round(weighted_completeness, 1),
            "evidence": round(weighted_evidence, 1),
        },
        "reason": reason,
    }

def calculate_product_health_score(
    validation_results: dict[str, dict],
    required_fields: list[str],
) -> dict:
    """
    Calculate an explainable health score across validated
    product fields.

    Components:
    - Agreement: 40%
    - Completeness: 30%
    - Evidence: 30%
    """

    if not required_fields:
        return {
            "score": 0.0,
            "components": {
                "agreement": 0.0,
                "completeness": 0.0,
                "evidence": 0.0,
            },
            "weighted_components": {
                "agreement": 0.0,
                "completeness": 0.0,
                "evidence": 0.0,
            },
            "reason": "No required fields were provided.",
        }

    # --------------------------------------------------
    # Agreement
    # --------------------------------------------------

    agreement_scores = []

    for field in required_fields:
        result = validation_results.get(field)

        if not result:
            agreement_scores.append(0.0)
            continue

        status = result.get("status")

        if status == "agreement":
            agreement_scores.append(100.0)

        elif status == "partial":
            agreement_scores.append(50.0)

        elif status == "conflict":
            source_count = result.get("source_count", 0)
            agreement_count = result.get("agreement_count", 0)

            if source_count > 0:
                agreement_scores.append(
                    (agreement_count / source_count) * 100
                )
            else:
                agreement_scores.append(0.0)

        else:
            agreement_scores.append(0.0)

    agreement_score = (
        sum(agreement_scores) / len(agreement_scores)
    )

    # --------------------------------------------------
    # Completeness
    # --------------------------------------------------

    present_fields = 0

    for field in required_fields:
        result = validation_results.get(field)

        if result and result.get("status") != "missing":
            present_fields += 1

    completeness_score = (
        present_fields / len(required_fields)
    ) * 100

    # --------------------------------------------------
    # Evidence
    # --------------------------------------------------

    fields_with_evidence = 0

    for field in required_fields:
        result = validation_results.get(field)

        if not result or result.get("status") == "missing":
            continue

        evidence = result.get("evidence", [])

        has_source_url = any(
            item.get("source_url")
            for item in evidence
        )

        if has_source_url:
            fields_with_evidence += 1

    if present_fields > 0:
        evidence_score = (
            fields_with_evidence / present_fields
        ) * 100
    else:
        evidence_score = 0.0

    # --------------------------------------------------
    # Weighted score
    # --------------------------------------------------

    weighted_agreement = agreement_score * 0.40
    weighted_completeness = completeness_score * 0.30
    weighted_evidence = evidence_score * 0.30

    score = (
        weighted_agreement
        + weighted_completeness
        + weighted_evidence
    )

    score = min(max(score, 0.0), 100.0)

    # --------------------------------------------------
    # Explanation
    # --------------------------------------------------

    if present_fields == 0:
        reason = "No required product fields have validated values."

    elif agreement_score < 100:
        reason = (
            "Some product fields have partial evidence or "
            "conflicting source values."
        )

    elif completeness_score < 100:
        reason = (
            f"{present_fields} of {len(required_fields)} "
            "required product fields have values."
        )

    elif evidence_score < 100:
        reason = (
            "All validated fields agree, but some fields "
            "lack traceable source evidence."
        )

    else:
        reason = (
            "All required fields have supporting evidence "
            "and available sources agree."
        )

    return {
        "score": round(score, 1),
        "components": {
            "agreement": round(agreement_score, 1),
            "completeness": round(completeness_score, 1),
            "evidence": round(evidence_score, 1),
        },
        "weighted_components": {
            "agreement": round(weighted_agreement, 1),
            "completeness": round(weighted_completeness, 1),
            "evidence": round(weighted_evidence, 1),
        },
        "reason": reason,
    }