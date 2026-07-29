#!/usr/bin/env python3
import json,pathlib,sys
import jsonschema
TYPES={"Addendum","Revision","Recalculation","Rebase","New Decision Object"}
ROOT=pathlib.Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/"schemas/continuous-state.schema.json").read_text())
def update(d):
    if d.get("delta_type") not in TYPES: raise ValueError("invalid_delta_type")
    state=d["state"]; changed=set(d.get("changed_fields",[]))
    jsonschema.Draft202012Validator(SCHEMA).validate(state)
    if d.get("object_id")!=state.get("object_id"):raise ValueError("object_id_mismatch")
    if d.get("expected_version")!=state.get("current_version"):raise ValueError("stale_or_concurrent_version")
    if d.get("new_version")==state.get("current_version"):raise ValueError("new_version_must_advance")
    impact=set(d.get("impact_map",{}).get(x,[]) for x in [])
    impacted=set()
    for field in changed: impacted.update(d.get("impact_map",{}).get(field,[]))
    previous=state.get("current_effective_decision")
    if previous: state.setdefault("history",[]).append({**previous,"status":"superseded"})
    state["current_version"]=d["new_version"]; state["current_effective_decision"]=d.get("new_decision")
    state["last_delta"]={"type":d["delta_type"],"changed":sorted(changed),"invalidated":sorted(impacted),"preserved":sorted(set(d.get("all_fields",[]))-changed-impacted)}
    state["invalidated_fields"]=sorted(set(state.get("invalidated_fields",[]))|impacted)
    state["recompute_scope"]=sorted(set(state.get("recompute_scope",[]))|impacted)
    irreversible={"committed","in_progress","irreversible","shipped"}
    affected_actions=[x for x in state.get("active_actions",[]) if x.get("status") in irreversible and (set(x.get("depends_on",[]))&changed)]
    if affected_actions:
        state["recovery_required"]=[{"action_id":x.get("action_id"),"status":x.get("status"),"reason":"changed_dependency_after_real_commitment","required":["contain_exposure","reconcile_sunk_and_recoverable_cost","owner_reapproval"]} for x in affected_actions]
        if "REALITY_RECOVERY" not in state.setdefault("open_gates",[]):state["open_gates"].append("REALITY_RECOVERY")
    jsonschema.Draft202012Validator(SCHEMA).validate(state)
    return state
def main():
    d=json.loads(pathlib.Path(sys.argv[1]).read_text())
    try:o=update(d)
    except (KeyError,ValueError) as e:raise SystemExit(f"SPPQ continuity BLOCKED:{e}")
    print(json.dumps(o,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
