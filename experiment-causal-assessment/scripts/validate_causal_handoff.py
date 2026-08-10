#!/usr/bin/env python3
"""Consumer-side validation for freshness, scope, hash and grade of an ECAE handoff."""

from __future__ import annotations

from ecae_common import ECAEError, cli_main, content_hash, parse_time
from validate_schema import validate_object


def validate_causal_handoff(value:dict)->dict:
    handoff=value.get("handoff")
    if not isinstance(handoff,dict): raise ECAEError("MISSING_HANDOFF","handoff is required")
    validate_object(handoff,"causal-handoff.schema.json")
    expected_consumer=value.get("consumer")
    if handoff.get("consumer")!=expected_consumer:
        raise ECAEError("CONSUMER_MISMATCH","Handoff is bound to a different consumer",{"expected":expected_consumer,"actual":handoff.get("consumer")})
    as_of=parse_time(value.get("as_of_time"),"as_of_time")
    if parse_time(handoff["expires_at"],"expires_at")<=as_of:
        raise ECAEError("HANDOFF_EXPIRED","Expired handoff cannot be consumed",{"expires_at":handoff["expires_at"]})
    if handoff.get("status") not in {"handed_off","replayed","current"}:
        raise ECAEError("HANDOFF_NOT_CURRENT","Handoff status is not consumable",{"status":handoff.get("status")})
    if handoff.get("external_write") is not False or handoff.get("business_owner_decision_required") is not True:
        raise ECAEError("SOVEREIGNTY_VIOLATION","Handoff cannot authorize external write or replace business owner")
    if handoff.get("causal_evidence_grade")=="CE5" and handoff.get("review_status")!="independent_accepted":
        raise ECAEError("CE5_REVIEW_REQUIRED","CE5 handoff lacks independent review")
    return {"consumable":True,"consumer":expected_consumer,"causal_evidence_grade":handoff["causal_evidence_grade"],"claim_ceiling":handoff["claim_ceiling"],"expires_at":handoff["expires_at"],"invalidation_triggers":handoff["invalidation_triggers"],"recompute_triggers":handoff["recompute_triggers"],"business_owner_decision_required":True,"external_write":False}


if __name__=="__main__":
    cli_main(validate_causal_handoff,__doc__ or "Validate causal handoff")
