#!/usr/bin/env python3
"""Executable 100-point release audit for all eight professional skills."""
from __future__ import annotations
import importlib.util
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SKILLS={
 "category-investment-decision":("investment","CIDM-2026.14","cidm"),
 "competitive-intelligence-monitoring":("competition","CIM-2026.10","cim"),
 "video-link-breakdown":("content_creative","VLB-2026.10","vlb"),
 "consumer-insights-customer-growth":("customer_growth","CIG-2026.09","cig"),
 "advertising-analysis-measurement-optimization":("advertising","AAMO-2026.08","d09"),
 "logistics-inventory-fulfillment-decision":("logistics","LIFD-2026.04","d07"),
 "platform-store-listing-conversion":("listing_conversion","PLCO-2026.08","d08"),
 "creator-affiliate-partnership-management":("creator_affiliate","CAPM-2026.07","capm"),
}
CORE_REPORT_SKILLS={name:value for name,value in SKILLS.items() if name != "creator-affiliate-partnership-management"}
spec=importlib.util.spec_from_file_location("quality",ROOT/"scripts/evaluate_report_quality.py")
quality=importlib.util.module_from_spec(spec); spec.loader.exec_module(quality)
repo_spec=importlib.util.spec_from_file_location("repo_validation",ROOT/"scripts/validate_repo.py")
repo_validation=importlib.util.module_from_spec(repo_spec); repo_spec.loader.exec_module(repo_validation)

def structural_validation_errors(skill_name):
 candidates=[]
 configured=os.environ.get("SKILL_CREATOR_QUICK_VALIDATE")
 if configured: candidates.append(pathlib.Path(configured).expanduser())
 codex_home=pathlib.Path(os.environ.get("CODEX_HOME", pathlib.Path.home()/".codex"))
 candidates.append(codex_home/"skills/.system/skill-creator/scripts/quick_validate.py")
 validator=next((path for path in candidates if path.is_file()),None)
 if validator:
  result=subprocess.run(["python3",str(validator),str(ROOT/skill_name)],capture_output=True,text=True)
  return [] if result.returncode==0 else [result.stdout,result.stderr]
 # GitHub runners do not install the local system Skill package. Fall back to
 # the repository-owned structural contract; test_10 still runs every full
 # repository, metadata, governance and release validator.
 return repo_validation.validate_skill(ROOT/skill_name)

def shared_payload(skill,decision_type,runtime):
 payload={"mode":"single","decision_type":decision_type,"decision_owner":skill,"participating_skills":[skill],"runtime_versions":{skill:runtime},"participant_results":{skill:{"status":"contributed"}},"professional_core":{"object_boundary":"one canonical object and version","conclusion":"Controlled decision","evidence_summary":["E1"],"counterevidence":["E2"],"commercial_constraints":["profit and capacity"],"risks_and_redlines":["P0/P1"],"actions":["controlled test"],"success_conditions":["mature pass"],"stop_conditions":["guardrail"],"limitations_and_missing_data":["real replay"]},"objects":[{"canonical_id":"o","country":"US","platform":"fixture","category":"fixture","lifecycle":"test"}],"evidence":[{"id":"E1","source_skill":skill,"evidence_type":"authorized_fixture","evidence_class":"direct","source_ref":"fixture:E1","observed_at":"2026-07-20","fingerprint":f"{skill}-E1"}],"claims":[{"id":"C1","producer_skill":skill,"claim_domain":decision_type,"state":"validated","object_id":"o","evidence_ids":["E1"],"allowed_uses":["decision_support"],"forbidden_uses":[],"effective_now":True}],"calculations":[{"id":"CAL1","calculator":"audit_fixture.py","input_hash":"sha256:audit-in","output_hash":"sha256:audit-out","status":"complete"}],"required_calculation_ids":["CAL1"],"unresolved_redlines":[],"adjustments":[]}
 if skill=="advertising-analysis-measurement-optimization":
  payload["advertising_context"]={"country":"US","platform":"fixture","as_of_time":"2026-07-20","lifecycle":"validation","axes":{"traffic_scenario":"paid","control_mode":"manual","billing_mode":"cpc","optimization_goal":"contribution"},"maturity":{"data":"mature","tracking":"mature","attribution":"mature","orders":"mature"},"ledgers":{"platform_attribution":{},"business_orders":{},"mature_contribution":{}},"incrementality_status":"not_claimed"}
 return payload

