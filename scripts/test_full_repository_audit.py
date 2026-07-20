#!/usr/bin/env python3
"""Executable 100-point release audit for all seven professional skills."""
from __future__ import annotations
import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SKILLS={
 "category-investment-decision":("investment","CIDM-2026.14","cidm"),
 "competitive-intelligence-monitoring":("competition","CIM-2026.10","cim"),
 "video-link-breakdown":("content_creative","VLB-2026.09","vlb"),
 "consumer-insights-customer-growth":("customer_growth","CIG-2026.09","cig"),
 "advertising-analysis-measurement-optimization":("advertising","D09-2026.07","d09"),
 "logistics-inventory-fulfillment-decision":("logistics","D07-2026.03","d07"),
 "platform-store-listing-conversion":("listing_conversion","D08-2026.01","d08"),
}
spec=importlib.util.spec_from_file_location("quality",ROOT/"scripts/evaluate_report_quality.py")
quality=importlib.util.module_from_spec(spec); spec.loader.exec_module(quality)

def shared_payload(skill,decision_type,runtime):
 return {"mode":"single","decision_type":decision_type,"decision_owner":skill,"participating_skills":[skill],"runtime_versions":{skill:runtime},"participant_results":{skill:{"status":"contributed"}},"professional_core":{"object_boundary":"one canonical object and version","conclusion":"Controlled decision","evidence_summary":["E1"],"counterevidence":["E2"],"commercial_constraints":["profit and capacity"],"risks_and_redlines":["P0/P1"],"actions":["controlled test"],"success_conditions":["mature pass"],"stop_conditions":["guardrail"],"limitations_and_missing_data":["real replay"]},"objects":[{"canonical_id":"o","country":"US","platform":"fixture","category":"fixture","lifecycle":"test"}],"evidence":[{"id":"E1","source_skill":skill,"evidence_type":"authorized_fixture","evidence_class":"direct","source_ref":"fixture:E1","observed_at":"2026-07-20","fingerprint":f"{skill}-E1"}],"claims":[{"id":"C1","producer_skill":skill,"claim_domain":decision_type,"state":"validated","object_id":"o","evidence_ids":["E1"],"allowed_uses":["decision_support"],"forbidden_uses":[],"effective_now":True}],"calculations":[{"id":"CAL1","calculator":"audit_fixture.py","input_hash":"sha256:audit-in","output_hash":"sha256:audit-out","status":"complete"}],"required_calculation_ids":["CAL1"],"unresolved_redlines":[],"adjustments":[]}

class FullRepositoryAudit(unittest.TestCase):
 def test_01_all_seven_skills_structurally_validate(self):
  validator=pathlib.Path('/Users/chenwenlong/.codex/skills/.system/skill-creator/scripts/quick_validate.py')
  for name in SKILLS:
   r=subprocess.run(["python3",str(validator),str(ROOT/name)],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,(name,r.stdout,r.stderr))

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

 def test_04_seven_single_reports_score_exactly_100(self):
  for _,(_,_,prefix) in SKILLS.items():
   p=ROOT/"evaluations/golden"/f"{prefix}-single.md"; self.assertTrue(p.is_file(),p)
   out=quality.score_report(p.read_text(encoding="utf-8"),"contract")
   self.assertEqual((out["result"],out["score"]),("PASS",100.0),out)

 def test_05_seven_full_reports_score_exactly_100(self):
  for _,(_,_,prefix) in SKILLS.items():
   p=ROOT/"evaluations/golden-reports"/f"{prefix}-full.md"; self.assertTrue(p.is_file(),p)
   out=quality.score_report(p.read_text(encoding="utf-8"),"full")
   self.assertEqual((out["result"],out["score"]),("PASS",100.0),out)

 def test_06_cross_skill_scenarios_cover_all_skills_and_conflicts(self):
  scenarios=json.loads((ROOT/"evaluations/cross-skill-scenarios.json").read_text())["scenarios"]
  used={x["primary"] for x in scenarios}|{p for x in scenarios for p in x["participants"]}
  self.assertEqual(used,set(SKILLS)); self.assertGreaterEqual(sum("conflict" in x for x in scenarios),8)
  for x in scenarios:
   self.assertNotIn(x["primary"],x["participants"]); self.assertTrue(x["must"] and x["forbidden"])

 def test_07_twelve_extreme_composites_cover_all_skills_and_failure(self):
  rows=json.loads((ROOT/"evaluations/extreme-composite-scenarios.json").read_text())["scenarios"]
  self.assertEqual(len(rows),12); self.assertEqual(len({x["id"] for x in rows}),12)
  used={x["primary"] for x in rows}|{p for x in rows for p in x["participants"]}
  self.assertEqual(used,set(SKILLS)); self.assertTrue(any("failed" in x for x in rows))
  for x in rows: self.assertGreaterEqual(len(x["must"]),4); self.assertGreaterEqual(len(x["forbidden"]),2)
  for x in rows:
   p=ROOT/"evaluations/extreme-reports"/f"{x['id']}.md"; self.assertTrue(p.is_file(),p)
   score=quality.score_report(p.read_text(encoding="utf-8"),"full"); self.assertEqual((score["result"],score["score"]),("PASS",100.0),score)

 def test_08_multiturn_preserves_state_and_forbids_shortcuts(self):
  d08=json.loads((ROOT/"evaluations/d08/multiturn-challenges.json").read_text())
  d07=json.loads((ROOT/"evaluations/d07/multiturn-challenges.json").read_text())
  self.assertGreaterEqual(len(d08),12); self.assertGreaterEqual(len(d07),6)
  for x in d08:
   for field in ("changed_fields","must_preserve","must_answer","forbidden","action_effect"): self.assertIn(field,x)
   self.assertTrue(x["must_preserve"] and x["must_answer"] and x["forbidden"])
  report=(ROOT/"evaluations/golden-reports/d08-full.md").read_text()
  self.assertIn("连续追问与增量重算",report); self.assertIn("历史结论不静默覆盖",report)

 def test_09_d08_concrete_optimization_cannot_regress(self):
  r=subprocess.run(["python3",str(ROOT/"scripts/test_listing_conversion_stress.py")],capture_output=True,text=True)
  self.assertEqual(r.returncode,0,(r.stdout,r.stderr))

 def test_10_repository_and_release_gates_pass(self):
  commands=("validate_repo.py","test_governance.py","test_cross_skill_integration.py","test_expert_release.py","test_domain_stress.py","test_category_semantics.py","test_advertising_stress.py","test_logistics_stress.py")
  for cmd in commands:
   r=subprocess.run(["python3",str(ROOT/"scripts"/cmd)],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,(cmd,r.stdout[-2000:],r.stderr[-2000:]))

if __name__=="__main__": unittest.main(verbosity=2)
