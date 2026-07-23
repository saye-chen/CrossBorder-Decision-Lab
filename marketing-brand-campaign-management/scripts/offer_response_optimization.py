#!/usr/bin/env python3
"""Estimate price elasticity and optimize nonlinear Offer depth on a declared grid."""
from __future__ import annotations
import math
from statistics import NormalDist
from mbcm_common import finite, require, run_cli, ModelError, sequence, text
from statistics_common import ols

def calculate(d):
    require(d,"historical_price","historical_orders","reference_price","candidate_discounts",
            "unit_variable_cost","fixed_cost","fatigue_rate","currency")
    prices=[finite(x,f"historical_price[{i}]",0) for i,x in enumerate(sequence(d["historical_price"],"historical_price",False))]
    orders=[finite(x,f"historical_orders[{i}]",0) for i,x in enumerate(sequence(d["historical_orders"],"historical_orders",False))]
    if len(prices)!=len(orders) or len(prices)<3 or any(x<=0 for x in prices+orders):
        raise ModelError("history:aligned_positive_three_or_more_required")
    fit=ols([math.log(x) for x in prices],[math.log(x) for x in orders],"elasticity")
    elasticity=fit["slope"]
    reference=finite(d["reference_price"],"reference_price",0)
    unit_cost=finite(d["unit_variable_cost"],"unit_variable_cost",0)
    fixed=finite(d["fixed_cost"],"fixed_cost",0)
    fatigue=finite(d["fatigue_rate"],"fatigue_rate",0,1)
    anchor_orders=math.exp(fit["intercept"]+elasticity*math.log(reference))
    rows=[]
    discounts=sequence(d["candidate_discounts"],"candidate_discounts",False)
    if len(discounts)!=len(set(discounts)): raise ModelError("candidate_discounts:unique_required")
    for i,raw in enumerate(discounts):
        discount=finite(raw,f"candidate_discounts[{i}]",0,0.95)
        price=reference*(1-discount)
        predicted=math.exp(fit["intercept"]+elasticity*math.log(price))
        fatigue_multiplier=max(0,1-fatigue*discount)
        adjusted=predicted*fatigue_multiplier
        contribution=adjusted*(price-unit_cost)-fixed
        rows.append({"discount":discount,"price":price,"predicted_orders":predicted,
                     "fatigue_adjusted_orders":adjusted,"contribution":contribution})
    feasible=[x for x in rows if x["price"]>=unit_cost]
    best=max(feasible,key=lambda x:x["contribution"]) if feasible else None
    z=NormalDist().inv_cdf(0.975)
    elasticity_interval=[elasticity-z*fit["slope_se"],elasticity+z*fit["slope_se"]]
    return {"method":"log_log_elasticity_grid_optimization","currency":text(d["currency"],"currency"),
            "elasticity":elasticity,"elasticity_se":fit["slope_se"],"r_squared":fit["r_squared"],
            "elasticity_interval_95":elasticity_interval,
            "reference_orders":anchor_orders,"candidates":rows,"optimal_discount":None if best is None else best["discount"],
            "optimal_contribution":None if best is None else best["contribution"],
            "nonlinearity_explicit":True,
            "action_limit":"test_required" if len(prices)<8 or fit["r_squared"] is None or fit["r_squared"]<0.5 or elasticity_interval[0]<=0<=elasticity_interval[1] else "bounded_offer_candidate"}
if __name__=="__main__": run_cli(calculate,"offer_response_optimization")
