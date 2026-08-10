#!/usr/bin/env python3
"""Evaluate native 2x2 DiD or fail-close staggered DiD to a verified backend."""

from __future__ import annotations

import math

from backend_contract import require_verified_backend
from ecae_common import ECAEError, cli_main, confidence_interval, two_sided_p_from_z


def evaluate_did(value: dict) -> dict:
    design = value.get("design")
    if design == "staggered":
        if value.get("estimator") in {"TWFE", "two_way_fixed_effects", "naive_event_study"}:
            raise ECAEError("NAIVE_TWFE_PROHIBITED", "Staggered treatment with heterogeneous timing/effects cannot use naive TWFE")
        required = [
            "estimand", "treatment_timing_frozen", "no_anticipation", "anticipation_periods",
            "all_covariates_pretreatment", "panel_structure", "simultaneous_confidence_band",
            "pretrend_event_window", "composition_policy", "reversal_policy", "spillover_assessment",
        ]
        missing = [field for field in required if field not in value or value[field] in (None, "", [], {})]
        if missing:
            raise ECAEError("STAGGERED_DID_CONTRACT_INCOMPLETE", "Staggered DiD identification contract is incomplete", missing)
        if value.get("estimator") != "group_time_ATT":
            raise ECAEError("STAGGERED_DID_ESTIMATOR_INVALID", "Staggered DiD requires the registered group-time ATT estimator")
        if value.get("control_group") not in {"never_treated","not_yet_treated"}:
            raise ECAEError("INVALID_STAGGERED_CONTROL", "Use never-treated or not-yet-treated controls")
        if value["treatment_timing_frozen"] is not True:
            raise ECAEError("TREATMENT_TIMING_NOT_FROZEN", "First-treatment timing must be frozen independently of post-treatment outcomes")
        if value["no_anticipation"] is not True and not isinstance(value.get("anticipation_periods"), int):
            raise ECAEError("ANTICIPATION_NOT_MODELED", "Anticipation must be ruled out or represented by a non-negative registered anticipation window")
        if not isinstance(value["anticipation_periods"], int) or isinstance(value["anticipation_periods"], bool) or value["anticipation_periods"] < 0:
            raise ECAEError("ANTICIPATION_WINDOW_INVALID", "anticipation_periods must be a non-negative integer")
        if value["all_covariates_pretreatment"] is not True:
            raise ECAEError("BAD_CONTROL", "Staggered DiD covariates must be determined before treatment")
        if value["simultaneous_confidence_band"] is not True:
            raise ECAEError("POINTWISE_EVENT_STUDY_PROHIBITED", "Confirmatory event-time inference requires simultaneous confidence bands")
        if value["reversal_policy"] not in {"no_reversal", "exclude_after_reversal", "separate_estimand"}:
            raise ECAEError("TREATMENT_REVERSAL_UNRESOLVED", "Treatment reversal requires a frozen handling rule")
        backend = require_verified_backend("staggered_did")
        return {"status":"ready_for_backend_execution","backend":backend,"estimand":value["estimand"],"required_outputs":["group_time_ATT","aggregation_weights","event_time_effects","simultaneous_intervals","pretrend_diagnostics","anticipation_sensitivity","composition_sensitivity","control_group"]}
    if design != "2x2":
        raise ECAEError("UNSUPPORTED_DID_DESIGN", "design must be 2x2 or staggered")
    if value.get("no_anticipation") is not True or not value.get("common_shock_argument"):
        raise ECAEError("IDENTIFICATION_CONTRACT_INCOMPLETE", "2x2 DiD requires no_anticipation and a common-shock/parallel-trend argument")
    cells = value.get("cells")
    required_cells = {"treated_pre","treated_post","control_pre","control_post"}
    if not isinstance(cells, dict) or set(cells) != required_cells:
        raise ECAEError("INVALID_DID_CELLS", "Exactly four 2x2 cells are required")
    for name, cell in cells.items():
        if not all(field in cell for field in ["n","mean","variance"]) or cell["n"] < 2 or cell["variance"] < 0:
            raise ECAEError("INVALID_DID_CELL", f"Invalid cell summary: {name}")
    t_pre,t_post,c_pre,c_post=(cells[name] for name in ["treated_pre","treated_post","control_pre","control_post"])
    estimate=(t_post["mean"]-t_pre["mean"])-(c_post["mean"]-c_pre["mean"])
    dependence = value.get("data_structure")
    if dependence != "independent_repeated_cross_sections":
        raise ECAEError("DEPENDENCE_BACKEND_REQUIRED", "Native 2x2 variance only supports independent repeated cross-sections; panel/cluster data need verified inference")
    se=math.sqrt(sum(cell["variance"]/cell["n"] for cell in cells.values()))
    level=float(value.get("confidence_level",0.95))
    lower,upper=confidence_interval(estimate,se,level)
    z=estimate/se if se>0 else (0.0 if estimate==0 else math.copysign(math.inf,estimate))
    p=1.0 if se==0 and estimate==0 else (0.0 if se==0 else two_sided_p_from_z(z))
    warnings=["A single pre-period cannot empirically diagnose parallel trends."]
    return {"design":"2x2_DiD","estimand":"ATT_under_parallel_trends","estimate":estimate,"standard_error":se,"confidence_interval":{"level":level,"lower":lower,"upper":upper,"method":"independent_cell_normal_approximation"},"p_value":p,"identification_assumptions":["parallel trends/common shocks","no anticipation","stable composition","no concurrent differential intervention"],"warnings":warnings,"claim_ceiling":"CE4"}


if __name__ == "__main__":
    cli_main(evaluate_did, __doc__ or "Evaluate DiD")
