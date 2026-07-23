#!/usr/bin/env python3
"""Validate MBCM incident identity, severity, containment and ownership."""
from mbcm_common import require, run_cli, ModelError, sequence, text

INCIDENT_TYPES={f"I{i:02d}" for i in range(1,11)}
SEVERITIES={f"S{i}" for i in range(5)}

def validate(d):
    require(d,"incident_id","incident_type","severity","objects","confirmed_facts",
            "unknowns","containment","owner","next_checkpoint")
    incident_id=text(d["incident_id"],"incident_id")
    if d["incident_type"] not in INCIDENT_TYPES: raise ModelError("incident_type:invalid")
    if d["severity"] not in SEVERITIES: raise ModelError("severity:invalid")
    objects=sequence(d["objects"],"objects",allow_empty=False)
    if any(not isinstance(x,dict) or not x.get("object_id") or not x.get("object_version") for x in objects):
        raise ModelError("objects:id_and_version_required")
    facts=sequence(d["confirmed_facts"],"confirmed_facts")
    unknowns=sequence(d["unknowns"],"unknowns")
    containment=sequence(d["containment"],"containment",allow_empty=False)
    owner=text(d["owner"],"owner")
    checkpoint=text(d["next_checkpoint"],"next_checkpoint")
    return {"valid":True,"incident_id":incident_id,"severity":d["severity"],
            "object_count":len(objects),"confirmed_fact_count":len(facts),
            "unknown_count":len(unknowns),"containment_count":len(containment),
            "owner":owner,"next_checkpoint":checkpoint}

if __name__=="__main__": run_cli(validate,"validate_incident")
