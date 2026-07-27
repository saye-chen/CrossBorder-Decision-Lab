#!/usr/bin/env python3
"""Falsifiable brand investment scenarios without invented probabilities."""
from mbcm_common import finite, require, run_cli, ModelError, sequence, text

def calculate(d):
    require(d,"scenarios","currency","discount_rate")
    rate=finite(d["discount_rate"],"discount_rate",0,1)
    out=[]; ids=[]
    for i,row in enumerate(sequence(d["scenarios"],"scenarios",allow_empty=False)):
        require(row,"id","current_investment","future_incremental_contributions","avoided_costs","risk_loss","approved_max_loss")
        current=finite(row["current_investment"],f"scenarios[{i}].current_investment",0)
        flows=row["future_incremental_contributions"]; avoided=row["avoided_costs"]
        if not isinstance(flows,list) or not isinstance(avoided,list): raise ModelError(f"scenarios[{i}]:cashflows_list_required")
        if len(flows)!=len(avoided) or not flows: raise ModelError(f"scenarios[{i}]:aligned_nonempty_periods_required")
        discounted_flows=[finite(x,f"scenarios[{i}].flow",) / ((1+rate)**(t+1)) for t,x in enumerate(flows)]
        discounted_avoided=[finite(x,f"scenarios[{i}].avoided",0) / ((1+rate)**(t+1)) for t,x in enumerate(avoided)]
        pv=sum(discounted_flows)
        pv_avoided=sum(discounted_avoided)
        risk=finite(row["risk_loss"],f"scenarios[{i}].risk_loss",0)
        max_loss=finite(row["approved_max_loss"],f"scenarios[{i}].approved_max_loss",0)
        value=pv+pv_avoided-current-risk
        scenario_id=text(row["id"],f"scenarios[{i}].id"); ids.append(scenario_id)
        cumulative=-current-risk
        payback=None
        for period,flow in enumerate((a+b for a,b in zip(discounted_flows,discounted_avoided)),start=1):
            cumulative+=flow
            if cumulative>=0 and payback is None: payback=period
        downside_factor=finite(row.get("downside_contribution_factor",1),f"scenarios[{i}].downside_contribution_factor",0,1)
        downside_value=sum(x*downside_factor for x in discounted_flows)+pv_avoided-current-risk
        out.append({"id":scenario_id,"brand_investment_value":value,
                    "downside_value":downside_value,"discounted_payback_period":payback,
                    "within_loss_boundary":current+risk<=max_loss,"positive_value":value>0,
                    "passes_downside":downside_value>0})
    if len(ids)!=len(set(ids)): raise ModelError("scenarios:duplicate_id")
    return {"currency":text(d["currency"],"currency"),"discount_rate":rate,"scenarios":out,
            "preferred_ids":[x["id"] for x in out if x["positive_value"] and x["within_loss_boundary"] and x["passes_downside"]]}
if __name__=="__main__": run_cli(calculate,"brand_investment_scenarios")
