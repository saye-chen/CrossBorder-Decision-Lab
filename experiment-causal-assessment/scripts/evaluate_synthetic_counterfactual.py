#!/usr/bin/env python3
"""Validate SCM/SDID donor and placebo contracts before verified execution."""

from __future__ import annotations

from backend_contract import require_verified_backend
from ecae_common import ECAEError, cli_main


def evaluate_synthetic_counterfactual(value: dict) -> dict:
    method = value.get("method")
    if method not in {"SCM", "SDID"}:
        raise ECAEError("SYNTHETIC_METHOD_INVALID", "method must be SCM or SDID")
    donors = value.get("donor_pool")
    if not isinstance(donors, list) or len(donors) < 2:
        raise ECAEError("DONOR_POOL_INADEQUATE", "At least two frozen donors are required")
    if value.get("donor_pool_frozen_before_post_outcomes") is not True:
        raise ECAEError("POST_OUTCOME_DONOR_SELECTION", "Donor pool must be frozen before post-treatment outcomes")
    contaminated=[item.get("donor_id") for item in donors if item.get("contaminated") is not False or item.get("metric_comparable") is not True or item.get("structural_break") is not False]
    if contaminated:
        raise ECAEError("DONOR_POOL_CONTAMINATED", "Donor qualification failed", contaminated)
    required = ["estimand", "intervention_time_frozen", "pre_period_count", "post_period_count", "uncertainty_method", "donor_dominance_threshold"]
    missing = [field for field in required if field not in value or value[field] in (None, "", [], {})]
    if missing:
        raise ECAEError("SYNTHETIC_CONTRACT_INCOMPLETE", "Synthetic counterfactual contract is incomplete", missing)
    if value["intervention_time_frozen"] is not True:
        raise ECAEError("INTERVENTION_TIME_NOT_FROZEN", "Intervention timing must be frozen before post-treatment outcome inspection")
    if not isinstance(value["pre_period_count"], int) or isinstance(value["pre_period_count"], bool) or value["pre_period_count"] < 4:
        raise ECAEError("PRE_PERIOD_INADEQUATE", "At least four pre-periods are required before backend routing; fit adequacy can still fail later")
    if not isinstance(value["post_period_count"], int) or isinstance(value["post_period_count"], bool) or value["post_period_count"] < 1:
        raise ECAEError("POST_PERIOD_INADEQUATE", "At least one post-period is required")
    threshold = value["donor_dominance_threshold"]
    if not isinstance(threshold, (int, float)) or isinstance(threshold, bool) or not 0 < threshold < 1:
        raise ECAEError("DONOR_DOMINANCE_THRESHOLD_INVALID", "donor_dominance_threshold must be in (0,1)")
    required_sensitivity={"in_space_placebo","time_placebo","leave_one_out","pre_fit","weight_concentration"}
    if method == "SDID":
        required_sensitivity.add("time_weight_concentration")
    if not required_sensitivity.issubset(set(value.get("registered_sensitivity",[]))):
        raise ECAEError("SCM_SENSITIVITY_INCOMPLETE", "SCM/SDID sensitivity suite is incomplete", sorted(required_sensitivity-set(value.get("registered_sensitivity",[]))))
    if method == "SCM":
        if value.get("treated_unit_count") != 1:
            raise ECAEError("SCM_TREATED_UNIT_SCOPE", "The selected SCM backend supports exactly one treated unit")
        if value["uncertainty_method"] != "in_space_placebo_rank":
            raise ECAEError("SCM_UNCERTAINTY_INVALID", "SCM requires registered in-space placebo-rank uncertainty")
        backend_id = "synthetic_control"
    else:
        if value.get("adoption_pattern") != "common_start":
            raise ECAEError("SDID_ADOPTION_SCOPE", "The selected SDID candidate supports a common treatment start only")
        if value["uncertainty_method"] not in {"placebo", "bootstrap", "jackknife"}:
            raise ECAEError("SDID_UNCERTAINTY_INVALID", "SDID uncertainty must be placebo, bootstrap, or jackknife")
        backend_id = "synthetic_did"
    backend=require_verified_backend(backend_id)
    return {"status":"ready_for_backend_execution","method":method,"backend":backend,"donor_count":len(donors),"required_outputs":["unit_weights","time_weights_if_sdid","effective_donor_count","weight_concentration","pre_RMSPE","post_gap","placebo_rank","leave_one_out","uncertainty"]}


if __name__ == "__main__":
    cli_main(evaluate_synthetic_counterfactual, __doc__ or "Evaluate synthetic counterfactual")
