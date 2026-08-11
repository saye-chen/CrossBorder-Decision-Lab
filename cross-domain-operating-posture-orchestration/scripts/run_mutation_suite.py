#!/usr/bin/env python3
"""Execute the blueprint's 16 adversarial assertions against COPO."""
from __future__ import annotations
import json
from pathlib import Path
from copo import *  # noqa: F403

ROOT=Path(__file__).resolve().parents[1];H="a"*64
def rec(owner="D06",decision="accepted"):
    authority=DOMAIN_BY_ID[owner]["owned_decision_types"][0] if owner in DOMAIN_BY_ID else {"F01":"causal_qualification","F02":"localization_comparability","ERDG":"governance_validation"}[owner]  # noqa: F405
    governance=governance_metadata(owner,decision,"2026-08-11T00:00:00Z",f"R-{owner}");governance["content_hash"]=H  # noqa: F405
    r={"receipt_id":f"R-{owner}","request_ref":"Q","cycle_id":"C1","scope_ref":"S1","owner":owner,"owner_authority":authority,"decision":decision,"packet_version":1,"expires_at":"2027-01-01T00:00:00Z","accepted_fields":[f"A-{owner}"],"allowed_uses":["operating_posture_synthesis","approved_action_sequencing"],"governance":governance,"external_write":False};r["packet_hash"]=canonical_hash(receipt_signed_payload(r));governance["content_hash"]=r["packet_hash"];return r
def raised(fn)->bool:
    try:fn()
    except CopoError:return True  # noqa: F405
    return False
def kill(mid:str)->bool:
    route=route_scenario("scale_readiness","S1")  # noqa: F405
    receipts=[rec(x) for x in route["required_owners"]];gates={x:"passed" for x in route["gates"]}
    if mid=="d14_professional_final":return raised(lambda:validate_graph({"nodes":[{"node_id":"N","node_type":"domain_finding","owner":"D14","state":"domain_supported","evidence_refs":[]}],"edges":[]}))
    if mid=="d14_capital_approval":return authority_owner("investment")=="D01"  # noqa: F405
    versions={x:1 for x in route["required_owners"]+route["conditional_owners"]}
    kwargs={"cycle_id":"C1","now":"2026-08-11T00:00:00Z","trusted_ledger":TRUSTED_LEDGER}
    if mid=="remove_noncompensable_gate":gates.pop(route["gates"][0]);return posture_qualification(route,receipts,gates,"comparable","scale",**kwargs)["status"]=="blocked"  # noqa: F405
    if mid=="partial_failure_overall_pass":return validate_receipt(rec(decision="partially_accepted"),{"cycle_id":"C1","scope_ref":"S1","owner":"D06","packet_version":1},"2026-01-01T00:00:00Z")!="accepted"  # noqa: F405
    if mid=="missing_owner_approved":return posture_qualification(route,receipts[:-1],gates,"comparable","scale",**kwargs)["status"]!="owner_approval_pending"  # noqa: F405
    if mid=="ce1_ce3_to_causal":return raised(lambda:validate_graph({"nodes":[{"node_id":"N","node_type":"causal_claim","owner":"D06","state":"causally_qualified","evidence_refs":[]}],"edges":[]}))
    if mid=="f02_not_comparable_aggregated":return posture_qualification(route,receipts,gates,"not_comparable","scale",**kwargs)["status"]=="blocked"  # noqa: F405
    if mid=="expired_current":x=rec();x["expires_at"]="2025-01-01T00:00:00Z";return raised(lambda:validate_receipt(x,{"cycle_id":"C1","scope_ref":"S1","owner":"D06","packet_version":1},"2026-01-01T00:00:00Z"))
    if mid=="old_overwrites_new":return raised(lambda:validate_receipt(rec(),{"cycle_id":"C1","scope_ref":"S1","owner":"D06","packet_version":2},"2026-01-01T00:00:00Z"))
    if mid=="conflict_majority_vote":return conflict_owner("capital")=="D01"  # noqa: F405
    if mid in {"posture_approves_action","plan_invents_action"}:return raised(lambda:build_coordination_plan(route,[rec()],[{"owner":"D09","scope_ref":"S1","action_ref":"A-D09","approval_ref":"R-D06"}],**kwargs))
    if mid=="view_recomputes_gate":return all(json.loads(p.read_text()).get("computes")==[] for p in (ROOT/"view-models").glob("*.json"))
    if mid=="external_write_true":x=rec();x["external_write"]=True;return raised(lambda:validate_receipt(x,{"cycle_id":"C1","scope_ref":"S1","owner":"D06","packet_version":1},"2026-01-01T00:00:00Z"))
    if mid=="manual_completion":return raised(lambda:validate_computed_status("approved","blocked"))  # noqa: F405
    if mid=="same_source_independence":return raised(lambda:validate_independent_evidence([{"source_group":"one"},{"source_group":"one"}]))  # noqa: F405
    return False
def run()->dict[str,bool]:
    ids=[x["id"] for x in json.loads((ROOT/"evaluations/mutations/contract.json").read_text())["mutations"]]
    return {mid:kill(mid) for mid in ids}
if __name__=="__main__":
    result=run();failed=[k for k,v in result.items() if not v];print(json.dumps(result,sort_keys=True));print("COPO_ADVERSARIAL_ASSERTIONS=PASS" if not failed else "COPO_ADVERSARIAL_ASSERTIONS=FAIL:"+",".join(failed));raise SystemExit(0 if not failed else 2)
