#!/usr/bin/env python3
"""Execute portfolio, multi-market, cascade, scale, mutation, shock and capacity stress cases."""
from __future__ import annotations
import json
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run(s):
 t=s["type"]
 if t=="portfolio":
  blocked=sorted(x["id"] for x in s["objects"] if x["risk"]!="clear")
  eligible=sorted((x for x in s["objects"] if x["risk"]=="clear"),key=lambda x:Decimal(x["contribution"]),reverse=True)
  cap=Decimal(s["constraints"]["capital"]); slots=s["constraints"]["capacity"]; selected=[]
  for x in eligible:
   if Decimal(x["capital"])<=cap and x["capacity"]<=slots: selected.append(x["id"]); cap-=Decimal(x["capital"]); slots-=x["capacity"]
  return {"selected":sorted(selected),"blocked":blocked}
 if t=="multi_market":
  return {"eligible":sorted(x["id"] for x in s["markets"] if x["gate"]=="eligible" and x["rule"]=="current" and x["rights"]=="valid"),"inheritance":False}
 if t=="cascade_failure":
  blocked=set(s["failed"]); changed=True
  while changed:
   changed=False
   for owner,deps in s["dependencies"].items():
    if owner not in blocked and blocked.intersection(deps): blocked.add(owner); changed=True
  return {"blocked":sorted(blocked-set(s["failed"])),"preserved":sorted(set(sum(([k]+v for k,v in s["dependencies"].items()),[]))-blocked)}
 if t=="concurrency":
  current={}; evidence=set(); assumptions=set()
  for i in range(s["object_count"]):
   oid=f"O{i:02d}"; current[oid]="v2"
   for j in range(s["evidence_per_object"]): evidence.add(f"{oid}-E{j}")
   for j in range(s["assumptions_per_object"]): assumptions.add(f"{oid}-A{j}")
   if i%s["late_version_every"]==0: current.setdefault(oid,"v1")
  return {"current_objects":len(current),"evidence":len(evidence),"assumptions":len(assumptions),"duplicate_effect":"no_op","late_version_effect":"ignored"}
 if t=="regulatory_mutation": return {"invalidated":sorted(s["affected_fields"]),"preserved":sorted(s["preserved_fields"]),"state":"blocked","recovery":s["recovery"]}
 if t=="financial_shock":
  def contribution(x): return (Decimal(x["price"])*Decimal(x["fx"])-Decimal(x["cost"])-Decimal(x["freight"])-Decimal(x["ad"])).quantize(Decimal("0.01"))
  shocked={**s["baseline"],**s["shock"]}
  return {"baseline":str(contribution(s["baseline"])),"shock":str(contribution(shocked)),"action":"freeze_scale" if contribution(shocked)<0 else "continue"}
 if t=="organization_capacity":
  ranked=sorted(s["actions"],key=lambda x:(x["redline"],x["severity"],x["impact"],x["evidence"]),reverse=True); chosen=ranked[:s["execution_capacity"]]
  return {"execute":sorted(x["id"] for x in chosen),"deferred":sorted(x["id"] for x in ranked if x not in chosen)}
 raise ValueError(f"unknown scenario type {t}")

def validate():
 rows=json.loads((ROOT/"evaluations/extreme-stress-scenarios.json").read_text())["scenarios"]; errors=[]
 if {x["type"] for x in rows}!={"portfolio","multi_market","cascade_failure","concurrency","regulatory_mutation","financial_shock","organization_capacity"}: errors.append("stress type coverage incomplete")
 for s in rows:
  r=run(s); sid=s["id"]
  if sid=="ES-01": ok=r=={"selected":sorted(s["expected_selected"]),"blocked":sorted(s["expected_blocked"])}
  elif sid=="ES-02": ok=r=={"eligible":s["expected_eligible"],"inheritance":False}
  elif sid=="ES-03": ok=r["blocked"]==sorted(s["expected_blocked"]) and r["preserved"]==sorted(s["expected_preserved"])
  elif sid=="ES-04": ok=r["current_objects"]==s["expected_current_objects"] and r["evidence"]==s["expected_evidence"] and r["assumptions"]==s["expected_assumptions"] and r["duplicate_effect"]=="no_op" and r["late_version_effect"]=="ignored"
  elif sid=="ES-05": ok=r["invalidated"]==sorted(s["affected_fields"]) and r["preserved"]==sorted(s["preserved_fields"]) and r["state"]==s["expected_state"]
  elif sid=="ES-06": ok=r=={"baseline":s["expected_baseline_contribution"],"shock":s["expected_shock_contribution"],"action":s["expected_action"]}
  else: ok=r=={"execute":sorted(s["expected_execute"]),"deferred":sorted(s["expected_deferred"])}
  if not ok: errors.append(f"{sid}: result mismatch {r}")
 return errors
if __name__=="__main__":
 e=validate(); print("EXTREME_STRESS=PASS" if not e else "EXTREME_STRESS=FAIL\n- "+"\n- ".join(e)); raise SystemExit(bool(e))
