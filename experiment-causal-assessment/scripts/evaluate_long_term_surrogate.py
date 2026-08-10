#!/usr/bin/env python3
"""Validate long-term outcome and surrogate-index evidence without proxy overclaim."""

from __future__ import annotations

from ecae_common import ECAEError, cli_main


BASE_REQUIRED = [
    "long_term_estimand", "long_term_outcome", "outcome_horizon", "decision_horizon",
    "evidence_mode", "intervention_family", "target_population", "treatment_version",
    "experimental_sample_ref", "long_term_outcome_sample_ref", "measurement_maturity_status",
    "censoring_competing_risk_plan", "missingness_sensitivity",
]
SURROGATE_REQUIRED = [
    "short_term_surrogates", "surrogate_measurement_times", "samples_comparable",
    "surrogacy_assumption", "comparability_assumption", "all_surrogates_post_assignment_pre_outcome",
    "surrogate_model_cross_fitted", "surrogate_model_frozen", "historical_validation",
    "treatment_family_validation", "negative_or_failure_cases", "surrogacy_violation_sensitivity",
    "bridge_validation_plan",
]


def evaluate_long_term_surrogate(value: dict) -> dict:
    mode = value.get("evidence_mode")
    required = BASE_REQUIRED + ([] if mode == "direct_long_term" else SURROGATE_REQUIRED)
    missing = [field for field in required if field not in value or value[field] in (None, "", [], {})]
    if missing:
        raise ECAEError("SURROGATE_CONTRACT_INCOMPLETE", "Long-term/surrogate contract is incomplete", missing)
    if mode not in {"direct_long_term", "surrogate_index", "surrogate_endpoint_only"}:
        raise ECAEError("SURROGATE_MODE_INVALID", "Unknown long-term evidence_mode")
    if mode == "direct_long_term":
        blockers = [] if value["measurement_maturity_status"] == "mature" else ["LONG_TERM_OUTCOME_NOT_MATURE"]
        if value.get("dynamic_treatment_or_time_varying_confounding") is True:
            blockers.append("TIME_VARYING_CONFOUNDING_REQUIRES_G_METHOD")
        return {
            "status": "qualified_for_direct_long_term_analysis" if not blockers else "not_yet_qualified",
            "claim_ceiling": "source_design_ceiling" if not blockers else "CE3",
            "blockers": sorted(blockers),
            "long_term_effect_estimated": False,
            "surrogate_effect_is_not_long_term_effect": True,
            "external_qualified_estimation_required": True,
        }
    if not isinstance(value["short_term_surrogates"], list) or not value["short_term_surrogates"]:
        raise ECAEError("SURROGATE_SET_INVALID", "At least one short-term surrogate must be registered")
    if value["all_surrogates_post_assignment_pre_outcome"] is not True:
        raise ECAEError("SURROGATE_TEMPORAL_ORDER_INVALID", "Surrogates must occur after assignment and before the long-term outcome")
    if value["surrogate_model_cross_fitted"] is not True or value["surrogate_model_frozen"] is not True:
        raise ECAEError("SURROGATE_MODEL_LEAKAGE", "Surrogate models must be cross-fitted and frozen before treatment-effect inspection")
    if value.get("surrogate_selected_after_effect_inspection") is True:
        raise ECAEError("SURROGATE_SELECTION_BIAS", "Surrogates cannot be selected after inspecting treatment effects")
    if value.get("treatment_effect_on_surrogate_used_as_long_term_proof") is True:
        raise ECAEError("SURROGATE_PARADOX_RISK", "A favorable surrogate effect alone cannot prove a favorable long-term effect")
    if value.get("dynamic_treatment_or_time_varying_confounding") is True:
        return {
            "status": "protocol_only_longitudinal_g_method_required",
            "claim_ceiling": "CE3",
            "blockers": ["TIME_VARYING_CONFOUNDING_REQUIRES_G_METHOD"],
            "long_term_effect_estimated": False,
        }

    blockers: list[str] = []
    if value["samples_comparable"] is not True:
        blockers.append("EXPERIMENTAL_OUTCOME_SAMPLE_NONCOMPARABLE")
    if value["surrogacy_assumption"] is not True:
        blockers.append("SURROGACY_ASSUMPTION_UNSUPPORTED")
    if value["comparability_assumption"] is not True:
        blockers.append("SURROGATE_COMPARABILITY_UNSUPPORTED")
    if value["treatment_family_validation"] is not True:
        blockers.append("TREATMENT_FAMILY_NOT_VALIDATED")
    if value["historical_validation"] is not True:
        blockers.append("HISTORICAL_SURROGATE_VALIDATION_FAILED")
    if not isinstance(value["negative_or_failure_cases"], list) or not value["negative_or_failure_cases"]:
        blockers.append("SURROGATE_FAILURE_CASES_MISSING")
    if value["measurement_maturity_status"] != "mature":
        blockers.append("LONG_TERM_OUTCOME_NOT_MATURE")
    if value.get("bridge_validation_completed") is not True:
        blockers.append("SURROGATE_BRIDGE_VALIDATION_PENDING")

    if mode == "surrogate_endpoint_only":
        blockers.append("SURROGATE_ENDPOINT_ONLY")
    status = "qualified_for_bounded_external_estimation" if not blockers else "not_yet_qualified"
    return {
        "status": status,
        "claim_ceiling": "CE4" if not blockers else "CE3",
        "blockers": sorted(set(blockers)),
        "required_outputs": [
            "long_term_effect_interval", "surrogate_index_effect_interval", "surrogacy_bias_sensitivity",
            "censoring_and_competing_risk_diagnostics", "failure_case_performance", "treatment_family_scope",
        ],
        "surrogate_effect_is_not_long_term_effect": True,
        "long_term_effect_estimated": False,
        "external_qualified_estimation_required": True,
    }


if __name__ == "__main__":
    cli_main(evaluate_long_term_surrogate, __doc__ or "Evaluate long-term surrogate evidence")
