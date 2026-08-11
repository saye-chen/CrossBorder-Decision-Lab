#!/usr/bin/env python3
"""Calculate MDE and confidence half-width under a frozen two-arm design."""

from __future__ import annotations

import math

from ecae_common import ECAEError, cli_main, require_positive, require_probability, z_quantile


def calculate_mde_precision(value: dict) -> dict:
    n_control = int(require_positive(value.get("n_control"), "n_control"))
    n_treatment = int(require_positive(value.get("n_treatment"), "n_treatment"))
    if n_control < 2 or n_treatment < 2:
        raise ECAEError("INSUFFICIENT_SAMPLE", "Each arm needs at least two analyzable units")
    alpha = require_probability(value.get("alpha", 0.05), "alpha")
    power = require_probability(value.get("power", 0.8), "power")
    confidence_level = require_probability(value.get("confidence_level", 0.95), "confidence_level")
    alternative = value.get("alternative", "two_sided")
    if alternative not in {"two_sided", "one_sided"}:
        raise ECAEError("INVALID_ALTERNATIVE", "alternative must be two_sided or one_sided")
    metric_type = value.get("metric_type")
    if metric_type == "binary":
        baseline = require_probability(value.get("baseline_rate"), "baseline_rate", allow_zero=True)
        variance = baseline * (1.0 - baseline)
        formula = "local_binary_normal_approx_v1"
    elif metric_type in {"continuous", "count", "ratio_influence"}:
        variance = require_positive(value.get("baseline_variance"), "baseline_variance")
        formula = "difference_in_means_normal_approx_v1"
    else:
        raise ECAEError("UNSUPPORTED_METRIC_TYPE", "Unsupported metric_type")
    standard_error_null = math.sqrt(variance * (1.0 / n_control + 1.0 / n_treatment))
    z_alpha = z_quantile(1.0 - alpha / (2.0 if alternative == "two_sided" else 1.0))
    z_power = z_quantile(power)
    mde = (z_alpha + z_power) * standard_error_null
    half_width = z_quantile(0.5 + confidence_level / 2.0) * standard_error_null
    return {
        "metric_type": metric_type,
        "mde_absolute": mde,
        "confidence_half_width_at_null": half_width,
        "standard_error_at_null": standard_error_null,
        "alpha": alpha,
        "power": power,
        "confidence_level": confidence_level,
        "formula_version": formula,
        "interpretation": "Local planning approximation; rerun sensitivity across plausible baselines/variances.",
    }


if __name__ == "__main__":
    cli_main(calculate_mde_precision, __doc__ or "Calculate MDE")
