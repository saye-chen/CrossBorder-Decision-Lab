#!/usr/bin/env python3
"""Estimate ITT effects for two-arm or multi-arm randomized data."""

from __future__ import annotations

import math
from statistics import mean, variance

from ecae_common import ECAEError, cli_main, confidence_interval, two_sided_p_from_z


def _numeric(values, label: str, *, binary: bool = False, count: bool = False) -> list[float]:
    if not isinstance(values, list) or len(values) < 2:
        raise ECAEError("INSUFFICIENT_SAMPLE", f"{label} needs at least two unit-level observations")
    result = []
    for item in values:
        if not isinstance(item, (int, float)) or isinstance(item, bool) or not math.isfinite(item):
            raise ECAEError("INVALID_OUTCOME", f"{label} contains non-finite/non-numeric values")
        if binary and item not in (0, 1):
            raise ECAEError("INVALID_BINARY_OUTCOME", f"{label} must contain only 0/1")
        if count and (item < 0 or int(item) != item):
            raise ECAEError("INVALID_COUNT_OUTCOME", f"{label} must contain non-negative integers")
        result.append(float(item))
    return result


def _mean_summary(values: list[float]) -> dict:
    return {"n": len(values), "mean": mean(values), "variance": variance(values)}


def _difference(treatment: list[float], control: list[float], level: float) -> dict:
    t, c = _mean_summary(treatment), _mean_summary(control)
    estimate = t["mean"] - c["mean"]
    se = math.sqrt(t["variance"] / t["n"] + c["variance"] / c["n"])
    lower, upper = confidence_interval(estimate, se, level)
    z_value = estimate / se if se > 0 else (0.0 if estimate == 0 else math.copysign(math.inf, estimate))
    p_value = 1.0 if se == 0 and estimate == 0 else (0.0 if se == 0 else two_sided_p_from_z(z_value))
    relative = None if c["mean"] == 0 else estimate / abs(c["mean"])
    return {
        "estimate_absolute": estimate,
        "standard_error": se,
        "confidence_interval": {"level": level, "lower": lower, "upper": upper, "method": "welch_normal_approximation"},
        "z_value": z_value,
        "p_value_unadjusted": p_value,
        "relative_change": relative,
        "treatment": t,
        "control": c,
    }


def _wilson(successes: float, total: int, level: float) -> tuple[float, float]:
    if total <= 0:
        raise ECAEError("EMPTY_BINARY_ARM", "Binary arm cannot be empty")
    from ecae_common import z_quantile
    z = z_quantile(0.5 + level / 2.0)
    p = successes / total
    denominator = 1.0 + z * z / total
    center = (p + z * z / (2.0 * total)) / denominator
    half = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total)) / denominator
    return max(0.0, center - half), min(1.0, center + half)


def _binary_difference(treatment: list[float], control: list[float], level: float) -> dict:
    n_t, n_c = len(treatment), len(control)
    x_t, x_c = sum(treatment), sum(control)
    p_t, p_c = x_t / n_t, x_c / n_c
    estimate = p_t - p_c
    lt, ut = _wilson(x_t, n_t, level)
    lc, uc = _wilson(x_c, n_c, level)
    lower = estimate - math.sqrt((p_t - lt) ** 2 + (uc - p_c) ** 2)
    upper = estimate + math.sqrt((ut - p_t) ** 2 + (p_c - lc) ** 2)
    pooled = (x_t + x_c) / (n_t + n_c)
    null_se = math.sqrt(pooled * (1.0 - pooled) * (1.0 / n_t + 1.0 / n_c))
    z_value = estimate / null_se if null_se > 0 else (0.0 if estimate == 0 else math.copysign(math.inf, estimate))
    p_value = 1.0 if null_se == 0 and estimate == 0 else (0.0 if null_se == 0 else two_sided_p_from_z(z_value))
    return {
        "estimate_absolute": estimate,
        "standard_error": math.sqrt(p_t * (1.0 - p_t) / n_t + p_c * (1.0 - p_c) / n_c),
        "confidence_interval": {"level": level, "lower": lower, "upper": upper, "method": "newcombe_hybrid_score_v1"},
        "z_value": z_value,
        "p_value_unadjusted": p_value,
        "relative_change": None if p_c == 0 else estimate / p_c,
        "treatment": {"n": n_t, "events": int(x_t), "rate": p_t},
        "control": {"n": n_c, "events": int(x_c), "rate": p_c},
    }


