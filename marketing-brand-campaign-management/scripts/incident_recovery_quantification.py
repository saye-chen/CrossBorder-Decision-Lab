#!/usr/bin/env python3
"""Controlled incident impact, recovery half-life and repair-vs-natural NPV."""
from __future__ import annotations
import math
from mbcm_common import finite, require, run_cli, ModelError, sequence, text
from statistics_common import mean, ols

def calculate(d):
    require(d,"affected_pre","affected_post","control_pre","control_post","recovery_gaps",
            "affected_retention","control_retention","repair_cost","repair_incremental_recovery","discount_rate","currency")
    affected_pre=sequence(d["affected_pre"],"affected_pre",False)
    affected_post=sequence(d["affected_post"],"affected_post",False)
    control_pre=sequence(d["control_pre"],"control_pre",False)
    control_post=sequence(d["control_post"],"control_post",False)
    impact=(mean(affected_post,"affected_post")-mean(affected_pre,"affected_pre"))-(mean(control_post,"control_post")-mean(control_pre,"control_pre"))
    gaps=[finite(x,f"recovery_gaps[{i}]",0) for i,x in enumerate(sequence(d["recovery_gaps"],"recovery_gaps",False))]
    positive=[(i,x) for i,x in enumerate(gaps) if x>0]
    if len(positive)<3: raise ModelError("recovery_gaps:three_positive_periods_required")
    fit=ols([i for i,_ in positive],[math.log(x) for _,x in positive],"recovery")
    decay=math.exp(fit["slope"])
    half_life=math.log(0.5)/fit["slope"] if fit["slope"]<0 else None
    rate=finite(d["discount_rate"],"discount_rate",0,1)
    recovery=[finite(x,f"repair_incremental_recovery[{i}]") for i,x in enumerate(sequence(d["repair_incremental_recovery"],"repair_incremental_recovery",False))]
    repair_cost=finite(d["repair_cost"],"repair_cost",0)
    repair_npv=sum(x/((1+rate)**(i+1)) for i,x in enumerate(recovery))-repair_cost
    affected_retention=finite(d["affected_retention"],"affected_retention",0,1)
    control_retention=finite(d["control_retention"],"control_retention",0,1)
    excess_churn=max(0,control_retention-affected_retention)
    return {"method":"controlled_pre_post_and_log_linear_recovery","currency":text(d["currency"],"currency"),
            "controlled_incident_effect":impact,"recovery_decay_per_period":decay,
            "recovery_half_life_periods":half_life,"recovery_fit_r_squared":fit["r_squared"],
            "excess_churn_probability":excess_churn,
            "repair_incremental_npv":repair_npv,
            "repair_recommended":repair_npv>0 and half_life is not None,
            "action_limit":"repair_candidate_not_external_action"}
if __name__=="__main__": run_cli(calculate,"incident_recovery_quantification")
