#!/usr/bin/env python3
"""Validate a target-population transport contract without inheriting source grade."""

from __future__ import annotations

import math

from ecae_common import ECAEError, cli_main


GRADE_ORDER = {"CE0": 0, "CE1": 1, "CE2": 2, "CE3": 3, "CE4": 4, "CE5": 5}
REQUIRED = [
    "source_environment", "target_environment", "source_grade", "source_estimand", "target_estimand",
    "source_population", "target_population", "selection_diagram_ref", "selection_exchangeability_assumption",
    "consistency_assumption", "treatment_version_equivalent", "outcome_measurement_equivalent",
    "effect_modifiers", "effect_modifier_sufficiency_argument", "all_effect_modifiers_pretreatment",
    "target_population_evidence", "sampling_score_model", "sampling_score_cross_fitted",
    "transport_estimator", "support_overlap_status", "weight_diagnostics", "transport_precision_policy",
    "weight_truncation_policy", "weight_sensitivity", "mechanism_stability_argument",
    "temporal_drift_assessment", "bridge_validation_plan", "bridge_validation_completed",
    "f02_applicability_ref", "f02_applicability_status",
]


def _finite_number(value, field: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ECAEError("TRANSPORT_DIAGNOSTIC_INVALID", f"{field} must be finite numeric")
    number = float(value)
    if positive and number <= 0:
        raise ECAEError("TRANSPORT_DIAGNOSTIC_INVALID", f"{field} must be positive")
    return number


def evaluate_transportability(value: dict) -> dict:
    missing = [field for field in REQUIRED if field not in value or value[field] in (None, "", [], {})]
    if missing:
        raise ECAEError("TRANSPORT_CONTRACT_INCOMPLETE", "Transportability contract is incomplete", missing)
    if value["source_grade"] not in GRADE_ORDER:
        raise ECAEError("TRANSPORT_SOURCE_GRADE_INVALID", "source_grade must be CE0 through CE5")
    if not isinstance(value["effect_modifiers"], list) or not value["effect_modifiers"]:
        raise ECAEError("TRANSPORT_MODIFIERS_MISSING", "At least one candidate effect modifier must be registered")
    if value["all_effect_modifiers_pretreatment"] is not True:
        raise ECAEError("POSTTREATMENT_MODIFIER", "Transport effect modifiers must be pretreatment")
    if value["sampling_score_cross_fitted"] is not True:
        raise ECAEError("TRANSPORT_NUISANCE_LEAKAGE", "Sampling-score predictions used for transport must be out of fold")
    if value["transport_estimator"] not in {"inverse_odds_sampling_weight", "inverse_probability_sampling_weight", "outcome_standardization", "doubly_robust_transport"}:
        raise ECAEError("TRANSPORT_ESTIMATOR_INVALID", "Unknown transport estimator")
    if value["support_overlap_status"] not in {"pass", "restricted_target"}:
        raise ECAEError("TARGET_SUPPORT_NOT_ESTABLISHED", "Target-population support must pass or be explicitly restricted")
    if value["support_overlap_status"] == "restricted_target" and not value.get("target_population_restriction"):
        raise ECAEError("TRANSPORT_RESTRICTION_UNDEFINED", "Restricted support requires a target-population restriction")

    diagnostics = value["weight_diagnostics"]
    policy = value["transport_precision_policy"]
    if not isinstance(diagnostics, dict) or not isinstance(policy, dict):
        raise ECAEError("TRANSPORT_DIAGNOSTIC_INVALID", "Weight diagnostics and precision policy must be objects")
    for field in ("source_sample_size", "effective_sample_size", "maximum_normalized_weight", "tail_weight_mass"):
        if field not in diagnostics:
            raise ECAEError("TRANSPORT_DIAGNOSTIC_INVALID", f"weight_diagnostics.{field} is required")
    for field in ("minimum_effective_sample_size", "maximum_normalized_weight", "maximum_tail_weight_mass"):
        if field not in policy:
            raise ECAEError("TRANSPORT_PRECISION_POLICY_INVALID", f"transport_precision_policy.{field} is required")
    source_n = _finite_number(diagnostics["source_sample_size"], "source_sample_size", positive=True)
    effective_n = _finite_number(diagnostics["effective_sample_size"], "effective_sample_size", positive=True)
    max_weight = _finite_number(diagnostics["maximum_normalized_weight"], "maximum_normalized_weight", positive=True)
    tail_mass = _finite_number(diagnostics["tail_weight_mass"], "tail_weight_mass")
    if effective_n > source_n or not 0 <= tail_mass <= 1:
        raise ECAEError("TRANSPORT_DIAGNOSTIC_INVALID", "Transport ESS or tail mass is impossible")

    blockers: list[str] = []
    if value["source_estimand"] != value["target_estimand"]:
        blockers.append("ESTIMAND_SHIFT")
    if value["selection_exchangeability_assumption"] is not True:
        blockers.append("SELECTION_EXCHANGEABILITY_UNSUPPORTED")
    if value["consistency_assumption"] is not True:
        blockers.append("CONSISTENCY_UNSUPPORTED")
    if value["treatment_version_equivalent"] is not True:
        blockers.append("TREATMENT_VERSION_SHIFT")
    if value["outcome_measurement_equivalent"] is not True:
        blockers.append("MEASUREMENT_NON_EQUIVALENCE")
    if effective_n < _finite_number(policy["minimum_effective_sample_size"], "minimum_effective_sample_size", positive=True):
        blockers.append("TRANSPORT_EFFECTIVE_SAMPLE_INADEQUATE")
    if max_weight > _finite_number(policy["maximum_normalized_weight"], "policy.maximum_normalized_weight", positive=True):
        blockers.append("TRANSPORT_WEIGHT_DOMINANCE")
    if tail_mass > _finite_number(policy["maximum_tail_weight_mass"], "maximum_tail_weight_mass"):
        blockers.append("TRANSPORT_WEIGHT_TAIL_EXCESS")
    if value["f02_applicability_status"] != "pass":
        blockers.append("F02_APPLICABILITY_NOT_PASSED")
    if value["bridge_validation_completed"] is not True:
        blockers.append("BRIDGE_VALIDATION_PENDING")

    protocol_qualified = not blockers
    source_ceiling = min(GRADE_ORDER[value["source_grade"]], GRADE_ORDER["CE4"])
    target_ceiling_value = source_ceiling if protocol_qualified else min(GRADE_ORDER[value["source_grade"]], GRADE_ORDER["CE3"])
    target_ceiling = f"CE{target_ceiling_value}"
    return {
        "transport_status": "protocol_qualified_external_estimation_required" if protocol_qualified else "not_yet_supported",
        "source_grade": value["source_grade"],
        "target_grade_ceiling": target_ceiling,
        "target_population_scope": value.get("target_population_restriction", value["target_population"]),
        "blockers": sorted(blockers),
        "weight_diagnostics": {"source_sample_size": source_n, "effective_sample_size": effective_n, "maximum_normalized_weight": max_weight, "tail_weight_mass": tail_mass},
        "external_transport_estimation_required": True,
        "f02_applicability_required": True,
        "source_grade_not_inherited_automatically": True,
        "target_grade_awarded": False,
    }


if __name__ == "__main__":
    cli_main(evaluate_transportability, __doc__ or "Evaluate transportability")
