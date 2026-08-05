#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("builder",ROOT/"scripts/build_domain_professional_evaluations.py");b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
qs=importlib.util.spec_from_file_location("quality",ROOT/"scripts/evaluate_report_quality.py");quality=importlib.util.module_from_spec(qs);qs.loader.exec_module(quality)
def validate(skill):
 e=[];p=b.P[skill];base=ROOT/skill/"evaluations";d=json.loads((base/"evaluation-catalog.json").read_text());cases=d.get("cases",[])
 if d.get("runtime")!=p["runtime"] or len(cases)<6 or len({x["id"] for x in cases})!=len(cases):e.append("catalog runtime breadth or uniqueness")
 modes={x["mode"] for x in cases}
 if modes!={"standard","conflict","extreme","multi_turn","adversarial","recovery"}:e.append("mode coverage")
 for x in cases:
  if not x["evidence"] or not x["counterevidence"] or not x["must"] or not x["forbidden"]:e.append(f"{x['id']}: shallow contract")
 report=(base/"golden/professional-report.md").read_text();card=(base/"golden/decision-card.md").read_text()
 for marker in p["markers"]+[p["runtime"],"反对证据","停止条件","回滚"]:
  if marker not in report+card:e.append(f"missing domain marker {marker}")
 for bad in ("controlled tradeoff for","could reverse if confirmed","field_0_0","TBD","TODO"):
  if bad in report+card:e.append(f"placeholder {bad}")
 if quality.score_report(report,"full")["result"]!="PASS":e.append("professional report fails shared semantic quality gate")
 return e
if __name__=="__main__":
 skills=sys.argv[1:] or list(b.P);errors=[]
 for skill in skills:errors += [f"{skill}: {x}" for x in validate(skill)]
 print("DOMAIN_PROFESSIONAL_EVALS=PASS" if not errors else "DOMAIN_PROFESSIONAL_EVALS=FAIL\n- "+"\n- ".join(errors));raise SystemExit(bool(errors))
