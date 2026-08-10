#!/usr/bin/env python3
"""Check whether a causal analysis has method-compatible sensitivity coverage."""

from __future__ import annotations

from ecae_common import ECAEError, cli_main


REQUIRED={
    "randomized":{"missingness","contamination","outliers","metric_window"},
    "did":{"parallel_trends","anticipation","composition","functional_form","placebo"},
    "synthetic_control":{"donor_pool","leave_one_out","in_space_placebo","time_placebo","pre_fit","weight_concentration"},
    "synthetic_did":{"donor_pool","leave_one_out","in_space_placebo","time_placebo","pre_fit","unit_time_weight_concentration","variance_method"},
    "rdd":{"bandwidth","polynomial_order","donut","placebo_cutoff","manipulation"},
    "iv":{"weak_instrument","exclusion_violation","monotonicity","alternative_instruments"},
    "observational_aipw":{"unmeasured_confounding","overlap_trimming","nuisance_models","negative_control","measurement_error","cross_fit_splits"},
    "observational_tmle":{"unmeasured_confounding","overlap_trimming","nuisance_models","negative_control","measurement_error","targeting_convergence","cross_fit_splits"},
    "observational_dml":{"unmeasured_confounding","overlap_trimming","nuisance_models","negative_control","measurement_error","cross_fit_splits","split_variability"},
    "hte":{"honest_split","overlap","subgroup_stability","policy_value_holdout","multiple_subgroups","calibration","ranking_metric","split_seed_variability","capacity_cost_fairness","deployment_drift"},
    "surrogate":{"surrogacy_violation","sample_comparability","treatment_family_shift","surrogate_paradox","outcome_maturity","censoring_competing_risk","failure_cases"},
    "transportability":{"effect_modifier_omission","support_overlap","sampling_score_models","weight_truncation","weight_dominance","estimand_shift","treatment_measurement_shift","temporal_drift","bridge_validation","F02_applicability"}
}


def evaluate_sensitivity(value: dict) -> dict:
    family=value.get("method_family")
    if family not in REQUIRED:
        raise ECAEError("UNKNOWN_METHOD_FAMILY","No sensitivity contract registered for method_family")
    analyses=value.get("analyses")
    if not isinstance(analyses,list):
        raise ECAEError("INVALID_SENSITIVITY_LIST","analyses must be a list")
    observed={item.get("threat") for item in analyses if item.get("status") in {"pass","fail","warning"}}
    missing=sorted(REQUIRED[family]-observed)
    failed=sorted(item.get("threat") for item in analyses if item.get("status")=="fail")
    status="pass" if not missing and not failed else "fail"
    return {"status":status,"method_family":family,"required":sorted(REQUIRED[family]),"missing":missing,"failed":failed,"claim_impact":"block_ce4" if missing or failed else "none"}


if __name__ == "__main__":
    cli_main(evaluate_sensitivity, __doc__ or "Evaluate sensitivity")