class FullRepositoryAudit(unittest.TestCase):
 def test_01_all_eight_skills_structurally_validate(self):
  for name in SKILLS:
   self.assertEqual(structural_validation_errors(name),[],name)

 def test_02_each_skill_independently_accepts_its_owned_contract(self):
  with tempfile.TemporaryDirectory() as td:
   for name,(dtype,runtime,_) in SKILLS.items():
    p=pathlib.Path(td)/f"{name}.json"; p.write_text(json.dumps(shared_payload(name,dtype,runtime)),encoding="utf-8")
    r=subprocess.run(["python3",str(ROOT/name/"scripts/validate_decision_contract.py"),str(p)],capture_output=True,text=True)
    self.assertEqual(r.returncode,0,(name,r.stdout,r.stderr))

 def test_03_each_skill_local_test_suite_executes(self):
  for name in SKILLS:
   tests=sorted((ROOT/name/"scripts").glob("test_*.py"))
   self.assertTrue(tests,name)
   for test in tests:
    r=subprocess.run(["python3",str(test)],capture_output=True,text=True)
    self.assertEqual(r.returncode,0,(test,r.stdout[-2000:],r.stderr[-2000:]))

 def test_04_all_eight_single_report_contracts_score_exactly_100(self):
  for _,(_,runtime,prefix) in CORE_REPORT_SKILLS.items():
   p=ROOT/"evaluations/golden"/f"{prefix}-single.md"; self.assertTrue(p.is_file(),p)
   report=p.read_text(encoding="utf-8"); self.assertIn(runtime,report,p)
   out=quality.score_report(report,"contract")
   self.assertEqual((out["result"],out["score"]),("PASS",100.0),out)
  p=ROOT/"creator-affiliate-partnership-management/evaluations/golden/decision-card.md"
  report=p.read_text(encoding="utf-8"); self.assertIn("CAPM-2026.07",report,p)
  out=quality.score_report(report,"contract")
  self.assertEqual((out["result"],out["score"]),("PASS",100.0),out)

 def test_05_all_eight_full_reports_score_exactly_100(self):
  for _,(_,runtime,prefix) in CORE_REPORT_SKILLS.items():
   p=ROOT/"evaluations/golden-reports"/f"{prefix}-full.md"; self.assertTrue(p.is_file(),p)
   report=p.read_text(encoding="utf-8"); self.assertIn(runtime,report,p)
   out=quality.score_report(report,"full")
   self.assertEqual((out["result"],out["score"]),("PASS",100.0),out)
  for p in (ROOT/"creator-affiliate-partnership-management/evaluations/golden").glob("*.md"):
   report=p.read_text(encoding="utf-8"); self.assertIn("CAPM-2026.07",report,p)
   out=quality.score_report(report,"full")
   self.assertEqual((out["result"],out["score"]),("PASS",100.0),out)

 def test_06_cross_skill_scenarios_cover_all_skills_and_conflicts(self):
  scenarios=json.loads((ROOT/"evaluations/cross-skill-scenarios.json").read_text())["scenarios"]
  used={x["primary"] for x in scenarios}|{p for x in scenarios for p in x["participants"]}
  self.assertEqual(used,set(CORE_REPORT_SKILLS)); self.assertGreaterEqual(sum("conflict" in x for x in scenarios),8)
  for x in scenarios:
   self.assertNotIn(x["primary"],x["participants"]); self.assertTrue(x["must"] and x["forbidden"])
  capm=json.loads((ROOT/"creator-affiliate-partnership-management/evaluations/fixtures/evaluation-catalog.json").read_text())
  cross=[x for x in capm["cases"] if x["mode"]=="cross_skill"]
  self.assertEqual(len(cross),14); self.assertEqual({p for x in cross for p in x["participants"]},{"CIDM","CIM","VLB","CIG","AAMO","LIFD","PLCO"})

 def test_07_twelve_extreme_composites_cover_all_skills_and_failure(self):
  rows=json.loads((ROOT/"evaluations/extreme-composite-scenarios.json").read_text())["scenarios"]
  self.assertEqual(len(rows),12); self.assertEqual(len({x["id"] for x in rows}),12)
  used={x["primary"] for x in rows}|{p for x in rows for p in x["participants"]}
  self.assertEqual(used,set(CORE_REPORT_SKILLS)); self.assertTrue(any("failed" in x for x in rows))
  for x in rows: self.assertGreaterEqual(len(x["must"]),4); self.assertGreaterEqual(len(x["forbidden"]),2)
  for x in rows:
   p=ROOT/"evaluations/extreme-reports"/f"{x['id']}.md"; self.assertTrue(p.is_file(),p)
   score=quality.score_report(p.read_text(encoding="utf-8"),"full"); self.assertEqual((score["result"],score["score"]),("PASS",100.0),score)
  capm=json.loads((ROOT/"creator-affiliate-partnership-management/evaluations/fixtures/evaluation-catalog.json").read_text())
  self.assertEqual(len([x for x in capm["cases"] if x["mode"]=="extreme"]),20)

 def test_08_multiturn_preserves_state_and_forbids_shortcuts(self):
  plco_challenges=json.loads((ROOT/"evaluations/d08/multiturn-challenges.json").read_text())
  lifd_challenges=json.loads((ROOT/"evaluations/d07/multiturn-challenges.json").read_text())
  self.assertGreaterEqual(len(plco_challenges),12); self.assertGreaterEqual(len(lifd_challenges),6)
  for x in plco_challenges:
   for field in ("changed_fields","must_preserve","must_answer","forbidden","action_effect"): self.assertIn(field,x)
   self.assertTrue(x["must_preserve"] and x["must_answer"] and x["forbidden"])
  report=(ROOT/"evaluations/golden-reports/d08-full.md").read_text()
  self.assertIn("连续追问与增量重算",report); self.assertIn("历史结论不静默覆盖",report)
  capm=json.loads((ROOT/"creator-affiliate-partnership-management/evaluations/fixtures/evaluation-catalog.json").read_text())
  multi=[x for x in capm["cases"] if x["mode"]=="multi_turn"]
  self.assertEqual(len(multi),12); self.assertTrue(all(len(x["turns"])>=4 for x in multi))

 def test_09_plco_concrete_optimization_cannot_regress(self):
  r=subprocess.run(["python3",str(ROOT/"scripts/test_listing_conversion_stress.py")],capture_output=True,text=True)
  self.assertEqual(r.returncode,0,(r.stdout,r.stderr))

 def test_10_repository_and_release_gates_pass(self):
  root_tests=sorted((ROOT/"scripts").glob("test_*.py"))
  for test in root_tests:
   if test.name==pathlib.Path(__file__).name: continue
   r=subprocess.run(["python3",str(test)],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,(test.name,r.stdout[-2000:],r.stderr[-2000:]))
  for validator in ("validate_repo.py","validate_governance_baseline.py"):
   r=subprocess.run(["python3",str(ROOT/"scripts"/validator)],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,(validator,r.stdout[-2000:],r.stderr[-2000:]))

 def test_11_capm_controlled_pilot_executes(self):
  name,runtime="creator-affiliate-partnership-management","CAPM-2026.07"
  self.assertEqual(structural_validation_errors(name),[],name)
  tests=subprocess.run(["python3",str(ROOT/name/"scripts/test_capm.py")],capture_output=True,text=True)
  self.assertEqual(tests.returncode,0,(tests.stdout[-3000:],tests.stderr[-3000:]))
  replay=json.loads((ROOT/name/"evaluations/historical-replay-template.json").read_text())
  self.assertEqual(replay["production_ready"],False)
  self.assertEqual(replay["cases"],[])
  self.assertIn(runtime,(ROOT/name/"SKILL.md").read_text())

if __name__=="__main__": unittest.main(verbosity=2)
