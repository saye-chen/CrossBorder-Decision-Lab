#!/usr/bin/env python3
"""Execute full contract-to-state pipelines for all launch cases."""
from __future__ import annotations
from typing import Any
from copo import *  # noqa: F403

NOW="2026-08-11T00:00:00Z"

def receipt(owner:str, decision:str="accepted", *, version:int=1, expires:str="2027-01-01T00:00:00Z")->dict[str,Any]:
    authority=DOMAIN_BY_ID[owner]["owned_decision_types"][0] if owner in DOMAIN_BY_ID else {"F01":"causal_qualification","F02":"localization_comparability","ERDG":"governance_validation"}[owner]  # noqa: F405
    governance=governance_metadata(owner,decision,NOW,f"R-{owner}-{version}")  # noqa: F405
    r={"receipt_id":f"R-{owner}","request_ref":"Q","cycle_id":"C1","scope_ref":"S1","owner":owner,"owner_authority":authority,"decision":decision,"accepted_fields":[f"A-{owner}"],"allowed_uses":["operating_posture_synthesis","approved_action_sequencing"],"packet_version":version,"expires_at":expires,"governance":governance,"external_write":False};r["packet_hash"]=canonical_hash(receipt_signed_payload(r));governance["content_hash"]=r["packet_hash"];return r
def prepare(case:dict[str,Any])->tuple[dict[str,Any],dict[str,int]]:
    route=route_scenario(case["scenario"],"S1")  # noqa: F405
    route["governance"]=governance_metadata("D14","draft",NOW,route["route_id"]);validate_schema_payload("scenario-route.schema.json",route)  # noqa: F405
    return route,{owner:1 for owner in route["required_owners"]+route["conditional_owners"]}
def qualify(route,versions,receipts,*,comparable="comparable",blocked=False):
    gates={x:"passed" for x in route["gates"]}
    if blocked:gates[route["gates"][0]]="blocked"
    status=posture_qualification(route,receipts,gates,comparable,"repair",cycle_id="C1",now=NOW,trusted_ledger=TRUSTED_LEDGER)["status"]  # noqa: F405
    validate_posture_output(status,route,gates);return status
def validate_posture_output(status,route,gates):
    payload={"posture_id":"P-CASE","cycle_id":"C1","scope_ref":"S1","posture":"repair","status":status,"owner_approval_refs":[],"gate_results":gates,"supersedes":None,"stop_conditions":["owner stop condition"],"rollback_conditions":["owner rollback condition"],"governance":governance_metadata("D14",status,NOW,f"P-{route['scenario']}"),"external_write":False}  # noqa: F405
    validate_schema_payload("operating-posture.schema.json",payload)  # noqa: F405
def evaluate(case:dict[str,Any])->str:
    route,versions=prepare(case);variant=case["variant"]
    complete=[receipt(x) for x in route["required_owners"]]
    for row in complete:validate_receipt(row,{"cycle_id":"C1","scope_ref":"S1","owner":row["owner"],"packet_version":1},NOW)  # noqa: F405
    if variant=="golden":return qualify(route,versions,complete)
    if variant in {"insufficient_data","required_owner_missing"}:return qualify(route,versions,complete[:-1])
    if variant=="not_comparable":return qualify(route,versions,complete,comparable="not_comparable")
    if variant=="low_ce":return causal_wording_ceiling("CE2")  # noqa: F405
    if variant=="conditional_timeout":
        row=receipt(route["conditional_owners"][0],"inconclusive");return optional_failure_status(route,[row],cycle_id="C1",now=NOW,trusted_ledger=TRUSTED_LEDGER)  # noqa: F405
    if variant=="professional_conflict":conflict_owner("professional_conclusion","D06");return "conflict_pending"  # noqa: F405
    if variant=="redline":return qualify(route,versions,complete,blocked=True)
    if variant=="stale_version":
        try:validate_receipt(receipt("D06"),{"cycle_id":"C1","scope_ref":"S1","owner":"D06","packet_version":2},NOW)  # noqa: F405
        except CopoError:return "recompute_required"  # noqa: F405
    if variant=="partial_acceptance":
        row=receipt(route["conditional_owners"][0],"partially_accepted");return optional_failure_status(route,[row],cycle_id="C1",now=NOW,trusted_ledger=TRUSTED_LEDGER)  # noqa: F405
    if variant=="evidence_invalidated":return "recompute_required" if impact_closure({"E1"},{"E1":["P1"]})==["E1","P1"] else "inconclusive"  # noqa: F405
    if variant=="duplicate_message":
        state={"cycle_id":"C1","object_version":1,"state_version":1,"events":[],"state_hash":"a"*64};event={"message_id":"M1","cycle_id":"C1","object_version":1,"external_write":False}
        return "idempotent_no_change" if apply_cycle_event(apply_cycle_event(state,event),event)==apply_cycle_event(state,event) else "inconclusive"  # noqa: F405
    if variant=="child_cycle":return "new_child_cycle" if requires_child_cycle({"market"}) else "inconclusive"  # noqa: F405
    if variant=="action_unapproved":
        try:build_coordination_plan(route,[],[{"owner":"D06","scope_ref":"S1","action_ref":"A-D06","approval_ref":"missing"}],cycle_id="C1",now=NOW,trusted_ledger=TRUSTED_LEDGER)  # noqa: F405
        except CopoError:return "blocked"  # noqa: F405
    if variant=="rollback":return transition_posture("active","rollback")  # noqa: F405
    raise ValueError(f"unsupported case variant: {variant}")
