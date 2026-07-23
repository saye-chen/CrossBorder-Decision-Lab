#!/usr/bin/env python3
"""Aggregate cohort CLV, acquisition quality and CAC payback without customer-level ownership."""
from __future__ import annotations
from mbcm_common import finite, require, run_cli, ModelError, sequence, text

def calculate(d):
    require(d,"cohorts","discount_rate_per_period","currency")
    rate=finite(d["discount_rate_per_period"],"discount_rate_per_period",0,1)
    out=[]
    for i,row in enumerate(sequence(d["cohorts"],"cohorts",False)):
        require(row,"cohort_id","acquired_customers","acquisition_cost","retention_rates",
                "contribution_per_active","maximum_payback_periods")
        acquired=finite(row["acquired_customers"],f"cohorts[{i}].acquired_customers",0)
        if acquired<=0: raise ModelError(f"cohorts[{i}]:positive_acquired_customers_required")
        cac=finite(row["acquisition_cost"],f"cohorts[{i}].acquisition_cost",0)/acquired
        retention=[finite(x,f"cohorts[{i}].retention_rates",0,1) for x in sequence(row["retention_rates"],"retention_rates",False)]
        contribution=[finite(x,f"cohorts[{i}].contribution_per_active") for x in sequence(row["contribution_per_active"],"contribution_per_active",False)]
        if len(retention)!=len(contribution): raise ModelError(f"cohorts[{i}]:aligned_periods_required")
        discounted=[]; cumulative=0.0; payback=None
        for t,(r,c) in enumerate(zip(retention,contribution)):
            value=r*c/((1+rate)**t); discounted.append(value); cumulative+=value
            if payback is None and cumulative>=cac: payback=t+1
        clv=sum(discounted); ceiling=int(finite(row["maximum_payback_periods"],"maximum_payback_periods",1))
        out.append({"cohort_id":text(row["cohort_id"],"cohort_id"),"cac":cac,"discounted_clv":clv,
                    "clv_to_cac":clv/cac if cac else None,"payback_periods":payback,
                    "quality_passed":clv>cac and payback is not None and payback<=ceiling})
    return {"method":"aggregate_discounted_cohort_clv","currency":text(d["currency"],"currency"),
            "cohorts":out,"ownership":"CIG_aggregated_input_MBCM_market_decision",
            "forbidden_use":"individual_targeting_or_contact"}
if __name__=="__main__": run_cli(calculate,"aggregate_customer_economics")
