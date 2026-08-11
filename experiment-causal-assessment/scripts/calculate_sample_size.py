#!/usr/bin/env python3
"""Calculate transparent two-arm fixed-horizon sample requirements."""

from __future__ import annotations

import math

from ecae_common import ECAEError, cli_main, require_positive, require_probability, z_quantile


def calculate_sample_size(value: dict) -> dict:
    metric_type = value.get("metric_type")
    alpha = require_probability(value.get("alpha", 0.05), "alpha")
    power = require_probability(value.get("power", 0.8), "power")
    ratio = require_positive(value.get("allocation_ratio", 1.0), "allocation_ratio")
    attrition = require_probability(value.get("attrition_rate", 0.0), "attrition_rate", allow_zero=True)
    if attrition >= 1:
        raise ECAEError("INVALID_ATTRITION", "attrition_rate must be below one")
    alternative = value.get("alternative", "two_sided")
    if alternative not in {"two_sided", "one_sided"}:
        raise ECAEError("INVALID_ALTERNATIVE", "alternative must be two_sided or one_sided")
    z_alpha = z_quantile(1.0 - alpha / (2.0 if alternative == "two_sided" else 1.0))
    z_power = z_quantile(power)

    if metric_type in {"continuous", "count", "ratio_influence"}:
        delta = abs(require_positive(value.get("minimum_important_effect"), "minimum_important_effect"))
        variance = require_positive(value.get("baseline_variance"), "baseline_variance")
        control_analyzable = (z_alpha + z_power) ** 2 * variance * (1.0 + 1.0 / ratio) / delta**2
        formula = "normal_approx_difference_in_means_v1"
        assumptions = ["independent units", "finite variance", "fixed horizon", "variance applies to the analysis-scale outcome or influence function"]
    elif metric_type == "binary":
        p_control = require_probability(value.get("baseline_rate"), "baseline_rate", allow_zero=True)
        delta_signed = float(value.get("minimum_important_effect"))
        p_treatment = p_control + delta_signed
        if not 0 < p_treatment < 1:
            raise ECAEError("IMPOSSIBLE_ALTERNATIVE_RATE", "baseline_rate + minimum_important_effect must be in (0,1)")
        delta = abs(delta_signed)
        if delta == 0:
            raise ECAEError("ZERO_EFFECT", "minimum_important_effect must be non-zero")
        pooled = (p_control + ratio * p_treatment) / (1.0 + ratio)
        null_variance = pooled * (1.0 - pooled) * (1.0 + 1.0 / ratio)
        alt_variance = p_control * (1.0 - p_control) + p_treatment * (1.0 - p_treatment) / ratio
        control_analyzable = (z_alpha * math.sqrt(null_variance) + z_power * math.sqrt(alt_variance)) ** 2 / delta**2
        formula = "unpooled_two_proportion_normal_approx_v1"
        assumptions = ["independent Bernoulli units", "fixed horizon", "normal approximation adequate", "absolute risk-difference estimand"]
    else:
        raise ECAEError("UNSUPPORTED_METRIC_TYPE", "metric_type must be continuous, count, ratio_influence, or binary")

    treatment_analyzable = ratio * control_analyzable
    inflation = 1.0 / (1.0 - attrition)
    n_control = math.ceil(control_analyzable * inflation)
    n_treatment = math.ceil(treatment_analyzable * inflation)
    return {
        "metric_type": metric_type,
        "design": "two_arm_fixed_horizon",
        "n_control": n_control,
        "n_treatment": n_treatment,
        "n_total": n_control + n_treatment,
        "allocation_ratio_treatment_to_control": ratio,
        "alpha": alpha,
        "power": power,
        "alternative": alternative,
        "attrition_rate": attrition,
        "formula_version": formula,
        "assumptions": assumptions,
        "sensitivity_required": True,
        "not_covered": ["cluster design effect", "sequential monitoring", "multiplicity", "finite-population correction"],
    }


if __name__ == "__main__":
    cli_main(calculate_sample_size, __doc__ or "Calculate sample size")
