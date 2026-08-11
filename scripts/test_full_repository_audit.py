#!/usr/bin/env python3
"""Executable release audit for fourteen expert-level L1-L3 repository skills."""
from __future__ import annotations
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
F02_RUNTIME="LCCA-2026.07"
SKILLS={
 "category-investment-decision":("investment","CIDM-2026.07","cidm"),
 "competitive-intelligence-monitoring":("competition","CIM-2026.07","cim"),
 "video-link-breakdown":("content_creative","VLB-2026.07","vlb"),
 "consumer-insights-customer-growth":("customer_growth","CIG-2026.07","cig"),
 "advertising-analysis-measurement-optimization":("advertising","AAMO-2026.07","d09"),
 "logistics-inventory-fulfillment-decision":("logistics","LIFD-2026.07","d07"),
 "platform-store-listing-conversion":("listing_conversion","PLCO-2026.07","d08"),
 "creator-affiliate-partnership-management":("creator_affiliate","CAPM-2026.07","capm"),
 "marketing-brand-campaign-management":("marketing_brand_campaign","MBCM-2026.07","mbcm"),
 "pricing-profit-finance-cashflow-decision":("pricing_profit","PPFC-2026.07","ppfc"),
 "product-innovation-product-management":("product_definition","PIPM-2026.07","pipm"),
 "supplier-procurement-production-quality-decision":("supplier_selection","SPPQ-2026.07","sppq"),
 "legal-tax-intellectual-property-market-access-decision":("market_access_gate","LTMA-2026.07","ltma"),
}
CORE_REPORT_SKILLS={name:value for name,value in SKILLS.items() if name not in {"creator-affiliate-partnership-management","marketing-brand-campaign-management","pricing-profit-finance-cashflow-decision","product-innovation-product-management","supplier-procurement-production-quality-decision","legal-tax-intellectual-property-market-access-decision"}}
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
  result=subprocess.run([sys.executable,str(validator),str(ROOT/skill_name)],capture_output=True,text=True)
  return [] if result.returncode==0 else [result.stdout,result.stderr]
 # GitHub runners do not install the local system Skill package. Fall back to
 # the repository-owned structural contract; test_10 still runs every full
 # repository, metadata, governance and release validator.
 return repo_validation.validate_skill(ROOT/skill_name)

def shared_payload(skill,decision_type,runtime):
 payload={"erdg_contract":"ERDG-CONTRACT-2026.07","mode":"single","decision_type":decision_type,"decision_owner":skill,"participating_skills":[skill],"runtime_versions":{skill:runtime},"participant_results":{skill:{"status":"contributed"}},"professional_core":{"object_boundary":"one canonical object and version","conclusion":"Controlled decision","evidence_summary":["E1"],"counterevidence":["E2"],"commercial_constraints":["profit and capacity"],"risks_and_redlines":["P0/P1"],"actions":["controlled test"],"success_conditions":["mature pass"],"stop_conditions":["guardrail"],"limitations_and_missing_data":["real replay"]},"objects":[{"canonical_id":"o","country":"US","platform":"fixture","category":"fixture","lifecycle":"test"}],"evidence":[{"id":"E1","source_skill":skill,"evidence_type":"authorized_fixture","evidence_class":"direct","source_ref":"fixture:E1","observed_at":"2026-07-20","fingerprint":f"{skill}-E1"}],"claims":[{"id":"C1","producer_skill":skill,"claim_domain":decision_type,"state":"validated","object_id":"o","evidence_ids":["E1"],"allowed_uses":["decision_support"],"forbidden_uses":[],"effective_now":True}],"calculations":[{"id":"CAL1","calculator":"audit_fixture.py","input_hash":"sha256:audit-in","output_hash":"sha256:audit-out","status":"complete"}],"required_calculation_ids":["CAL1"],"unresolved_redlines":[],"adjustments":[]}
 if skill=="advertising-analysis-measurement-optimization":
  payload["advertising_context"]={"country":"US","platform":"fixture","as_of_time":"2026-07-20","lifecycle":"validation","axes":{"traffic_scenario":"paid","control_mode":"manual","billing_mode":"cpc","optimization_goal":"contribution"},"maturity":{"data":"mature","tracking":"mature","attribution":"mature","orders":"mature"},"ledgers":{"platform_attribution":{},"business_orders":{},"mature_contribution":{}},"incrementality_status":"not_claimed"}
 return payload

