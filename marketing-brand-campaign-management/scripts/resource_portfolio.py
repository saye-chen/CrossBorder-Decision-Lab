#!/usr/bin/env python3
"""Constrained resource portfolio, marginal ranking and concentration."""
from mbcm_common import finite, require, run_cli, ModelError, boolean, sequence, text

def calculate(d):
    require(d,"approved_envelope","candidates","currency")
    envelope=finite(d["approved_envelope"],"approved_envelope",0); candidates=[]; total=0
    rows=sequence(d["candidates"],"candidates",allow_empty=False)
    ids=[]
    for i,row in enumerate(rows):
        require(row,"id","allocation","minimum","maximum","marginal_incremental_value","gate_passed")
        allocation=finite(row["allocation"],f"candidates[{i}].allocation",0)
        low=finite(row["minimum"],f"candidates[{i}].minimum",0); high=finite(row["maximum"],f"candidates[{i}].maximum",0)
        if low>high or allocation<low or allocation>high: raise ModelError(f"candidates[{i}]:allocation_outside_bounds")
        total+=allocation
        candidate_id=text(row["id"],f"candidates[{i}].id"); ids.append(candidate_id)
        candidates.append({"id":candidate_id,"allocation":allocation,
            "marginal_incremental_value":finite(row["marginal_incremental_value"],f"candidates[{i}].marginal_incremental_value"),
            "gate_passed":boolean(row["gate_passed"],f"candidates[{i}].gate_passed")})
    if len(ids)!=len(set(ids)): raise ModelError("candidates:duplicate_id")
    if total>envelope+1e-9: raise ModelError("allocation:exceeds_approved_envelope")
    hhi=sum((x["allocation"]/total)**2 for x in candidates) if total else 0
    ranked=sorted(candidates,key=lambda x:(x["gate_passed"],x["marginal_incremental_value"]),reverse=True)
    return {"currency":text(d["currency"],"currency"),"approved_envelope":envelope,"allocated":total,
            "unallocated":envelope-total,"hhi":hhi,"marginal_ranking":[x["id"] for x in ranked],
            "negative_marginal_ids":[x["id"] for x in candidates if x["marginal_incremental_value"]<0],
            "scale_allowed_ids":[x["id"] for x in candidates if x["gate_passed"] and x["marginal_incremental_value"]>0]}
if __name__=="__main__": run_cli(calculate,"resource_portfolio")
