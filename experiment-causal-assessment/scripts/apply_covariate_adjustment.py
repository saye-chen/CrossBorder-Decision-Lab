#!/usr/bin/env python3
"""Apply pooled pretreatment CUPED adjustment and preserve unadjusted ITT."""

from __future__ import annotations

import math
from statistics import mean, variance

from ecae_common import ECAEError, cli_main
from evaluate_randomized_effect import evaluate_randomized_effect


def _solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(vector)
    augmented = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            raise ECAEError("SINGULAR_COVARIATES", "Covariate covariance matrix is singular")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        scale = augmented[col][col]
        augmented[col] = [item / scale for item in augmented[col]]
        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            augmented[row] = [a - factor * b for a, b in zip(augmented[row], augmented[col])]
    return [augmented[i][-1] for i in range(n)]


def apply_covariate_adjustment(value: dict) -> dict:
    records = value.get("records")
    covariates = value.get("covariates")
    control_arm = value.get("control_arm")
    if not isinstance(records, list) or len(records) < 4 or not isinstance(covariates, list) or not covariates:
        raise ECAEError("INVALID_INPUT", "records and at least one covariate are required")
    if any(item.get("temporal_status") != "pre_treatment" for item in covariates):
        raise ECAEError("BAD_CONTROL", "All covariates must be explicitly pre_treatment")
    names = [item.get("name") for item in covariates]
    arms = sorted({record.get("arm") for record in records})
    if control_arm not in arms or len(arms) < 2:
        raise ECAEError("INVALID_GROUPS", "control_arm and at least one treatment arm are required")
    outcomes, matrix = [], []
    for record in records:
        try:
            outcome = float(record["outcome"])
            row = [float(record["covariates"][name]) for name in names]
        except (KeyError, TypeError, ValueError) as exc:
            raise ECAEError("INVALID_RECORD", "Each record needs arm, numeric outcome, and all covariates") from exc
        if not math.isfinite(outcome) or any(not math.isfinite(item) for item in row):
            raise ECAEError("NON_FINITE_NUMBER", "Outcomes and covariates must be finite")
        outcomes.append(outcome)
        matrix.append(row)
    centers = [mean(row[j] for row in matrix) for j in range(len(names))]
    centered = [[row[j] - centers[j] for j in range(len(names))] for row in matrix]
    y_center = [item - mean(outcomes) for item in outcomes]
    covariance = [[sum(row[j] * row[k] for row in centered) for k in range(len(names))] for j in range(len(names))]
    cross = [sum(row[j] * y for row, y in zip(centered, y_center)) for j in range(len(names))]
    theta = _solve(covariance, cross)
    adjusted = [y - sum(coef * x for coef, x in zip(theta, row)) for y, row in zip(outcomes, centered)]
    unadjusted_groups = {arm: [outcomes[i] for i, record in enumerate(records) if record["arm"] == arm] for arm in arms}
    adjusted_groups = {arm: [adjusted[i] for i, record in enumerate(records) if record["arm"] == arm] for arm in arms}
    unadjusted = evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"continuous","groups":unadjusted_groups,"control_arm":control_arm,"confidence_level":value.get("confidence_level",0.95)})
    adjusted_result = evaluate_randomized_effect({"estimand_type":"ITT","metric_type":"continuous","groups":adjusted_groups,"control_arm":control_arm,"confidence_level":value.get("confidence_level",0.95)})
    original_variance, adjusted_variance = variance(outcomes), variance(adjusted)
    return {
        "method": "pooled_pretreatment_CUPED_linear_projection_v1",
        "covariates": names,
        "theta": dict(zip(names, theta)),
        "unadjusted": unadjusted,
        "adjusted": adjusted_result,
        "variance_reduction_fraction": None if original_variance == 0 else 1.0 - adjusted_variance / original_variance,
        "requirements": ["randomized assignment", "pretreatment covariates", "same frozen analysis population"],
        "not_equivalent_to": ["post-treatment adjustment", "as-treated analysis", "causal identification by regression"],
    }


if __name__ == "__main__":
    cli_main(apply_covariate_adjustment, __doc__ or "Apply CUPED")
