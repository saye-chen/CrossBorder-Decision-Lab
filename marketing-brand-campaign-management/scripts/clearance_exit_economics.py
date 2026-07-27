#!/usr/bin/env python3
"""Comparable continue, repair, clearance and exit recovery values."""
from mbcm_common import finite, require, run_cli, boolean, sequence, text, ModelError

def calculate(d):
    require(d,"options","currency")
    out=[]; ids=[]
    for i,row in enumerate(sequence(d["options"],"options",allow_empty=False)):
        require(row,"id","net_revenue","channel_cost","offer_cost","fulfillment_returns",
                "service_complaint","channel_conflict","brand_risk","residual_asset_value","residual_liabilities","redline")
        costs={k:finite(row[k],f"options[{i}].{k}",0) for k in
            ("channel_cost","offer_cost","fulfillment_returns","service_complaint","channel_conflict","brand_risk","residual_liabilities")}
        revenue=finite(row["net_revenue"],f"options[{i}].net_revenue")
        residual=finite(row["residual_asset_value"],f"options[{i}].residual_asset_value",0)
        value=revenue-sum(costs.values())+residual
        recovery_factor=finite(row.get("downside_recovery_factor",1),f"options[{i}].downside_recovery_factor",0,1)
        liability_factor=finite(row.get("downside_liability_factor",1),f"options[{i}].downside_liability_factor",1)
        downside_value=revenue*recovery_factor-sum(v*(liability_factor if k=="residual_liabilities" else 1) for k,v in costs.items())+residual*recovery_factor
        option_id=text(row["id"],f"options[{i}].id"); ids.append(option_id)
        out.append({"id":option_id,"net_recovery_value":value,
                    "downside_net_recovery_value":downside_value,
                    "value_waterfall":{"net_revenue":revenue,"costs":costs,"residual_asset_value":residual},
                    "redline":boolean(row["redline"],f"options[{i}].redline"),
                    "irreversible_at":row.get("irreversible_at")})
    if len(ids)!=len(set(ids)): raise ModelError("options:duplicate_id")
    feasible=[x for x in out if not x["redline"]]
    preferred=max(feasible,key=lambda x:x["downside_net_recovery_value"])["id"] if feasible else None
    return {"currency":text(d["currency"],"currency"),"options":out,"preferred_feasible_option":preferred,
            "selection_basis":"maximum_downside_net_recovery_among_non_redline_options",
            "no_feasible_option":not bool(feasible)}
if __name__=="__main__": run_cli(calculate,"clearance_exit_economics")
