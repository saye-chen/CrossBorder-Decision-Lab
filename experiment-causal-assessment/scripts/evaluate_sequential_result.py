#!/usr/bin/env python3
"""Enforce mutually exclusive fixed, group-sequential, and anytime-valid inference."""

from __future__ import annotations

import math

from backend_contract import require_verified_backend
from ecae_common import ECAEError, cli_main


def _numeric(value, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise ECAEError("SEQUENTIAL_VALUE_INVALID", f"{name} must be finite numeric")
    return float(value)


def _validate_group_sequential(value: dict, looks: list[dict]) -> None:
    alpha = _numeric(value.get("alpha"), "alpha")
    if not 0 < alpha < 1:
        raise ECAEError("ALPHA_SPENDING_INVALID", "Group-sequential alpha must be in (0,1)")
    if value.get("sided") not in {1, 2} or value.get("efficacy_spending") not in {"obrien_fleming", "pocock", "hwang_shih_decani", "user_supplied"}:
        raise ECAEError("SEQUENTIAL_DESIGN_NOT_FROZEN", "Sidedness and efficacy spending must be frozen")
    if value.get("futility_binding") not in {True, False} or value.get("design_frozen_before_outcomes") is not True:
        raise ECAEError("SEQUENTIAL_DESIGN_NOT_FROZEN", "Futility semantics and pre-outcome design freeze are required")
    fractions = value.get("information_fractions")
    if not isinstance(fractions, list) or len(fractions) != len(looks):
        raise ECAEError("INFORMATION_FRACTION_INVALID", "One registered information fraction is required per look")
    fractions = [_numeric(item, "information_fraction") for item in fractions]
    if any(not 0 < item <= 1 for item in fractions) or any(fractions[index] <= fractions[index - 1] for index in range(1, len(fractions))) or abs(fractions[-1] - 1.0) > 1e-12:
        raise ECAEError("INFORMATION_FRACTION_INVALID", "Information fractions must be strictly increasing in (0,1] and end at one")
    alpha_spent = []
    for index, look in enumerate(looks):
        missing = [field for field in ("information_fraction", "boundary", "alpha_spent") if field not in look]
        if missing:
            raise ECAEError("SEQUENTIAL_LOOK_INCOMPLETE", "Registered group-sequential look fields are missing", {"look": index, "fields": missing})
        observed_fraction = _numeric(look["information_fraction"], f"looks[{index}].information_fraction")
        if abs(observed_fraction - fractions[index]) > 1e-12:
            raise ECAEError("INFORMATION_FRACTION_MISMATCH", "Observed and registered information fractions differ", {"look": index})
        _numeric(look["boundary"], f"looks[{index}].boundary")
        alpha_spent.append(_numeric(look["alpha_spent"], f"looks[{index}].alpha_spent"))
    if any(item < 0 or item > alpha + 1e-12 for item in alpha_spent) or any(alpha_spent[index] < alpha_spent[index - 1] for index in range(1, len(alpha_spent))):
        raise ECAEError("ALPHA_SPENDING_INVALID", "Cumulative alpha spent must be nondecreasing and bounded by registered alpha")


def _validate_anytime(value: dict, looks: list[dict]) -> None:
    if value.get("anytime_method") not in {"e_process", "confidence_sequence"} or value.get("method_frozen_before_outcomes") is not True:
        raise ECAEError("ANYTIME_METHOD_NOT_FROZEN", "Anytime-valid method must be frozen before outcomes")
    if not isinstance(value.get("observation_process"), str) or not value["observation_process"]:
        raise ECAEError("OBSERVATION_PROCESS_NOT_FROZEN", "Anytime-valid inference requires a frozen observation process")
    for index, look in enumerate(looks):
        missing = [field for field in ("e_value_or_cs", "confidence_sequence") if field not in look]
        if missing:
            raise ECAEError("SEQUENTIAL_LOOK_INCOMPLETE", "Registered anytime-valid look fields are missing", {"look": index, "fields": missing})
        e_value = _numeric(look["e_value_or_cs"], f"looks[{index}].e_value_or_cs")
        interval = look["confidence_sequence"]
        if e_value < 0 or not isinstance(interval, dict) or set(interval) != {"lower", "upper"}:
            raise ECAEError("ANYTIME_OUTPUT_INVALID", "Anytime look requires non-negative e-value and lower/upper confidence sequence")
        lower = _numeric(interval["lower"], f"looks[{index}].confidence_sequence.lower")
        upper = _numeric(interval["upper"], f"looks[{index}].confidence_sequence.upper")
        if lower > upper:
            raise ECAEError("ANYTIME_OUTPUT_INVALID", "Confidence-sequence lower bound cannot exceed upper bound")


def evaluate_sequential_result(value: dict) -> dict:
    paradigm = value.get("sequential_paradigm")
    looks = value.get("looks")
    if paradigm not in {"fixed_horizon","group_sequential","anytime_valid"}:
        raise ECAEError("INVALID_SEQUENTIAL_PARADIGM", "Unknown sequential paradigm")
    if not isinstance(looks, list) or not looks:
        raise ECAEError("MISSING_LOOKS", "At least one analysis look is required")
    if any(look.get("paradigm") not in (None, paradigm) for look in looks):
        raise ECAEError("MIXED_SEQUENTIAL_PARADIGMS", "All looks must use the registered paradigm")
    if paradigm == "fixed_horizon":
        outcome_reviewed_early = any(look.get("outcome_reviewed") is True and not look.get("is_final") for look in looks)
        final_looks = [look for look in looks if look.get("is_final") is True]
        if outcome_reviewed_early or len(final_looks) != 1 or final_looks[0] is not looks[-1]:
            raise ECAEError("FIXED_HORIZON_VIOLATION", "Fixed-horizon inference permits one final outcome analysis and no outcome-driven early stop")
        return {"paradigm":paradigm,"status":"valid_final_look","backend":"native_contract","claim_impact":"none","result_ref":final_looks[0].get("result_ref")}
    if paradigm == "group_sequential":
        _validate_group_sequential(value, looks)
        backend_id = "group_sequential"
    else:
        _validate_anytime(value, looks)
        backend_id = "anytime_valid"
    backend = require_verified_backend(backend_id)
    return {"paradigm":paradigm,"status":"evaluated_by_verified_backend","backend":backend,"looks":looks}


if __name__ == "__main__":
    cli_main(evaluate_sequential_result, __doc__ or "Evaluate sequential result")
