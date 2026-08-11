#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from lcca_common import LCCAError,parse_time,canonical_hash,require_false
def evaluate(p):
    require_false(p); source=p.get("source",{})
    if not source.get("source_id") or not source.get("content_fingerprint"): raise LCCAError("SOURCE_UNQUALIFIED","qualified source and fingerprint required")
    decision=parse_time(p.get("decision_time"),"decision_time"); start=parse_time(p.get("valid_from"),"valid_from"); end=parse_time(p.get("valid_until"),"valid_until")
    if not start<=decision<=end: return {"status":"expired","error_code":"DYNAMIC_FACT_EXPIRED","fact_id":p.get("object_id"),"external_write":False}
    recorded=parse_time(p.get("recorded_at"),"recorded_at")
    if recorded>decision and not p.get("historical_restatement",False): raise LCCAError("VALID_RECORD_TIME_INCONSISTENT","fact was not known at decision time")
    if p.get("conflict_refs"): return {"status":"conflicted","error_code":"OWNER_CONFLICT_UNRESOLVED","fact_id":p.get("object_id"),"external_write":False}
    return {"status":"qualified","fact_id":p.get("object_id"),"fact_hash":canonical_hash(p),"external_write":False}
def main():
    q=argparse.ArgumentParser();q.add_argument("input",type=Path);a=q.parse_args()
    try: print(json.dumps(evaluate(json.loads(a.input.read_text())),sort_keys=True));return 0
    except (OSError,json.JSONDecodeError,LCCAError) as e: print(f"{getattr(e,'code','INVALID')}: {e}",file=sys.stderr);return 2
if __name__=="__main__": raise SystemExit(main())
