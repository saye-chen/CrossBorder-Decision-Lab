#!/usr/bin/env python3
"""Bridge observed/attributed/incremental outcomes to mature contribution."""
from mbcm_common import finite, require, run_cli, ModelError, text

def calculate(d):
    require(d,"observed_orders","attributed_orders","counterfactual_orders","incremental_net_revenue",
            "incremental_cogs","incremental_fulfillment","incremental_platform_fees",
            "incremental_service_returns","incremental_channel_cost","incremental_offer_cost",
            "incremental_fixed_cost","ci_lower_orders","ci_upper_orders","currency")
    observed=finite(d["observed_orders"],"observed_orders",0)
    attributed=finite(d["attributed_orders"],"attributed_orders",0)
    counter=finite(d["counterfactual_orders"],"counterfactual_orders",0)
    if attributed>observed: raise ModelError("attributed_orders:cannot_exceed_observed_orders")
    low=finite(d["ci_lower_orders"],"ci_lower_orders"); high=finite(d["ci_upper_orders"],"ci_upper_orders")
    if low>high: raise ModelError("confidence_interval:lower_above_upper")
    inc_orders=observed-counter
    revenue=finite(d["incremental_net_revenue"],"incremental_net_revenue")
    costs=sum(finite(d[k],k,0) for k in ("incremental_cogs","incremental_fulfillment",
        "incremental_platform_fees","incremental_service_returns","incremental_channel_cost",
        "incremental_offer_cost","incremental_fixed_cost"))
    contribution=revenue-costs
    inc_orders=observed-counter
    if not (low<=inc_orders<=high): raise ModelError("confidence_interval:does_not_contain_point_estimate")
    return {"currency":text(d["currency"],"currency"),"observed_orders":observed,"attributed_orders":attributed,
            "incremental_orders":inc_orders,"incremental_order_interval":[low,high],
            "mature_incremental_contribution":contribution,
            "causal_claim_allowed":low>0 and contribution>0,
            "attribution_equals_incrementality":attributed==inc_orders}
if __name__=="__main__": run_cli(calculate,"incrementality_bridge")
