#!/usr/bin/env python3
"""Reconcile assignment, exposure, outcome maturity, attrition, and contamination."""

from __future__ import annotations

from ecae_common import ECAEError, cli_main, require_probability


def validate_exposure_outcome(value: dict) -> dict:
    arms = value.get("arms")
    if not isinstance(arms, dict) or len(arms) < 2:
        raise ECAEError("INVALID_ARMS", "At least two arm summaries are required")
    thresholds = value.get("thresholds", {})
    max_missing = require_probability(thresholds.get("max_outcome_missing_rate", 0.05), "max_outcome_missing_rate", allow_zero=True)
    max_contamination = require_probability(thresholds.get("max_contamination_rate", 0.01), "max_contamination_rate", allow_zero=True)
    max_crossarm_difference = require_probability(thresholds.get("max_crossarm_missingness_difference", 0.02), "max_crossarm_missingness_difference", allow_zero=True)
    summaries, blockers, warnings = {}, [], []
    missing_rates = []
    for arm, summary in arms.items():
        required = ["assigned", "eligible_exposure", "actually_exposed", "outcome_observed", "outcome_mature", "contaminated", "duplicate_units"]
        if any(key not in summary for key in required):
            raise ECAEError("MISSING_ARM_FIELD", f"{arm} is missing reconciliation counts")
        if any(not isinstance(summary[key], int) or isinstance(summary[key], bool) or summary[key] < 0 for key in required):
            raise ECAEError("INVALID_ARM_COUNT", f"{arm} counts must be non-negative integers")
        assigned = summary["assigned"]
        if assigned == 0:
            raise ECAEError("EMPTY_ARM", f"{arm} has zero assigned units")
        if any(summary[key] > assigned for key in ["eligible_exposure", "actually_exposed", "outcome_observed", "outcome_mature", "contaminated"]):
            raise ECAEError("COUNT_EXCEEDS_ASSIGNED", f"{arm} reconciliation count exceeds assigned")
        missing_rate = 1.0 - summary["outcome_observed"] / assigned
        mature_rate = summary["outcome_mature"] / assigned
        contamination_rate = summary["contaminated"] / assigned
        exposure_rate = summary["actually_exposed"] / assigned
        missing_rates.append(missing_rate)
        summaries[arm] = {"missing_rate":missing_rate,"mature_rate":mature_rate,"contamination_rate":contamination_rate,"exposure_rate":exposure_rate,"duplicate_units":summary["duplicate_units"]}
        if missing_rate > max_missing:
            blockers.append(f"{arm}:OUTCOME_MISSINGNESS_EXCEEDS_PROTOCOL")
        if mature_rate < 1.0:
            blockers.append(f"{arm}:OUTCOME_NOT_MATURE")
        if contamination_rate > max_contamination:
            blockers.append(f"{arm}:CONTAMINATION_EXCEEDS_PROTOCOL")
        if summary["duplicate_units"] > 0:
            blockers.append(f"{arm}:DUPLICATE_ASSIGNMENT_UNITS")
        if exposure_rate < 1.0:
            warnings.append(f"{arm}:NONCOMPLIANCE_REQUIRES_ITT_AND_SENSITIVITY")
    missingness_gap = max(missing_rates) - min(missing_rates)
    if missingness_gap > max_crossarm_difference:
        blockers.append("DIFFERENTIAL_MISSINGNESS_EXCEEDS_PROTOCOL")
    return {
        "status":"pass" if not blockers else "fail",
        "arms":summaries,
        "crossarm_missingness_difference":missingness_gap,
        "thresholds":{"max_outcome_missing_rate":max_missing,"max_contamination_rate":max_contamination,"max_crossarm_missingness_difference":max_crossarm_difference},
        "blockers":blockers,
        "warnings":warnings,
        "claim_impact":"block_ce4_ce5_until_resolved" if blockers else "none"
    }


if __name__ == "__main__":
    cli_main(validate_exposure_outcome, __doc__ or "Validate exposure and outcome")
