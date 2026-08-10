#!/usr/bin/env python3
"""Validate honest HTE, uplift-ranking, and policy-value contracts before execution."""

from __future__ import annotations

from backend_contract import require_verified_backend
from ecae_common import ECAEError, cli_main


REQUIRED = [
    "estimand", "mode", "source_design", "source_estimand", "source_causal_grade",
    "treatment_versions", "target_population", "effect_modifier_set",
    "all_effect_modifiers_pretreatment", "honest_evaluation", "development_sample_ref",
    "evaluation_sample_ref", "samples_disjoint", "sample_split_or_crossfit",
    "split_assignment_frozen", "split_hash", "model_selection_frozen",
    "hyperparameter_tuning_scope", "seed_contract", "overlap_diagnostics",
    "overlap_status", "subgroup_or_score_definition", "definition_frozen_before_evaluation",
    "holdout_policy_value", "policy_rule_frozen_before_evaluation", "baseline_policies",
    "capacity_constraint", "cost_policy", "fairness_review_ref", "multiple_testing_policy",
    "calibration_plan", "stability_plan",
]


def _missing(value: dict) -> list[str]:
    return [field for field in REQUIRED if field not in value or value[field] in (None, "", [], {})]


def evaluate_heterogeneous_effect(value: dict) -> dict:
    missing = _missing(value)
    if missing:
        raise ECAEError("HTE_CONTRACT_INCOMPLETE", "HTE/uplift contract is incomplete", missing)

    if value["estimand"] not in {"GATE", "CATE_ranking", "policy_value"}:
        raise ECAEError("HTE_ESTIMAND_INVALID", "estimand must be GATE, CATE_ranking, or policy_value")
    if value["mode"] not in {"confirmatory", "exploratory", "policy_learning"}:
        raise ECAEError("HTE_MODE_INVALID", "mode must be confirmatory, exploratory, or policy_learning")
    if value["source_design"] not in {"randomized", "observational_unconfounded"}:
        raise ECAEError("HTE_SOURCE_DESIGN_INVALID", "source_design must be randomized or observational_unconfounded")
    if value["source_causal_grade"] not in {"CE4", "CE5"}:
        raise ECAEError("HTE_SOURCE_GRADE_INADEQUATE", "HTE requires a qualified CE4 or CE5 source effect")
    if not isinstance(value["effect_modifier_set"], list) or not value["effect_modifier_set"]:
        raise ECAEError("HTE_MODIFIER_SET_INVALID", "At least one effect modifier must be registered")
    if value["all_effect_modifiers_pretreatment"] is not True:
        raise ECAEError("POSTTREATMENT_MODIFIER", "HTE effect modifiers must be measured before treatment")

    if value["honest_evaluation"] is not True or value["sample_split_or_crossfit"] is not True:
        raise ECAEError("DISHONEST_HTE", "HTE discovery, tuning, and evaluation must be separated")
    if value["samples_disjoint"] is not True or value["development_sample_ref"] == value["evaluation_sample_ref"]:
        raise ECAEError("HTE_EVALUATION_LEAKAGE", "Development and final evaluation samples must be disjoint")
    if value["split_assignment_frozen"] is not True or value["model_selection_frozen"] is not True:
        raise ECAEError("HTE_SELECTION_NOT_FROZEN", "Splits, model selection, and tuning policy must be frozen before evaluation outcomes are inspected")
    if value.get("evaluation_outcomes_used_for_training") is True:
        raise ECAEError("HTE_EVALUATION_LEAKAGE", "Evaluation outcomes cannot train or select the CATE model or policy")
    if value["definition_frozen_before_evaluation"] is not True:
        raise ECAEError("HTE_DEFINITION_NOT_FROZEN", "Subgroups or prioritization scores must be frozen before evaluation")
    if value.get("individual_true_effect_claimed") is True:
        raise ECAEError("INDIVIDUAL_CAUSAL_CLAIM_PROHIBITED", "CATE/uplift scores are not individual true effects")

    if value["overlap_status"] not in {"pass", "restricted_estimand"}:
        raise ECAEError("HTE_OVERLAP_NOT_ESTABLISHED", "HTE overlap must pass or the target estimand must be explicitly restricted")
    if value["overlap_status"] == "restricted_estimand" and not value.get("restricted_population_definition"):
        raise ECAEError("HTE_RESTRICTED_ESTIMAND_UNDEFINED", "Restricted overlap requires an explicit target-population restriction")
    if value["source_design"] == "observational_unconfounded" and not value.get("observational_identification_ref"):
        raise ECAEError("HTE_OBSERVATIONAL_IDENTIFICATION_MISSING", "Observational HTE must bind the qualified adjustment and nuisance-score analysis")

    baselines = value["baseline_policies"]
    if not isinstance(baselines, list) or not {"treat_all", "treat_none", "current_policy"}.issubset(set(baselines)):
        raise ECAEError("POLICY_BASELINES_INCOMPLETE", "Policy value requires treat_all, treat_none, and current_policy baselines")
    if value["holdout_policy_value"] is not True or value["policy_rule_frozen_before_evaluation"] is not True:
        raise ECAEError("POLICY_VALUE_NOT_HONEST", "Policy rules and thresholds must be frozen and evaluated on an independent holdout")
    if value.get("policy_uses_protected_attribute_without_approval") is True:
        raise ECAEError("POLICY_FAIRNESS_APPROVAL_REQUIRED", "Protected-attribute policy use requires explicit owner approval")

    if value["mode"] == "confirmatory" and value["multiple_testing_policy"] in {"none", "exploratory_only"}:
        raise ECAEError("HTE_MULTIPLICITY_UNCONTROLLED", "Confirmatory GATE families require registered multiplicity control")
    if value["mode"] == "exploratory" and value.get("confirmatory_language_requested") is True:
        raise ECAEError("EXPLORATORY_HTE_OVERCLAIM", "Exploratory heterogeneity cannot use confirmatory language")

    backend = require_verified_backend("hte_uplift")
    return {
        "status": "ready_for_backend_execution",
        "backend": backend,
        "required_outputs": [
            "GATE_intervals_and_group_sizes", "BLP_or_calibration", "holdout_AUTOC_Qini_with_uncertainty",
            "policy_value_interval_vs_treat_all_none_current", "overlap_and_effective_sample",
            "split_and_seed_binding", "subgroup_and_policy_stability", "capacity_cost_and_fairness_limits",
        ],
        "claim_ceiling": "CE3" if value["mode"] == "exploratory" else "CE4",
        "individual_action_authorized": False,
        "business_policy_owner_required": True,
    }


if __name__ == "__main__":
    cli_main(evaluate_heterogeneous_effect, __doc__ or "Evaluate heterogeneous effects")
