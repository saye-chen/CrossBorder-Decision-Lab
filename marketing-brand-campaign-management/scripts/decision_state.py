#!/usr/bin/env python3
"""Validate multi-turn inheritance and compute affected closure."""
from mbcm_common import require, sha, run_cli, ModelError, sequence, text
def update(d):
    require(d,"parent_state","parent_hash","object_id","object_version","changed_fields",
            "new_evidence_ids","dependency_map","preserved_constraints")
    parent=d["parent_state"]
    if sha(parent)!=d["parent_hash"]: raise ModelError("parent_hash:mismatch")
    if parent.get("object_id")!=d["object_id"]: raise ModelError("object_id:change_requires_new_ledger")
    text(d["object_version"],"object_version")
    changed_fields=sequence(d["changed_fields"],"changed_fields")
    new_evidence=sequence(d["new_evidence_ids"],"new_evidence_ids")
    preserved=sequence(d["preserved_constraints"],"preserved_constraints")
    parent_constraints=parent.get("constraints",[])
    if not isinstance(parent_constraints,list): raise ModelError("parent_state.constraints:list_required")
    if not set(parent_constraints).issubset(set(preserved)):
        raise ModelError("preserved_constraints:parent_constraint_lost")
    if not isinstance(d["dependency_map"],dict): raise ModelError("dependency_map:object_required")
    changed=set(changed_fields)|set(new_evidence)
    affected=set()
    progress=True
    while progress:
        progress=False
        for node,deps in d["dependency_map"].items():
            if not isinstance(deps,list): raise ModelError(f"dependency_map.{node}:list_required")
            if node in affected: continue
            if changed.intersection(deps) or affected.intersection(deps):
                affected.add(node); progress=True
    return {"parent_decision_id":parent.get("decision_id"),"object_id":d["object_id"],
            "object_version":d["object_version"],"affected_nodes":sorted(affected),
            "preserved_constraints":preserved,
            "next_state_hash":sha({"parent":d["parent_hash"],"version":d["object_version"],"affected":sorted(affected)})}
if __name__=="__main__": run_cli(update,"decision_state")
