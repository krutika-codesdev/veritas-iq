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