#!/usr/bin/env python3
"""Validate RDD/IV identification contracts before verified backend execution."""

from __future__ import annotations

from backend_contract import require_verified_backend
from ecae_common import ECAEError, cli_main


def evaluate_rdd_iv(value: dict) -> dict:
    method=value.get("method")
    if method=="RDD":
        required=["running_variable","running_variable_frozen","cutoff","cutoff_frozen","assignment_type","bandwidth_rule","kernel","local_polynomial_order","robust_bias_correction","manipulation_test","covariate_continuity","placebo_cutoffs","bandwidth_sensitivity","polynomial_sensitivity","donut_sensitivity","local_population"]
        missing=[field for field in required if field not in value or value[field] in (None,"",[],{})]
        if missing:
            raise ECAEError("RDD_CONTRACT_INCOMPLETE","RDD contract is incomplete",missing)
        if value["assignment_type"] not in {"sharp","fuzzy"}:
            raise ECAEError("INVALID_RDD_TYPE","RDD assignment_type must be sharp or fuzzy")
        if value["running_variable_frozen"] is not True or value["cutoff_frozen"] is not True:
            raise ECAEError("RDD_CUTOFF_NOT_FROZEN","Running variable and cutoff must be frozen before outcome inspection")
        if value["local_polynomial_order"] != 1:
            raise ECAEError("RDD_PRIMARY_ORDER_INVALID","The primary RDD specification must be local linear; higher orders belong only in sensitivity analysis")
        if value["robust_bias_correction"] is not True:
            raise ECAEError("RDD_RBC_REQUIRED","Robust bias-corrected inference is required")
        if value["bandwidth_rule"] not in {"mserd","msetwo","cerrd","certwo"} or value["kernel"] not in {"triangular","uniform","epanechnikov"}:
            raise ECAEError("RDD_SPECIFICATION_INVALID","RDD bandwidth or kernel is outside the frozen supported set")
        if value["assignment_type"] == "fuzzy" and not value.get("treatment_column"):
            raise ECAEError("FUZZY_RDD_TREATMENT_MISSING","Fuzzy RDD requires an observed treatment column")
        ceiling="CE4_or_CE5_local_only"
        backend_id="rdd_local"
    elif method=="IV":
        required=["instrument","treatment","outcome","estimand","relevance_evidence","exclusion_argument","independence_argument","monotonicity_argument","complier_population","estimator","weak_instrument_robust_inference","first_stage_diagnostics","reduced_form"]
        missing=[field for field in required if not value.get(field)]
        if missing:
            raise ECAEError("IV_CONTRACT_INCOMPLETE","IV contract is incomplete",missing)
        if value["estimator"] not in {"2SLS","LIML"}:
            raise ECAEError("IV_ESTIMATOR_INVALID","IV estimator must be 2SLS or LIML")
        if value["weak_instrument_robust_inference"] not in {"anderson_rubin","conditional_likelihood_ratio","both"}:
            raise ECAEError("WEAK_IV_INFERENCE_REQUIRED","Use Anderson-Rubin, conditional likelihood ratio, or both")
        if value["estimand"] not in {"LATE","CACE"}:
            raise ECAEError("IV_ESTIMAND_INVALID","The supported causal interpretation is LATE/CACE only")
        ceiling="CE4_LATE_only"
        backend_id="weak_iv"
    else:
        raise ECAEError("UNSUPPORTED_METHOD","method must be RDD or IV")
    backend=require_verified_backend(backend_id)
    return {"status":"ready_for_backend_execution","method":method,"backend":backend,"claim_ceiling":ceiling,"generalization_prohibited":True}


if __name__ == "__main__":
    cli_main(evaluate_rdd_iv, __doc__ or "Evaluate RDD or IV")