def _ratio_summary(records, label: str) -> tuple[dict, float]:
    if not isinstance(records, list) or len(records) < 2:
        raise ECAEError("INSUFFICIENT_SAMPLE", f"{label} needs at least two ratio records")
    numerators, denominators = [], []
    for record in records:
        if not isinstance(record, dict) or "numerator" not in record or "denominator" not in record:
            raise ECAEError("INVALID_RATIO_RECORD", f"{label} records need numerator and denominator")
        x, y = float(record["numerator"]), float(record["denominator"])
        if not math.isfinite(x) or not math.isfinite(y) or y < 0:
            raise ECAEError("INVALID_RATIO_RECORD", f"{label} contains invalid numerator/denominator")
        numerators.append(x)
        denominators.append(y)
    mean_x, mean_y = mean(numerators), mean(denominators)
    if mean_y <= 0:
        raise ECAEError("ZERO_DENOMINATOR", f"{label} mean denominator must be positive")
    ratio = mean_x / mean_y
    influence = [(x - ratio * y) / mean_y for x, y in zip(numerators, denominators)]
    return {"n": len(records), "ratio_of_totals": ratio, "mean_numerator": mean_x, "mean_denominator": mean_y}, variance(influence) / len(influence)


def _ratio_difference(treatment, control, level: float) -> dict:
    t, var_t = _ratio_summary(treatment, "treatment")
    c, var_c = _ratio_summary(control, "control")
    estimate = t["ratio_of_totals"] - c["ratio_of_totals"]
    se = math.sqrt(var_t + var_c)
    lower, upper = confidence_interval(estimate, se, level)
    z_value = estimate / se if se > 0 else (0.0 if estimate == 0 else math.copysign(math.inf, estimate))
    p_value = 1.0 if se == 0 and estimate == 0 else (0.0 if se == 0 else two_sided_p_from_z(z_value))
    relative = None if c["ratio_of_totals"] == 0 else estimate / abs(c["ratio_of_totals"])
    return {
        "estimate_absolute": estimate,
        "standard_error": se,
        "confidence_interval": {"level": level, "lower": lower, "upper": upper, "method": "delta_method_unit_influence"},
        "z_value": z_value,
        "p_value_unadjusted": p_value,
        "relative_change": relative,
        "treatment": t,
        "control": c,
    }


def evaluate_randomized_effect(value: dict) -> dict:
    if value.get("estimand_type") != "ITT":
        raise ECAEError("ESTIMAND_MISMATCH", "Native randomized evaluator only supports ITT")
    metric_type = value.get("metric_type")
    level = float(value.get("confidence_level", 0.95))
    if not 0 < level < 1:
        raise ECAEError("INVALID_CONFIDENCE_LEVEL", "confidence_level must be in (0,1)")
    groups = value.get("groups")
    control_arm = value.get("control_arm")
    if not isinstance(groups, dict) or control_arm not in groups or len(groups) < 2:
        raise ECAEError("INVALID_GROUPS", "groups must contain a named control and at least one treatment")
    comparisons = []
    for arm in sorted(groups):
        if arm == control_arm:
            continue
        if metric_type == "ratio":
            result = _ratio_difference(groups[arm], groups[control_arm], level)
        else:
            treatment = _numeric(groups[arm], arm, binary=metric_type == "binary", count=metric_type == "count")
            control = _numeric(groups[control_arm], control_arm, binary=metric_type == "binary", count=metric_type == "count")
            if metric_type not in {"binary", "continuous", "count"}:
                raise ECAEError("UNSUPPORTED_METRIC_TYPE", "Supported metric types: binary, continuous, count, ratio")
            result = _binary_difference(treatment, control, level) if metric_type == "binary" else _difference(treatment, control, level)
        result["contrast"] = f"{arm} - {control_arm}"
        comparisons.append(result)
    return {
        "design": "randomized",
        "estimand_type": "ITT",
        "metric_type": metric_type,
        "control_arm": control_arm,
        "comparisons": comparisons,
        "multiplicity_status": "unadjusted_requires_family_ledger" if len(comparisons) > 1 else "single_contrast",
        "diagnostics_required": ["assignment_integrity", "SRM", "exposure_reconciliation", "maturity", "missingness", "contamination"],
        "inference_limit": "Normal/delta approximation; finite-sample and design diagnostics determine claim grade.",
    }


if __name__ == "__main__":
    cli_main(evaluate_randomized_effect, __doc__ or "Evaluate randomized effect")
