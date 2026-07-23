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
        pv=sum(finite(x,f"scenarios[{i}].flow",) / ((1+rate)**(t+1)) for t,x in enumerate(flows))
        pv_avoided=sum(finite(x,f"scenarios[{i}].avoided",0) / ((1+rate)**(t+1)) for t,x in enumerate(avoided))
        risk=finite(row["risk_loss"],f"scenarios[{i}].risk_loss",0)
        max_loss=finite(row["approved_max_loss"],f"scenarios[{i}].approved_max_loss",0)
        value=pv+pv_avoided-current-risk
        scenario_id=text(row["id"],f"scenarios[{i}].id"); ids.append(scenario_id)
        out.append({"id":scenario_id,"brand_investment_value":value,
                    "within_loss_boundary":current+risk<=max_loss,"positive_value":value>0})
    if len(ids)!=len(set(ids)): raise ModelError("scenarios:duplicate_id")
    return {"currency":text(d["currency"],"currency"),"discount_rate":rate,"scenarios":out,
            "preferred_ids":[x["id"] for x in out if x["positive_value"] and x["within_loss_boundary"]]}
if __name__=="__main__": run_cli(calculate,"brand_investment_scenarios")
