#!/usr/bin/env python3
"""End-to-end MBCM DQ, Gate, sovereignty and action ceiling evaluator."""
from mbcm_common import require, run_cli, ModelError, text, sequence
GATES={f"G{i}" for i in range(9)}
STATUSES={"passed","failed","unknown","not_applicable"}
OWNER_FORBIDDEN={"capital_entry":"CIDM","final_price":"D06","replenishment":"LIFD",
 "listing_edit":"PLCO","ad_bid":"AAMO","creator_contract":"CAPM","creative_script":"VLB",
 "customer_contact":"CIG","cross_domain_posture":"D14","legal_conclusion":"D05"}

def evaluate(d):
    require(d,"dq_level","claim_level","gates","requested_action","requested_owner","reversibility")
    dq=d["dq_level"]; claim=d["claim_level"]
    if dq not in {"DQ0","DQ1","DQ2","DQ3"} or claim not in {"C0","C1","C2","C3","C4"}:
        raise ModelError("dq_or_claim_level:invalid")
    gate_map={}
    for row in sequence(d["gates"],"gates",allow_empty=False):
        require(row,"gate","status","owner")
        if row["gate"] not in GATES or row["status"] not in STATUSES: raise ModelError("gate:invalid")
        if row["gate"] in gate_map: raise ModelError("gates:duplicate_gate")
        text(row["owner"],f"{row['gate']}.owner")
        gate_map[row["gate"]]=row
    if set(gate_map)!=GATES: raise ModelError("gates:G0_to_G8_required")
    failed=[g for g,r in gate_map.items() if r["status"]=="failed"]
    unknown=[g for g,r in gate_map.items() if r["status"]=="unknown"]
    action=text(d["requested_action"],"requested_action")
    owner=text(d["requested_owner"],"requested_owner")
    if d["reversibility"] not in {"reversible","partially_reversible","irreversible"}:
        raise ModelError("reversibility:invalid")
    sovereignty_violation=action in OWNER_FORBIDDEN and owner=="MBCM"
    if sovereignty_violation: state="escalate"
    elif failed: state="stop" if any(x in failed for x in ("G1","G2","G3","G4","G7")) else "hold"
    elif unknown: state="hold"
    elif dq in {"DQ0","DQ1"} or claim in {"C0","C1"}: state="inconclusive"
    elif dq=="DQ2" or claim=="C2":
        state="test" if d["reversibility"]=="reversible" else "hold"
    else: state="proceed"
    scale_allowed=state=="proceed" and dq=="DQ3" and claim in {"C3","C4"}
    return {"decision_state":state,"failed_gates":failed,"unknown_gates":unknown,
            "sovereignty_violation":sovereignty_violation,
            "required_owner":OWNER_FORBIDDEN.get(action,"MBCM"),
            "scale_allowed":scale_allowed,"production_ready":False}
if __name__=="__main__": run_cli(evaluate,"evaluate_marketing_decision")
