#!/usr/bin/env python3
"""Validate assignment integrity and sample-ratio mismatch (SRM)."""

from __future__ import annotations

import math

from ecae_common import ECAEError, cli_main, require_probability


def _regularized_gamma_q(shape: float, x: float) -> float:
    if x < 0 or shape <= 0:
        raise ECAEError("NUMERICAL_DOMAIN", "Invalid gamma survival arguments")
    if x == 0:
        return 1.0
    eps, tiny, max_iter = 1e-14, 1e-300, 1000
    if x < shape + 1:
        term = 1.0 / shape
        total = term
        ap = shape
        for _ in range(max_iter):
            ap += 1
            term *= x / ap
            total += term
            if abs(term) < abs(total) * eps:
                p = total * math.exp(-x + shape * math.log(x) - math.lgamma(shape))
                return max(0.0, min(1.0, 1.0 - p))
        raise ECAEError("NUMERICAL_NONCONVERGENCE", "Gamma series did not converge")
    b = x + 1.0 - shape
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, max_iter + 1):
        an = -i * (i - shape)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            q = math.exp(-x + shape * math.log(x) - math.lgamma(shape)) * h
            return max(0.0, min(1.0, q))
    raise ECAEError("NUMERICAL_NONCONVERGENCE", "Gamma continued fraction did not converge")


def validate_randomization(value: dict) -> dict:
    counts, probabilities = value.get("observed_counts"), value.get("expected_probabilities")
    if not isinstance(counts, dict) or not isinstance(probabilities, dict) or set(counts) != set(probabilities) or len(counts) < 2:
        raise ECAEError("INVALID_ASSIGNMENT_COUNTS", "Observed and expected arms must match and include at least two arms")
    if any(not isinstance(count, int) or isinstance(count, bool) or count < 0 for count in counts.values()):
        raise ECAEError("INVALID_ASSIGNMENT_COUNTS", "Observed counts must be non-negative integers")
    for arm, probability in probabilities.items():
        require_probability(probability, f"expected_probabilities.{arm}")
    if abs(sum(probabilities.values()) - 1.0) > 1e-12:
        raise ECAEError("PROBABILITIES_NOT_NORMALIZED", "Expected probabilities must sum to one")
    total = sum(counts.values())
    if total == 0:
        raise ECAEError("EMPTY_ASSIGNMENT", "No assignment units observed")
    expected = {arm: total * probabilities[arm] for arm in counts}
    if any(item < 5 for item in expected.values()):
        raise ECAEError("SRM_ASYMPTOTIC_UNSAFE", "Expected counts below five require an exact verified backend", expected)
    statistic = sum((counts[arm] - expected[arm]) ** 2 / expected[arm] for arm in counts)
    degrees = len(counts) - 1
    p_value = _regularized_gamma_q(degrees / 2.0, statistic / 2.0)
    threshold = require_probability(value.get("srm_alpha", 0.001), "srm_alpha")
    passed = p_value >= threshold
    proof = value.get("assignment_proof")
    proof_valid = isinstance(proof, dict) and bool(proof.get("proof_type")) and bool(proof.get("value"))
    blockers = []
    if not passed:
        blockers.append("SRM_DETECTED")
    if not proof_valid:
        blockers.append("ASSIGNMENT_PROOF_MISSING")
    return {
        "status": "pass" if not blockers else "fail",
        "observed_counts": counts,
        "expected_counts": expected,
        "pearson_chi_square": statistic,
        "degrees_of_freedom": degrees,
        "p_value": p_value,
        "srm_alpha": threshold,
        "assignment_proof_valid": proof_valid,
        "blockers": blockers,
        "claim_impact": "block_causal_until_resolved" if blockers else "none",
    }


if __name__ == "__main__":
    cli_main(validate_randomization, __doc__ or "Validate randomization")