class FullRepositoryAudit(unittest.TestCase):
 def test_00_f02_release_is_exercised_without_l4_claim(self):
  self.assertEqual(F02_RUNTIME,"LCCA-2026.07")
  result=subprocess.run([sys.executable,str(ROOT/'scripts/validate_f02_release.py'),'--require-l3'],capture_output=True,text=True)
  self.assertEqual(result.returncode,0,(result.stdout,result.stderr))
  audit=json.loads(result.stdout)
  self.assertTrue(audit['f02_release_audit']['l3_expert'])
  self.assertFalse(audit['f02_release_audit']['l4_external_assurance'])
  self.assertFalse(audit['policy']['production_ready'])
  self.assertFalse(audit['policy']['external_write'])
 def test_01_all_registered_skills_structurally_validate(self):
  for name in SKILLS:
   self.assertEqual(structural_validation_errors(name),[],name)

 def test_01b_ppfc_is_governed_without_production_claim(self):
  name,runtime="pricing-profit-finance-cashflow-decision","PPFC-2026.07"
  ledger=json.loads((ROOT/"governance/domain-maturity-status.json").read_text())
  row=next(item for item in ledger["domains"] if item["skill"]==name)
  self.assertEqual((row["l3"],row["l4"],row["maturity"]),("passed_automated_gate","not_passed","controlled pilot"))
  r=subprocess.run([sys.executable,str(ROOT/name/"scripts/validate_structure_contract.py")],capture_output=True,text=True)
  self.assertEqual(r.returncode,0,(r.stdout,r.stderr))
  payload=shared_payload(name,"pricing_profit",runtime)
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)/"ppfc-shared.json"; p.write_text(json.dumps(payload),encoding="utf-8")
   entry=ROOT/name/"scripts/validate_decision_contract.py"
   accepted=subprocess.run([sys.executable,str(entry),str(p)],capture_output=True,text=True)
   self.assertEqual(accepted.returncode,0,(accepted.stdout,accepted.stderr))
   payload["external_write"]=True; payload["production_ready"]=True
   p.write_text(json.dumps(payload),encoding="utf-8")
   rejected=subprocess.run([sys.executable,str(entry),str(p)],capture_output=True,text=True)
   self.assertNotEqual(rejected.returncode,0,(rejected.stdout,rejected.stderr))

 def test_01c_pipm_passes_expert_repository_gate_without_l4_claim(self):
  name="product-innovation-product-management"
  ledger=json.loads((ROOT/"governance/domain-maturity-status.json").read_text())
  row=next(item for item in ledger["domains"] if item["skill"]==name)
  self.assertEqual((row["l2"],row["l3"],row["l4"],row["maturity"]),("wp9_passed","passed_automated_gate","not_passed","controlled pilot"))
  result=subprocess.run([sys.executable,str(ROOT/name/"scripts/validate_wp2_structure.py")],capture_output=True,text=True)
  self.assertEqual(result.returncode,0,(result.stdout,result.stderr))

 def test_01d_copo_controlled_pilot_gate_executes_without_l4_claim(self):
  name, runtime = "cross-domain-operating-posture-orchestration", "COPO-2026.07"
  self.assertIn(runtime, (ROOT/name/"SKILL.md").read_text())
  result=subprocess.run([sys.executable,str(ROOT/name/"scripts/validate_decision_contract.py")],capture_output=True,text=True)
  self.assertEqual(result.returncode,0,(result.stdout,result.stderr))
  self.assertIn("L4_EXTERNAL_ASSURANCE=NOT_PASSED", subprocess.run([sys.executable,str(ROOT/name/"scripts/validate_copo.py")],capture_output=True,text=True).stdout)

 def test_02_each_skill_independently_accepts_its_owned_contract(self):
  with tempfile.TemporaryDirectory() as td:
   for name,(dtype,runtime,_) in SKILLS.items():
    p=pathlib.Path(td)/f"{name}.json"; p.write_text(json.dumps(shared_payload(name,dtype,runtime)),encoding="utf-8")
    r=subprocess.run([sys.executable,str(ROOT/name/"scripts/validate_decision_contract.py"),str(p)],capture_output=True,text=True)
    self.assertEqual(r.returncode,0,(name,r.stdout,r.stderr))

 def test_02b_each_skill_really_enforces_erdg_fail_closed_rules(self):
  with tempfile.TemporaryDirectory() as td:
   for name,(dtype,runtime,_) in SKILLS.items():
    payload=shared_payload(name,dtype,runtime)
    payload["production_ready"]=True
    payload["external_write"]=True
    p=pathlib.Path(td)/f"{name}-unsafe.json"
    p.write_text(json.dumps(payload),encoding="utf-8")
    r=subprocess.run([sys.executable,str(ROOT/name/"scripts/validate_decision_contract.py"),str(p)],capture_output=True,text=True)
    combined=(r.stdout+r.stderr).lower()
    self.assertNotEqual(r.returncode,0,(name,r.stdout,r.stderr))
    self.assertIn("erdg",combined,(name,r.stdout,r.stderr))
    self.assertTrue("production_ready" in combined or "external write" in combined,(name,r.stdout,r.stderr))

 def test_03_each_skill_local_test_suite_executes(self):
  for name in SKILLS:
   tests=sorted((ROOT/name/"scripts").glob("test_*.py"))
   self.assertTrue(tests,name)
   for test in tests:
    r=subprocess.run([sys.executable,str(test)],capture_output=True,text=True)
    self.assertEqual(r.returncode,0,(test,r.stdout[-2000:],r.stderr[-2000:]))

 def test_04_existing_single_report_contracts_score_exactly_100_and_mbcm_is_specialized(self):
  for _,(_,runtime,prefix) in CORE_REPORT_SKILLS.items():
   p=ROOT/"evaluations/golden"/f"{prefix}-single.md"; self.assertTrue(p.is_file(),p)
   report=p.read_text(encoding="utf-8"); self.assertIn(runtime,report,p)
   out=quality.score_report(report,"contract")
   self.assertEqual((out["result"],out["score"]),("PASS",100.0),out)
  p=ROOT/"creator-affiliate-partnership-management/evaluations/golden/decision-card.md"
  report=p.read_text(encoding="utf-8"); self.assertIn("CAPM-2026.07",report,p)
  out=quality.score_report(report,"contract")
  self.assertEqual((out["result"],out["score"]),("PASS",100.0),out)
  mbcm=sorted((ROOT/"marketing-brand-campaign-management/evaluations/golden").glob("*.md"))
  self.assertEqual(len(mbcm),10)
  self.assertEqual(len({next(x for x in p.read_text().splitlines() if x.startswith("专属机制：")) for p in mbcm}),10)

 def test_05_existing_full_reports_score_exactly_100_and_mbcm_has_ten_contracts(self):
  for _,(_,runtime,prefix) in CORE_REPORT_SKILLS.items():
   p=ROOT/"evaluations/golden-reports"/f"{prefix}-full.md"; self.assertTrue(p.is_file(),p)
   report=p.read_text(encoding="utf-8"); self.assertIn(runtime,report,p)
   out=quality.score_report(report,"full")
   self.assertEqual((out["result"],out["score"]),("PASS",100.0),out)
  for p in (ROOT/"creator-affiliate-partnership-management/evaluations/golden").glob("*.md"):
   report=p.read_text(encoding="utf-8"); self.assertIn("CAPM-2026.07",report,p)
   out=quality.score_report(report,"full")
   self.assertEqual((out["result"],out["score"]),("PASS",100.0),out)
  for p in (ROOT/"marketing-brand-campaign-management/evaluations/golden").glob("*.md"):
   report=p.read_text(); self.assertIn("MBCM-2026.07",report,p)
   for marker in ("停止","回滚","controlled pilot"): self.assertIn(marker,report,p)

 def test_06_cross_skill_scenarios_cover_all_skills_and_conflicts(self):
  scenarios=json.loads((ROOT/"evaluations/cross-skill-scenarios.json").read_text())["scenarios"]
  used={x["primary"] for x in scenarios}|{p for x in scenarios for p in x["participants"]}
  self.assertEqual(used,set(CORE_REPORT_SKILLS)); self.assertGreaterEqual(sum("conflict" in x for x in scenarios),8)
  for x in scenarios:
   self.assertNotIn(x["primary"],x["participants"]); self.assertTrue(x["must"] and x["forbidden"])
  capm=json.loads((ROOT/"creator-affiliate-partnership-management/evaluations/fixtures/evaluation-catalog.json").read_text())
  cross=[x for x in capm["cases"] if x["mode"]=="cross_skill"]
  self.assertEqual(len(cross),28); self.assertEqual({p for x in cross for p in x["participants"]},{"CIDM","CIM","VLB","CIG","AAMO","LIFD","PLCO"})

 def test_07_twelve_extreme_composites_cover_all_skills_and_failure(self):
  rows=json.loads((ROOT/"evaluations/extreme-composite-scenarios.json").read_text())["scenarios"]
  self.assertEqual(len(rows),12); self.assertEqual(len({x["id"] for x in rows}),12)
  used={x["primary"] for x in rows}|{p for x in rows for p in x["participants"]}
  self.assertEqual(used,set(CORE_REPORT_SKILLS)); self.assertTrue(any("failed" in x for x in rows))
  for x in rows: self.assertGreaterEqual(len(x["must"]),4); self.assertGreaterEqual(len(x["forbidden"]),2)
  for x in rows:
   p=ROOT/"evaluations/extreme-reports"/f"{x['id']}.md"; self.assertTrue(p.is_file(),p)
   score=quality.score_report(p.read_text(encoding="utf-8"),"full"); self.assertEqual((score["result"],score["score"]),("PASS",100.0),score)
  semantic=subprocess.run([sys.executable,str(ROOT/"scripts/validate_extreme_semantics.py")],capture_output=True,text=True)
  self.assertEqual(semantic.returncode,0,(semantic.stdout,semantic.stderr))
  stress=subprocess.run([sys.executable,str(ROOT/"scripts/validate_extreme_stress.py")],capture_output=True,text=True)
  self.assertEqual(stress.returncode,0,(stress.stdout,stress.stderr))
  capm=json.loads((ROOT/"creator-affiliate-partnership-management/evaluations/fixtures/evaluation-catalog.json").read_text())
  self.assertEqual(len([x for x in capm["cases"] if x["mode"]=="extreme"]),20)

 def test_08_multiturn_preserves_state_and_forbids_shortcuts(self):
  plco_challenges=json.loads((ROOT/"platform-store-listing-conversion/evaluations/multiturn-challenges.json").read_text())
  lifd_challenges=json.loads((ROOT/"logistics-inventory-fulfillment-decision/evaluations/multiturn-challenges.json").read_text())
  self.assertGreaterEqual(len(plco_challenges),12); self.assertGreaterEqual(len(lifd_challenges),6)
  for x in plco_challenges:
   for field in ("changed_fields","must_preserve","must_answer","forbidden","action_effect"): self.assertIn(field,x)
   self.assertTrue(x["must_preserve"] and x["must_answer"] and x["forbidden"])
  report=(ROOT/"evaluations/golden-reports/d08-full.md").read_text()
  self.assertIn("连续追问与增量重算",report); self.assertIn("历史结论不静默覆盖",report)
  capm=json.loads((ROOT/"creator-affiliate-partnership-management/evaluations/fixtures/evaluation-catalog.json").read_text())
  multi=[x for x in capm["cases"] if x["mode"]=="multi_turn"]
  self.assertEqual(len(multi),24); self.assertTrue(all(len(x["turns"])>=4 for x in multi))

 def test_09_plco_concrete_optimization_cannot_regress(self):
  r=subprocess.run([sys.executable,str(ROOT/"scripts/test_listing_conversion_stress.py")],capture_output=True,text=True)
  self.assertEqual(r.returncode,0,(r.stdout,r.stderr))

 def test_10_repository_and_release_gates_pass(self):
  root_tests=sorted((ROOT/"scripts").glob("test_*.py"))
  for test in root_tests:
   if test.name==pathlib.Path(__file__).name: continue
   r=subprocess.run([sys.executable,str(test)],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,(test.name,r.stdout[-2000:],r.stderr[-2000:]))
  for validator in ("validate_repo.py","validate_governance_baseline.py","validate_evaluation_taxonomy.py","validate_domain_maturity.py","validate_domain_architecture.py","validate_system_release.py","validate_capm_blueprint.py","validate_mbcm_blueprint.py","validate_release_integrity.py"):
   r=subprocess.run([sys.executable,str(ROOT/"scripts"/validator)],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,(validator,r.stdout[-2000:],r.stderr[-2000:]))

 def test_11_capm_controlled_pilot_executes(self):
  name,runtime="creator-affiliate-partnership-management","CAPM-2026.07"
  self.assertEqual(structural_validation_errors(name),[],name)
  tests=subprocess.run([sys.executable,str(ROOT/name/"scripts/test_capm.py")],capture_output=True,text=True)
  self.assertEqual(tests.returncode,0,(tests.stdout[-3000:],tests.stderr[-3000:]))
  replay=json.loads((ROOT/name/"evaluations/historical-replay-template.json").read_text())
  self.assertEqual(replay["production_ready"],False)
  self.assertEqual(replay["cases"],[])
  self.assertIn(runtime,(ROOT/name/"SKILL.md").read_text())

 def test_12_mbcm_depth_math_multiturn_and_controlled_pilot_execute(self):
  name,runtime="marketing-brand-campaign-management","MBCM-2026.07"
  self.assertEqual(structural_validation_errors(name),[],name)
  tests=subprocess.run([sys.executable,str(ROOT/name/"scripts/test_mbcm.py")],capture_output=True,text=True)
  self.assertEqual(tests.returncode,0,(tests.stdout[-3000:],tests.stderr[-3000:]))
  science=subprocess.run([sys.executable,str(ROOT/name/"scripts/test_marketing_science.py")],capture_output=True,text=True)
  self.assertEqual(science.returncode,0,(science.stdout[-3000:],science.stderr[-3000:]))
  integration=subprocess.run([sys.executable,str(ROOT/"scripts/test_mbcm_integration.py")],capture_output=True,text=True)
  self.assertEqual(integration.returncode,0,(integration.stdout[-3000:],integration.stderr[-3000:]))
  catalog=json.loads((ROOT/name/"evaluations/fixtures/evaluation-catalog.json").read_text())
  self.assertEqual(catalog["total"],120)
  self.assertEqual(len(catalog["coverage"]["scenarios"]),13)
  self.assertEqual(len(catalog["coverage"]["estimation_methods"]),10)
  replay=json.loads((ROOT/name/"evaluations/historical-replay-template.json").read_text())
  self.assertEqual((replay["production_ready"],replay["cases"]),(False,[]))
  self.assertIn(runtime,(ROOT/name/"SKILL.md").read_text())

 def test_13_erdg_economic_risk_decision_governance_executes(self):
  test=ROOT/"governance/erdg/tests/test_erdg.py"
  self.assertTrue(test.is_file())
  result=subprocess.run([sys.executable,str(test)],capture_output=True,text=True)
  self.assertEqual(result.returncode,0,(result.stdout[-4000:],result.stderr[-4000:]))
  version=json.loads((ROOT/"governance/erdg/contract-version.json").read_text())
  self.assertEqual(version["owner"],"repository-governance")
  self.assertEqual((version["production_ready"],version["l4"]),(False,"not_passed"))

 def test_14_erdg_reports_recompute_and_capacity_gate_executes(self):
  for script in ("validate_report_recomputation.py","validate_erdg_capacity.py"):
   result=subprocess.run([sys.executable,str(ROOT/"governance/erdg/scripts"/script)],capture_output=True,text=True)
   self.assertEqual(result.returncode,0,(script,result.stdout,result.stderr))

if __name__=="__main__": unittest.main(verbosity=2)
