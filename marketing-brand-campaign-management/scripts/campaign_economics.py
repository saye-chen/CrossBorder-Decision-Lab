#!/usr/bin/env python3
"""Mature campaign contribution with explicit revenue and cost waterfall."""
from mbcm_common import finite, require, run_cli, text, ModelError

def calculate(d):
    require(d,"quantity","unit_price","merchant_discount","refunds","tax","cogs","fulfillment",
            "platform_fees","service_cost","channel_cost","offer_cost","campaign_fixed_cost","currency")
    q=finite(d["quantity"],"quantity",0); price=finite(d["unit_price"],"unit_price",0)
    gross=q*price
    costs={k:finite(d[k],k,0) for k in ("merchant_discount","refunds","tax","cogs","fulfillment",
            "platform_fees","service_cost","channel_cost","offer_cost","campaign_fixed_cost")}
    net=gross-costs["merchant_discount"]-costs["refunds"]-costs["tax"]
    before=net-costs["cogs"]-costs["fulfillment"]-costs["platform_fees"]-costs["service_cost"]
    contribution=before-costs["channel_cost"]-costs["offer_cost"]-costs["campaign_fixed_cost"]
    currency=text(d["currency"],"currency")
    if costs["merchant_discount"]+costs["refunds"]+costs["tax"]>gross:
        warnings=["revenue_deductions_exceed_gross"]
    else: warnings=[]
    stress=d.get("stress",{})
    if not isinstance(stress,dict): raise ModelError("stress:object_required")
    volume_factor=finite(stress.get("volume_factor",1),"stress.volume_factor",0)
    price_factor=finite(stress.get("price_factor",1),"stress.price_factor",0)
    variable_cost_factor=finite(stress.get("variable_cost_factor",1),"stress.variable_cost_factor",0)
    stressed_gross=q*volume_factor*price*price_factor
    stressed_variable=sum(costs[k] for k in ("merchant_discount","refunds","tax","cogs","fulfillment",
                                             "platform_fees","service_cost","channel_cost","offer_cost"))
    stressed_contribution=stressed_gross-stressed_variable*variable_cost_factor-costs["campaign_fixed_cost"]
    first_flip=None
    if gross>0:
        first_flip=(stressed_variable*variable_cost_factor+costs["campaign_fixed_cost"])/(q*price) if q*price else None
    return {"currency":currency,"gross_revenue":gross,"net_revenue":net,
            "contribution_before_marketing":before,"campaign_contribution":contribution,
            "contribution_per_mature_order":contribution/q if q else None,
            "cost_waterfall":costs,
            "stress":{"volume_factor":volume_factor,"price_factor":price_factor,
                      "variable_cost_factor":variable_cost_factor,
                      "campaign_contribution":stressed_contribution},
            "break_even_volume_factor_under_stress_costs":first_flip,
            "decision_signal":"positive" if contribution>0 else "zero" if contribution==0 else "negative",
            "action_limit":"proceed" if contribution>0 and stressed_contribution>0 else "test_or_reduce" if contribution>0 else "stop",
            "warnings":warnings}
if __name__=="__main__": run_cli(calculate,"campaign_economics")
