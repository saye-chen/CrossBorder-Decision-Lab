#!/usr/bin/env python3
from datetime import datetime,timezone
from common import main

IMPACT={
 "demand":["forecast","replenishment","allocation","capacity","exit"],
 "lead_time":["lead_time","replenishment","routing","promising"],
 "inventory":["ledger","replenishment","allocation","promising","exit"],
 "route_capacity":["routing","flow","replenishment","promising"],
 "warehouse_capacity":["capacity","replenishment","promising"],
 "cash_capacity":["routing","replenishment","exit"],
 "compliance":["routing","reverse_exit","traceability"],
 "title":["reverse_exit","traceability"],
 "cost":["routing","cost_to_serve","exit"],
 "return_rate":["forecast","capacity","reverse_exit","cost_to_serve"],
 "promotion":["forecast","replenishment","allocation","capacity"]
 ,"time_window":["forecast","lead_time","replenishment","routing","flow","allocation","capacity","promising","reverse_exit","cost_to_serve"]
}
TRANSITIONS={
 "proposed":{"validated","rejected","stopped","superseded"},
 "validated":{"executing","stopped","superseded"},
 "executing":{"completed","failed","stopped","superseded"},
 "completed":set(),"failed":set(),"stopped":set(),"superseded":set(),"rejected":set()
}

def impacted(fields): return sorted({m for f in fields for m in IMPACT.get(f,[])})

def parse_time(value):
    if value.endswith("Z"): value=value[:-1]+"+00:00"
    return datetime.fromisoformat(value)

def run(d):
    reports=d.get("reports",[]);errors=[];ids={}
    for r in reports:
        rid=r.get("report_id")
        if not rid or rid in ids: errors.append(f"duplicate_or_missing_report_id:{rid}")
        else: ids[rid]=r
    for r in reports:
        rid=r.get("report_id");parents=r.get("parent_ids",[])
        for parent in parents:
            if parent not in ids: errors.append(f"missing_parent:{rid}:{parent}")
            elif ids[parent].get("object_id")!=r.get("object_id"): errors.append(f"cross_object_parent:{rid}:{parent}")
        required=impacted(r.get("changed_fields",[]));declared=set(r.get("recalculated_modules",[]))
        missing=[x for x in required if x not in declared]
        if parents and missing: errors.append(f"missing_incremental_recompute:{rid}:{','.join(missing)}")
        if parents:
            parent_report=ids.get(parents[0],{});prior={a.get("action_id"):a for a in parent_report.get("actions",[])}
            current_actions={a.get("action_id") for a in r.get("actions",[])}
            transitions={x.get("action_id"):x for x in r.get("action_transitions",[])}
            for aid,old in prior.items():
                if old.get("status") in {"validated","executing"} and aid not in current_actions:
                    tr=transitions.get(aid,{})
                    if tr.get("to_status") not in {"stopped","failed","superseded","completed"}: errors.append(f"active_action_silently_dropped:{rid}:{aid}")
                    if old.get("status")=="executing" and tr.get("to_status") in {"stopped","failed","superseded"}:
                        for key in ["recovery_action","remaining_exposure","owner","due_at"]:
                            if not tr.get(key): errors.append(f"missing_action_recovery:{rid}:{aid}:{key}")
            parent_evidence={e.get("evidence_id") for e in parent_report.get("evidence",[]) if e.get("evidence_id")}
            current_evidence={e.get("evidence_id") for e in r.get("evidence",[]) if e.get("evidence_id")}
            evidence_transitions={e.get("evidence_id"):e for e in r.get("evidence_transitions",[])}
            for eid in parent_evidence-current_evidence:
                tr=evidence_transitions.get(eid,{})
                if tr.get("state") not in {"expired","revoked","superseded"} or not tr.get("reason"): errors.append(f"evidence_silently_dropped:{rid}:{eid}")
            for a in r.get("actions",[]):
                aid=a.get("action_id");old=prior.get(aid)
                if old and a.get("status")!=old.get("status"):
                    if a.get("status") not in TRANSITIONS.get(old.get("status"),set()): errors.append(f"illegal_action_transition:{rid}:{aid}:{old.get('status')}->{a.get('status')}")
                    if old.get("status")=="executing" and a.get("status") in {"failed","stopped","superseded"}:
                        for key in ["recovery_action","remaining_exposure","owner","due_at"]:
                            if not a.get(key): errors.append(f"missing_action_recovery:{rid}:{aid}:{key}")
                if a.get("owner_domain") and a.get("owner_domain")!="LIFD" and a.get("status") not in {"proposed","rejected"}: errors.append(f"cross_domain_self_approval:{rid}:{aid}")
    visiting=set();done=set()
    def visit(rid):
        if rid in visiting: errors.append(f"lineage_cycle:{rid}");return
        if rid in done or rid not in ids:return
        visiting.add(rid)
        for p in ids[rid].get("parent_ids",[]): visit(p)
        visiting.remove(rid);done.add(rid)
    for rid in ids: visit(rid)
    by_object={}
    for r in reports: by_object.setdefault(r.get("object_id"),[]).append(r)
    current={}
    for oid,rows in by_object.items():
        marked=[r for r in rows if r.get("is_current") is True]
        if len(marked)!=1: errors.append(f"current_count:{oid}:{len(marked)}")
        elif marked: current[oid]=marked[0]
    now=parse_time(d.get("as_of_time",datetime.now(timezone.utc).isoformat()))
    expired=[]
    for oid,r in current.items():
        for e in r.get("evidence",[]):
            if e.get("expires_at") and parse_time(e["expires_at"])<now: expired.append(f"{oid}:{e.get('evidence_id')}")
    active_actions=[]
    for oid,r in current.items():
        for a in r.get("actions",[]):
            if a.get("status") in ["proposed","validated","executing"]: active_actions.append({"object_id":oid,**a})
    if expired and active_actions: errors.append("expired_evidence_supports_active_action")
    return {"valid":not errors,"errors":sorted(set(errors)),"current_state":{k:v.get("report_id") for k,v in current.items()},"expired_evidence":expired,"active_actions":active_actions,"impact_map_version":"LIFD-impact-1.0"}

if __name__=="__main__": main(run)
