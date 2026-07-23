#!/usr/bin/env python3
"""Validate claim-evidence ledger and evidence-to-action ceilings."""
from mbcm_common import require, run_cli, ModelError, sequence, text
LEVELS={"C0","C1","C2","C3","C4"}
def validate(d):
    require(d,"evidence","claims")
    evidence=sequence(d["evidence"],"evidence",allow_empty=False)
    ids={x.get("evidence_id") for x in evidence}
    if None in ids or len(ids)!=len(evidence): raise ModelError("evidence:unique_ids_required")
    claims=sequence(d["claims"],"claims",allow_empty=False); claim_ids=[]
    for i,c in enumerate(claims):
        require(c,"claim_id","claim_level","supporting_evidence","contrary_evidence","alternative_explanations",
                "scope","allowed_action","falsifier","refresh_trigger")
        if c["claim_level"] not in LEVELS: raise ModelError(f"claims[{i}]:invalid_level")
        claim_ids.append(text(c["claim_id"],f"claims[{i}].claim_id"))
        supporting=sequence(c["supporting_evidence"],f"claims[{i}].supporting_evidence")
        contrary=sequence(c["contrary_evidence"],f"claims[{i}].contrary_evidence")
        if not set(supporting+contrary).issubset(ids): raise ModelError(f"claims[{i}]:unknown_evidence")
        if c["claim_level"] in {"C3","C4"} and not supporting:
            raise ModelError(f"claims[{i}]:strong_claim_without_evidence")
        if c["claim_level"] in {"C0","C1"} and c["allowed_action"]=="scale": raise ModelError(f"claims[{i}]:action_exceeds_evidence")
    if len(claim_ids)!=len(set(claim_ids)): raise ModelError("claims:duplicate_claim_id")
    return {"valid":True,"evidence_count":len(ids),"claim_count":len(claims)}
if __name__=="__main__": run_cli(validate,"validate_evidence_claims")
