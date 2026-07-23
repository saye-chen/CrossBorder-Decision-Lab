#!/usr/bin/env python3
"""Comparable continue, repair, clearance and exit recovery values."""
from mbcm_common import finite, require, run_cli, boolean, sequence, text, ModelError

def calculate(d):
    require(d,"options","currency")
    out=[]; ids=[]
    for i,row in enumerate(sequence(d["options"],"options",allow_empty=False)):
        require(row,"id","net_revenue","channel_cost","offer_cost","fulfillment_returns",
                "service_complaint","channel_conflict","brand_risk","residual_asset_value","residual_liabilities","redline")
        value=finite(row["net_revenue"],f"options[{i}].net_revenue")-sum(finite(row[k],f"options[{i}].{k}",0) for k in
            ("channel_cost","offer_cost","fulfillment_returns","service_complaint","channel_conflict","brand_risk","residual_liabilities"))+finite(row["residual_asset_value"],f"options[{i}].residual_asset_value",0)
        option_id=text(row["id"],f"options[{i}].id"); ids.append(option_id)
        out.append({"id":option_id,"net_recovery_value":value,
                    "redline":boolean(row["redline"],f"options[{i}].redline")})
    if len(ids)!=len(set(ids)): raise ModelError("options:duplicate_id")
    feasible=[x for x in out if not x["redline"]]
    preferred=max(feasible,key=lambda x:x["net_recovery_value"])["id"] if feasible else None
    return {"currency":text(d["currency"],"currency"),"options":out,"preferred_feasible_option":preferred,
            "no_feasible_option":not bool(feasible)}
if __name__=="__main__": run_cli(calculate,"clearance_exit_economics")
