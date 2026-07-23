#!/usr/bin/env python3
"""Quantify brand proxy-to-outcome bridge, price premium and adstock decay."""
from __future__ import annotations
import math
from mbcm_common import finite, require, run_cli, ModelError, sequence, text
from statistics_common import ols, mean

def calculate(d):
    require(d,"brand_proxy","business_outcome","brand_prices","matched_generic_prices",
            "brand_quantities","generic_quantities",
            "decay_rate","currency")
    proxy=[finite(x,f"brand_proxy[{i}]") for i,x in enumerate(sequence(d["brand_proxy"],"brand_proxy",False))]
    outcome=[finite(x,f"business_outcome[{i}]") for i,x in enumerate(sequence(d["business_outcome"],"business_outcome",False))]
    if len(proxy)!=len(outcome): raise ModelError("proxy_outcome:aligned_required")
    decay=finite(d["decay_rate"],"decay_rate",0,0.999)
    stock=[]; carry=0.0
    for value in proxy: carry=value+decay*carry; stock.append(carry)
    bridge=ols(stock,outcome,"brand_bridge")
    brand=[finite(x,f"brand_prices[{i}]",0) for i,x in enumerate(sequence(d["brand_prices"],"brand_prices",False))]
    generic=[finite(x,f"matched_generic_prices[{i}]",0) for i,x in enumerate(sequence(d["matched_generic_prices"],"matched_generic_prices",False))]
    if len(brand)!=len(generic) or any(x<=0 for x in generic): raise ModelError("matched_prices:aligned_positive_required")
    brand_q=[finite(x,f"brand_quantities[{i}]",0) for i,x in enumerate(sequence(d["brand_quantities"],"brand_quantities",False))]
    generic_q=[finite(x,f"generic_quantities[{i}]",0) for i,x in enumerate(sequence(d["generic_quantities"],"generic_quantities",False))]
    if len(brand_q)!=len(brand) or len(generic_q)!=len(generic) or any(x<=0 for x in brand_q+generic_q):
        raise ModelError("price_quantity:aligned_positive_required")
    if len(brand)<3: raise ModelError("price_elasticity:three_or_more_pairs_required")
    brand_elasticity=ols([math.log(x) for x in brand],[math.log(x) for x in brand_q],"brand_elasticity")
    generic_elasticity=ols([math.log(x) for x in generic],[math.log(x) for x in generic_q],"generic_elasticity")
    premiums=[b/g-1 for b,g in zip(brand,generic)]
    half_life=math.log(0.5)/math.log(decay) if 0<decay<1 else 0.0
    return {"method":"adstock_proxy_outcome_ols_and_matched_price_premium",
            "currency":text(d["currency"],"currency"),"decay_rate":decay,"adstock_half_life_periods":half_life,
            "proxy_to_outcome_slope":bridge["slope"],"slope_se":bridge["slope_se"],
            "r_squared":bridge["r_squared"],"average_matched_price_premium":mean(premiums,"premiums"),
            "brand_price_elasticity":brand_elasticity["slope"],
            "generic_price_elasticity":generic_elasticity["slope"],
            "elasticity_difference":brand_elasticity["slope"]-generic_elasticity["slope"],
            "assumptions":["matched_product_comparability","no_omitted_time_varying_driver"],
            "action_limit":"scenario_or_test" if bridge["r_squared"] is None or bridge["r_squared"]<0.5 else "bounded_value_bridge"}
if __name__=="__main__": run_cli(calculate,"brand_value_bridge")
