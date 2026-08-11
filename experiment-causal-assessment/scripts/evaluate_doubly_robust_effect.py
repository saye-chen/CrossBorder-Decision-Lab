#!/usr/bin/env python3
"""Validate target-trial and doubly robust observational contracts."""

from __future__ import annotations

from backend_contract import require_verified_backend
from ecae_common import ECAEError, cli_main


def evaluate_doubly_robust_effect(value: dict) -> dict:
    required=["method","target_trial","estimand","dag_ref","adjustment_set","all_covariates_pretreatment","cross_fitting","cross_fit_folds","out_of_fold_nuisance_predictions","overlap_diagnostics","nuisance_models","nuisance_model_selection_frozen","trimming_policy","negative_control_or_placebo","unmeasured_confounding_sensitivity","influence_function_interval","seed_contract"]
    missing=[field for field in required if field not in value or value[field] in (None,"",[],{})]
    if missing:
        raise ECAEError("OBSERVATIONAL_CONTRACT_INCOMPLETE","Observational causal contract is incomplete",missing)
    if value["all_covariates_pretreatment"] is not True:
        raise ECAEError("BAD_CONTROL","All adjustment covariates must be pretreatment")
    if value["cross_fitting"] is not True:
        raise ECAEError("CROSS_FITTING_REQUIRED","AIPW/TMLE/DML execution requires cross-fitting")
    if not isinstance(value["cross_fit_folds"],int) or isinstance(value["cross_fit_folds"],bool) or value["cross_fit_folds"] < 2:
        raise ECAEError("CROSS_FIT_FOLDS_INVALID","At least two cross-fitting folds are required")
    if value["out_of_fold_nuisance_predictions"] is not True:
        raise ECAEError("NUISANCE_LEAKAGE","Every nuisance prediction used in the score must be out-of-fold")
    if value["nuisance_model_selection_frozen"] is not True:
        raise ECAEError("NUISANCE_SELECTION_NOT_FROZEN","Nuisance model library and selection rule must be frozen before effect inspection")
    if value["influence_function_interval"] is not True:
        raise ECAEError("INFLUENCE_FUNCTION_INTERVAL_REQUIRED","Influence-function or orthogonal-score uncertainty is required")
    if value.get("overlap_status") not in {"pass","restricted_estimand"}:
        raise ECAEError("OVERLAP_NOT_ESTABLISHED","Overlap must pass or estimand must be explicitly restricted")
    method=value["method"]
    backend_ids={"AIPW":"observational_aipw","TMLE":"observational_tmle","DML":"observational_dml"}
    if method not in backend_ids:
        raise ECAEError("OBSERVATIONAL_METHOD_INVALID","method must be AIPW, TMLE, or DML")
    if value["estimand"] not in {"ATE","ATT"}:
        raise ECAEError("OBSERVATIONAL_ESTIMAND_UNSUPPORTED","Current point-treatment backends support ATE or ATT only")
    backend=require_verified_backend(backend_ids[method])
    return {"status":"ready_for_backend_execution","backend":backend,"required_outputs":["effect","influence_curve_interval","propensity_distribution","balance","effective_sample","trimming_estimand","negative_control","confounding_tipping_point"],"claim_ceiling":"CE4"}


if __name__ == "__main__":
    cli_main(evaluate_doubly_robust_effect, __doc__ or "Evaluate doubly robust effect")
