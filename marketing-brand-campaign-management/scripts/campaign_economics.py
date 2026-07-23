#!/usr/bin/env python3
"""Mature campaign contribution with explicit revenue and cost waterfall."""
from mbcm_common import finite, require, run_cli, text

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
    return {"currency":currency,"gross_revenue":gross,"net_revenue":net,
            "contribution_before_marketing":before,"campaign_contribution":contribution,
            "contribution_per_mature_order":contribution/q if q else None,
            "decision_signal":"positive" if contribution>0 else "zero" if contribution==0 else "negative",
            "warnings":warnings}
if __name__=="__main__": run_cli(calculate,"campaign_economics")
