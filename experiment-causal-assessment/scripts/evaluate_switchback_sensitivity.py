#!/usr/bin/env python3
"""Estimate preregistered switchback lag, periodicity, and HAC sensitivity models."""

from __future__ import annotations

import math

from ecae_common import ECAEError, cli_main


def _transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [list(column) for column in zip(*matrix)]


def _matmul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    return [[sum(a * b for a, b in zip(row, column)) for column in _transpose(right)] for row in left]


def _inverse(matrix: list[list[float]]) -> list[list[float]]:
    size = len(matrix)
    work = [row[:] + [1.0 if i == j else 0.0 for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(work[row][column]))
        if abs(work[pivot][column]) < 1e-12:
            raise ECAEError("SWITCHBACK_DESIGN_SINGULAR", "Sensitivity design matrix is singular")
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [value - factor * base for value, base in zip(work[row], work[column])]
    return [row[size:] for row in work]


def _fit(rows: list[dict], lag_order: int, periodicities: list[int], hac_lag: int) -> dict:
    start = lag_order
    names = ["intercept", "current_treatment"]
    names.extend(f"lag_{lag}" for lag in range(1, lag_order + 1))
    for period in periodicities:
        names.extend((f"sin_{period}", f"cos_{period}"))
    design, outcome = [], []
    for index in range(start, len(rows)):
        vector = [1.0, float(rows[index]["arm"])]
        vector.extend(float(rows[index - lag]["arm"]) for lag in range(1, lag_order + 1))
        for period in periodicities:
            angle = 2 * math.pi * float(rows[index]["period_index"]) / period
            vector.extend((math.sin(angle), math.cos(angle)))
        design.append(vector)
        outcome.append(float(rows[index]["outcome"]))
    if len(design) <= len(names) + 2:
        raise ECAEError("SWITCHBACK_SENSITIVITY_UNDERPOWERED", "Sensitivity model needs more residual degrees of freedom")
    xt = _transpose(design)
    inverse = _inverse(_matmul(xt, design))
    beta = [row[0] for row in _matmul(_matmul(inverse, xt), [[value] for value in outcome])]
    residual = [y - sum(value * coefficient for value, coefficient in zip(row, beta)) for row, y in zip(design, outcome)]
    width = len(names)
    meat = [[0.0] * width for _ in range(width)]
    for left in range(len(design)):
        for right in range(max(0, left - hac_lag), min(len(design), left + hac_lag + 1)):
            lag = abs(left - right)
            weight = 1 - lag / (hac_lag + 1) if hac_lag else 1.0
            for i in range(width):
                for j in range(width):
                    meat[i][j] += weight * design[left][i] * residual[left] * residual[right] * design[right][j]
    covariance = _matmul(_matmul(inverse, meat), inverse)
    standard_errors = [math.sqrt(max(covariance[index][index], 0.0)) for index in range(width)]
    return {
        "lag_order": lag_order,
        "periodicities": periodicities,
        "hac_lag": hac_lag,
        "sample_size": len(design),
        "residual_degrees_of_freedom": len(design) - width,
        "coefficients": {name: beta[index] for index, name in enumerate(names)},
        "standard_errors": {name: standard_errors[index] for index, name in enumerate(names)},
        "current_treatment_interval_95": [beta[1] - 1.96 * standard_errors[1], beta[1] + 1.96 * standard_errors[1]],
    }


def evaluate_switchback_sensitivity(value: dict) -> dict:
    rows = value.get("rows")
    if not isinstance(rows, list) or len(rows) < 16 or not all(isinstance(row, dict) for row in rows):
        raise ECAEError("SWITCHBACK_SENSITIVITY_UNDERPOWERED", "At least sixteen period rows are required")
    for index, row in enumerate(rows):
        if set(row) < {"period_index", "arm", "outcome"}:
            raise ECAEError("INVALID_PERIOD_RECORD", "Every sensitivity row needs period_index arm and outcome")
        if row["period_index"] != index or row["arm"] not in {0, 1}:
            raise ECAEError("SWITCHBACK_PERIOD_ORDER_INVALID", "period_index must be consecutive and arm binary")
        if isinstance(row["outcome"], bool) or not isinstance(row["outcome"], (int, float)) or not math.isfinite(row["outcome"]):
            raise ECAEError("INVALID_CLUSTER_OUTCOME", "Switchback sensitivity outcomes must be finite")
    registered_lag = value.get("registered_lag_order")
    maximum_lag = value.get("maximum_lag_order")
    hac_lag = value.get("hac_lag")
    periodicities = value.get("registered_periodicities")
    tolerance = value.get("coefficient_stability_tolerance")
    if not all(isinstance(item, int) and not isinstance(item, bool) for item in (registered_lag, maximum_lag, hac_lag)):
        raise ECAEError("CARRYOVER_ORDER_INVALID", "Lag orders and HAC lag must be integers")
    if not 0 <= registered_lag <= maximum_lag <= 8 or not 0 <= hac_lag <= 12:
        raise ECAEError("CARRYOVER_ORDER_INVALID", "Lag orders or HAC lag exceed the bounded contract")
    if not isinstance(periodicities, list) or not periodicities or any(not isinstance(period, int) or isinstance(period, bool) or period < 2 for period in periodicities):
        raise ECAEError("PERIODICITY_CONFOUNDED", "At least one integer periodicity of two or greater is required")
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or tolerance < 0 or not math.isfinite(tolerance):
        raise ECAEError("SWITCHBACK_SENSITIVITY_INVALID", "coefficient_stability_tolerance must be finite and non-negative")
    models = [_fit(rows, lag, periodicities, hac_lag) for lag in range(maximum_lag + 1)]
    registered = models[registered_lag]
    effect = registered["coefficients"]["current_treatment"]
    differences = [abs(model["coefficients"]["current_treatment"] - effect) for model in models]
    stable = max(differences) <= tolerance
    return {
        "status": "pass" if stable else "downgrade_required",
        "registered_model": registered,
        "sensitivity_models": models,
        "maximum_absolute_effect_shift": max(differences),
        "coefficient_stability_tolerance": float(tolerance),
        "carryover_sensitivity_pass": stable,
        "periodicity_terms_estimated": True,
        "serial_dependence_interval": "Newey_West_Bartlett_HAC",
        "claim_impact": "none" if stable else "downgrade_and_investigate_carryover_periodicity",
        "business_action_authorized": False,
    }


if __name__ == "__main__":
    cli_main(evaluate_switchback_sensitivity, __doc__ or "Evaluate switchback sensitivity")
