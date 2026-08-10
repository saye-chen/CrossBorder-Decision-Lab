#!/usr/bin/env python3
"""Translate qualified causal effects into scenario-bounded incremental economics."""

from __future__ import annotations

from datetime import timezone

from ecae_common import ECAEError, cli_main, parse_time, require_positive


def _product_interval(a_lower,a_upper,b_lower,b_upper):
    candidates=[a_lower*b_lower,a_lower*b_upper,a_upper*b_lower,a_upper*b_upper]
    return min(candidates),max(candidates)


def calculate_incremental_economics(value:dict)->dict:
    grade=value.get("causal_evidence_grade")
    if grade not in {"CE4","CE5"}:
        raise ECAEError("CAUSAL_EVIDENCE_INELIGIBLE","Incremental economics require CE4 or CE5; use attributed/associated economics otherwise",{"grade":grade})
    effect=value.get("effect_interval",{})
    if not all(key in effect for key in ["lower","point","upper"]):
        raise ECAEError("EFFECT_INTERVAL_INCOMPLETE","Effect interval requires lower, point, upper")
    if effect["lower"]>effect["point"] or effect["point"]>effect["upper"]:
        raise ECAEError("INVALID_EFFECT_INTERVAL","Effect interval must be ordered")
    volume=require_positive(value.get("eligible_volume"),"eligible_volume")
    unit_value=value.get("qualified_unit_value",{})
    required=["lower","point","upper","currency","source_ref","version","valid_until"]
    missing=[field for field in required if field not in unit_value]
    if missing: raise ECAEError("ECONOMIC_PARAMETER_INCOMPLETE","qualified_unit_value is incomplete",missing)
    if unit_value["lower"]>unit_value["point"] or unit_value["point"]>unit_value["upper"]:
        raise ECAEError("INVALID_VALUE_INTERVAL","Unit-value interval must be ordered")
    as_of=parse_time(value.get("as_of_time"),"as_of_time")
    valid_until=parse_time(unit_value["valid_until"],"qualified_unit_value.valid_until")
    if valid_until<=as_of:
        raise ECAEError("ECONOMIC_PARAMETER_EXPIRED","Economic parameter bundle is expired")
    costs=value.get("costs",{})
    for key in ["implementation","opportunity","risk"]:
        require_positive(costs.get(key,0),f"costs.{key}",allow_zero=True)
    total_cost=sum(float(costs.get(key,0)) for key in ["implementation","opportunity","risk"])
    quantity=[effect[key]*volume for key in ["lower","point","upper"]]
    gross_lower,gross_upper=_product_interval(quantity[0],quantity[2],unit_value["lower"],unit_value["upper"])
    gross_point=quantity[1]*unit_value["point"]
    net_lower,net_point,net_upper=gross_lower-total_cost,gross_point-total_cost,gross_upper-total_cost
    denominator=volume*unit_value["point"]
    break_even=None if denominator==0 else total_cost/denominator
    if net_lower>0: status="value_supported"
    elif net_upper<0: status="value_not_supported"
    elif net_point<0: status="downside_risk"
    else: status="precision_insufficient"
    return {"currency":unit_value["currency"],"effect_quantity":{"lower":quantity[0],"point":quantity[1],"upper":quantity[2],"unit":value.get("effect_unit","incremental_outcome_per_eligible_unit")},"incremental_value_interval":{"lower":net_lower,"point":net_point,"upper":net_upper},"break_even_effect":break_even,"costs":{**costs,"total":total_cost},"scenarios":[{"name":"bear","net_value":net_lower},{"name":"base","net_value":net_point},{"name":"bull","net_value":net_upper}],"economic_status":status,"causal_eligibility":grade,"parameter_source_ref":unit_value["source_ref"],"parameter_version":unit_value["version"],"business_owner_decision_required":True,"external_write":False}


if __name__=="__main__":
    cli_main(calculate_incremental_economics,__doc__ or "Calculate incremental economics")
