#!/usr/bin/env python3
"""Maximum committed loss and one-way sensitivity/flip points."""
from mbcm_common import finite, require, run_cli, ModelError, sequence, text

def calculate(d):
    require(d,"base_value","nonrecoverable_spend","nonrecoverable_offer_cost","unavoidable_fulfillment",
            "contract_exit_cost","incident_reserve","variables","currency")
    maximum_loss=sum(finite(d[k],k,0) for k in ("nonrecoverable_spend","nonrecoverable_offer_cost",
        "unavoidable_fulfillment","contract_exit_cost","incident_reserve"))
    base=finite(d["base_value"],"base_value")
    rows=[]; ids=[]
    for i,row in enumerate(sequence(d["variables"],"variables",allow_empty=False)):
        require(row,"id","low_impact","high_impact")
        low=base+finite(row["low_impact"],f"variables[{i}].low_impact")
        high=base+finite(row["high_impact"],f"variables[{i}].high_impact")
        variable_id=text(row["id"],f"variables[{i}].id"); ids.append(variable_id)
        rows.append({"id":variable_id,"low_value":low,"high_value":high,
                     "crosses_zero":min(low,high)<=0<=max(low,high),"range":abs(high-low),
                     "zero_flip_impact":-base})
    if len(ids)!=len(set(ids)): raise ModelError("variables:duplicate_id")
    rows.sort(key=lambda x:x["range"],reverse=True)
    return {"currency":text(d["currency"],"currency"),"base_value":base,"maximum_committed_loss":maximum_loss,
            "sensitivities":rows,"most_sensitive":rows[0]["id"] if rows else None}
if __name__=="__main__": run_cli(calculate,"risk_and_sensitivity")
