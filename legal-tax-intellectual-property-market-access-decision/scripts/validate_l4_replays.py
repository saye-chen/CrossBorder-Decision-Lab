#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
import jsonschema
R=Path(__file__).resolve().parents[1]
def validate(x):
 errors=[]; cases=x.get("cases",[])
 if x.get("production_ready") is not False and len(cases)<3: errors.append("production cannot precede three replays")
 if len(cases)<x.get("minimum_authorized_cases",3): errors.append("minimum authorized replay count not met")
 ids=[]
 for i,c in enumerate(cases):
  try: jsonschema.validate(c,json.loads((R/"schemas/authorized-replay.schema.json").read_text()),format_checker=jsonschema.FormatChecker())
  except jsonschema.ValidationError as e: errors.append(f"case {i}: {e.message}"); continue
  ids.append(c["case_id"])
  if c["review_decision"]!="approved": errors.append(f"{c['case_id']}: independent review not approved")
 if len(ids)!=len(set(ids)): errors.append("duplicate replay case id")
 if cases and len({(tuple(c.get("jurisdictions",[])),tuple(c.get("topics",[]))) for c in cases})<2: errors.append("replays lack jurisdiction or topic breadth")
 return errors
if __name__=="__main__":
 x=json.loads(Path(sys.argv[1] if len(sys.argv)>1 else R/"evaluations/historical-replay-template.json").read_text()); e=validate(x); print("L4_REPLAYS=PASS" if not e else "L4_REPLAYS=BLOCKED\n- "+"\n- ".join(e)); raise SystemExit(bool(e))
