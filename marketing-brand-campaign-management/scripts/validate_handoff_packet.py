#!/usr/bin/env python3
"""Validate cross-domain packet, uses, status and lineage."""
from mbcm_common import require, text, run_cli, ModelError, sequence
STATES={"validated","proposed","blocked","inconclusive","stale","conflicted","withdrawn","superseded"}
def validate(d):
    require(d,"packet_id","packet_version","source_domain","source_runtime","target_domain","object",
            "status","evidence","calculations","allowed_uses","forbidden_uses","lineage")
    if d["status"] not in STATES: raise ModelError("status:invalid")
    for x in ("packet_id","packet_version","source_domain","source_runtime","target_domain"): text(d[x],x)
    allowed=sequence(d["allowed_uses"],"allowed_uses")
    forbidden=sequence(d["forbidden_uses"],"forbidden_uses",allow_empty=False)
    if not isinstance(d["object"],dict) or not d["object"].get("object_id"):
        raise ModelError("object:object_id_required")
    if not isinstance(d["lineage"],dict) or not d["lineage"].get("decision_id"):
        raise ModelError("lineage:decision_id_required")
    overlap=set(allowed)&set(forbidden)
    if overlap: raise ModelError("uses:allowed_forbidden_overlap")
    return {"valid":True,"packet_id":d["packet_id"],"status":d["status"],
            "actionable":d["status"]=="validated" and bool(allowed)}
if __name__=="__main__": run_cli(validate,"validate_handoff_packet")
