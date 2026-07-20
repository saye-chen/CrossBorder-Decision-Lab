#!/usr/bin/env python3
"""Compose CIM identity, baseline, anomaly, attribution and window gates."""
from __future__ import annotations
import argparse,json,math
from datetime import datetime
from pathlib import Path

def number(v,name):
 try:x=float(v)
 except (TypeError,ValueError) as e:raise ValueError(f"{name} must be numeric") from e
 if not math.isfinite(x):raise ValueError(f"{name} must be finite")
 return x

def evaluate(d):
 errors=[];object_id=d.get("object_id");snapshots=d.get("snapshots",[])
 if not object_id:errors.append("missing_object_id")
 if len(snapshots)<3:errors.append("trend_requires_three_snapshots")
 times=[]
 for i,s in enumerate(snapshots):
  if s.get("object_id")!=object_id:errors.append(f"mixed_object:{i}")
  try:times.append(datetime.fromisoformat(str(s.get("observed_at")).replace("Z","+00:00")))
  except ValueError:errors.append(f"invalid_time:{i}")
  if not s.get("display_condition"):errors.append(f"missing_display_condition:{i}")
 if times!=sorted(times):errors.append("snapshots_not_sorted")
 signals=d.get("signals",[]);confirmed=[];proxies=[]
 for i,s in enumerate(signals):
  value=number(s.get("value"),f"signal.{i}.value")
  baseline=number(s.get("baseline"),f"signal.{i}.baseline")
  threshold=number(s.get("threshold"),f"signal.{i}.threshold")
  changed=abs(value-baseline)>=threshold
  if changed and s.get("consecutive_confirmations",0)>=2:confirmed.append(s.get("id"))
  if s.get("evidence_type") in {"public_proxy","estimate","inference"}:proxies.append(s.get("id"))
 hypotheses=[]
 for h in d.get("hypotheses",[]):
  support=set(h.get("supporting_signal_ids",[]));counter=set(h.get("counter_signal_ids",[]))
  independent=len(set(h.get("independent_source_fingerprints",[])))
  confidence="high" if len(support)>=3 and independent>=3 and not counter else "medium" if len(support)>=2 and independent>=2 else "low"
  hypotheses.append({"id":h.get("id"),"confidence":confidence,"support":sorted(support),"counter":sorted(counter),"validation_due":h.get("validation_due")})
 window=d.get("opportunity_window",{});deploy=number(window.get("deployment_days",0),"deployment_days");remaining=number(window.get("conservative_remaining_days",0),"conservative_remaining_days")
 posture="Test" if confirmed and deploy<remaining and not errors else "Watch" if not errors else "Blocked"
 forbidden_claims=[]
 if proxies:forbidden_claims=["proxy signals cannot be stated as competitor sales, spend, inventory or market share"]
 return {"object_id":object_id,"confirmed_changes":confirmed,"proxy_signal_ids":proxies,"hypotheses":hypotheses,"posture":posture,"errors":errors,"forbidden_claims":forbidden_claims,"stop_conditions":["window closes","evidence refuted","deployment exceeds remaining window"]}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 try:r=evaluate(json.loads(a.input.read_text()))
 except (ValueError,OSError,json.JSONDecodeError) as e:p.error(str(e))
 a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__":main()
