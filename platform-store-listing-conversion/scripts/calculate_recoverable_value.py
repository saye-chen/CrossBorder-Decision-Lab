#!/usr/bin/env python3
from d08_common import number, run_cli

def calculate(data):
    visits=number(data.get("qualified_visits"),"qualified_visits")
    gap=number(data.get("conversion_gap"),"conversion_gap"); share=number(data.get("recoverable_share"),"recoverable_share")
    if gap>1 or share>1: raise ValueError("conversion_gap and recoverable_share must be <= 1")
    margin=data.get("mature_contribution_per_order",{}); lo=number(margin.get("low"),"margin.low",False); hi=number(margin.get("high"),"margin.high",False)
    if lo>hi: raise ValueError("margin.low exceeds margin.high")
    orders=visits*gap*share; cost=number(data.get("implementation_cost",0),"implementation_cost")
    return {"status":"ok","recoverable_orders":orders,"contribution_range":[orders*lo-cost,orders*hi-cost],"currency":data.get("currency"),"precision":"scenario_range"}
if __name__ == "__main__": run_cli(calculate,"D08-value-1")
