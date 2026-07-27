#!/usr/bin/env python3
"""Offer full cost, non-incremental subsidy and break-even incremental rate."""
from mbcm_common import finite, require, run_cli, ModelError, text

def calculate(d):
    require(d,"eligible","redeemed_orders","incremental_orders","merchant_discount_per_redeemed",
            "gift_cost_per_redeemed","shipping_subsidy_per_redeemed","guarantee_cost",
            "fraud_loss","service_cost","incremental_cm_per_order","pull_forward_loss",
            "cannibalization_loss","fixed_cost","currency")
    eligible=finite(d["eligible"],"eligible",0); redeemed=finite(d["redeemed_orders"],"redeemed_orders",0)
    inc=finite(d["incremental_orders"],"incremental_orders",0)
    if redeemed>eligible: raise ModelError("redeemed_orders:cannot_exceed_eligible")
    if inc>redeemed: raise ModelError("incremental_orders:cannot_exceed_redeemed_orders")
    unit_offer=sum(finite(d[k],k,0) for k in ("merchant_discount_per_redeemed","gift_cost_per_redeemed","shipping_subsidy_per_redeemed"))
    variable=redeemed*unit_offer+sum(finite(d[k],k,0) for k in ("guarantee_cost","fraud_loss","service_cost"))
    losses=sum(finite(d[k],k,0) for k in ("pull_forward_loss","cannibalization_loss","fixed_cost"))
    cm=finite(d["incremental_cm_per_order"],"incremental_cm_per_order")
    total_cost=variable+losses
    net=inc*cm-total_cost
    breakeven=None if redeemed==0 or cm<=0 else total_cost/(redeemed*cm)
    actual_rate=inc/redeemed if redeemed else None
    rate_margin=None if actual_rate is None or breakeven is None else actual_rate-breakeven
    stress=d.get("stress",{})
    if not isinstance(stress,dict): raise ModelError("stress:object_required")
    cm_factor=finite(stress.get("cm_factor",1),"stress.cm_factor",0)
    cost_factor=finite(stress.get("cost_factor",1),"stress.cost_factor",0)
    stressed_net=inc*cm*cm_factor-total_cost*cost_factor
    return {"currency":text(d["currency"],"currency"),"eligible":eligible,"redeemed_orders":redeemed,
            "incremental_orders":inc,"non_incremental_redeemed_orders":redeemed-inc,
            "redemption_rate":redeemed/eligible if eligible else None,
            "incremental_order_rate":actual_rate,
            "offer_cost_all_redeemed":variable,"total_offer_burden":total_cost,
            "cost_components":{"redeemed_variable_cost":redeemed*unit_offer,
                               "guarantee_fraud_service":variable-redeemed*unit_offer,
                               "pull_forward_cannibalization_fixed":losses},
            "incremental_offer_contribution":net,"break_even_incremental_order_rate":breakeven,
            "incremental_rate_margin_to_break_even":rate_margin,
            "stress":{"cm_factor":cm_factor,"cost_factor":cost_factor,
                      "incremental_offer_contribution":stressed_net},
            "passes_economic_gate":net>=0 and cm>0,
            "action_limit":"proceed" if net>=0 and stressed_net>=0 and cm>0 else "test_or_reduce" if net>=0 else "stop"}
if __name__=="__main__": run_cli(calculate,"offer_economics")
