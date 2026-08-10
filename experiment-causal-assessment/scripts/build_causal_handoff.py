#!/usr/bin/env python3
"""Build a claim-bounded, expiring ECAE handoff for D01-D14 or F02."""

from __future__ import annotations

import re

from ecae_common import ECAEError, cli_main, content_hash, parse_time


CONSUMER_PATTERN=re.compile(r"^(D(0[1-9]|1[0-4])|F02)$")


def build_causal_handoff(value:dict)->dict:
    result=value.get("causal_result")
    if not isinstance(result,dict): raise ECAEError("MISSING_CAUSAL_RESULT","causal_result is required")
    consumer=value.get("consumer")
    if not isinstance(consumer,str) or not CONSUMER_PATTERN.fullmatch(consumer):
        raise ECAEError("INVALID_CONSUMER","consumer must be D01-D14 or F02")
    if result.get("status") in {"invalidated","superseded","stale","data_failed"}:
        raise ECAEError("RESULT_NOT_CONSUMABLE","Invalidated, superseded, stale or failed results cannot be handed off")
    grade=result.get("causal_evidence_grade")
    if grade not in {"CE0","CE1","CE2","CE3","CE4","CE5"}: raise ECAEError("INVALID_GRADE","Result lacks a valid CE grade")
    required_value=["created_at","expires_at","applicability","invalidation_triggers","recompute_triggers"]
    missing=[field for field in required_value if field not in value or value[field] in (None,"",[],{})]
    if missing: raise ECAEError("HANDOFF_CONTRACT_INCOMPLETE","Handoff fields are incomplete",missing)
    if parse_time(value["expires_at"],"expires_at")<=parse_time(value["created_at"],"created_at"):
        raise ECAEError("INVALID_EXPIRY","expires_at must follow created_at")
    if grade=="CE5" and result.get("review_status")!="independent_accepted":
        raise ECAEError("CE5_REVIEW_REQUIRED","CE5 handoff requires independent_accepted review")
    object_id=value.get("object_id",f"ECAE-HANDOFF-{result.get('object_id','UNBOUND')}-{consumer}")
    handoff={
        "schema_version":"1.0.0","object_id":object_id,"object_version":value.get("object_version","1.0.0"),"status":"handed_off","as_of_time":value["created_at"],"owner":value.get("owner","ECAE"),"created_at":value["created_at"],"updated_at":value["created_at"],
        "source_refs":value.get("source_refs",[result.get("object_id","UNBOUND")]),"lineage_refs":value.get("lineage_refs",[result.get("reproducibility_bundle_ref","UNBOUND")]),"jurisdiction_refs":value.get("jurisdiction_refs",[]),"parameter_refs":value.get("parameter_refs",[]),"assumption_refs":value.get("assumption_refs",[]),"limitations":result.get("limitations",[]),
        "producer":"ECAE","consumer":consumer,"causal_result_ref":result.get("object_id","UNBOUND"),"estimand_ref":result.get("estimand_ref","UNBOUND"),"causal_evidence_grade":grade,"claim_ceiling":result.get("claim_ceiling",grade),
        "allowed_actions":value.get("allowed_actions",["consider_within_consumer_decision_contract"]),"prohibited_actions":sorted(set(value.get("prohibited_actions",[])+["upgrade_causal_grade","remove_scope_limitations","automatic_external_write","treat_as_final_business_decision"])),
        "allowed_wording":result.get("allowed_wording",[]),"prohibited_wording":result.get("prohibited_wording",[]),"applicability":value["applicability"],"invalidation_triggers":value["invalidation_triggers"],"recompute_triggers":value["recompute_triggers"],"expires_at":value["expires_at"],
        "reproducibility_bundle_ref":result.get("reproducibility_bundle_ref","UNBOUND"),"review_status":result.get("review_status","unreviewed"),"business_owner_decision_required":True,"external_write":False,"content_hash":"PENDING"
    }
    handoff["content_hash"]=content_hash(handoff)
    return handoff


if __name__=="__main__":
    cli_main(build_causal_handoff,__doc__ or "Build causal handoff")
