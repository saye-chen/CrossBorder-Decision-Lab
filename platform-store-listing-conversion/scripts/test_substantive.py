#!/usr/bin/env python3
import csv,json,pathlib,sys,unittest
HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parents[1]; sys.path.insert(0,str(HERE))
from validate_d08_contract import validate as contract
from validate_object_version import validate as obj
from validate_evidence_ledger import validate as evidence
from evaluate_hard_gates import evaluate as gates
from compare_page_versions import compare
from check_cross_layer_consistency import check
from evaluate_task_coverage import evaluate as tasks
from evaluate_variant_structure import evaluate as variants
from decompose_conversion_funnel import evaluate as funnel
from evaluate_listing_experiment import evaluate as experiment
from calculate_recoverable_value import calculate
from rank_repair_actions import rank
from validate_page_lineage import validate as lineage
from validate_output_goldens import validate as output_goldens
from validate_migration_parity import validate as migration
from validate_historical_replay import validate as historical

class SubstantiveD08(unittest.TestCase):
 def test_historical_template_blocks_production(self):
  p=ROOT/"evaluations/d08/historical-replay-template.json";d=json.loads(p.read_text());r=historical(d,p.parent);self.assertFalse(r["valid"]);self.assertFalse(r["production_ready"]);self.assertIn("authorized_cases_below_minimum:0<3",r["errors"])
 def test_100_semantically_named_scenarios(self):
  with (ROOT/"evaluations/d08/expert-scenarios.tsv").open(encoding="utf-8",newline="") as fh: rows=list(csv.DictReader(fh,delimiter="\t"))
  self.assertEqual(len(rows),100); self.assertEqual(len({r["id"] for r in rows}),100); self.assertEqual({r["group"] for r in rows},{f"S{i:02}" for i in range(1,15)})
  self.assertTrue({"standard","boundary","failure","adversarial"}<={r["mode"] for r in rows}); self.assertEqual(len({r["case"] for r in rows}),100)
 def test_12_platform_cards_have_expert_depth(self):
  cards=json.loads((ROOT/"platform-store-listing-conversion/references/platform-expert-cards.json").read_text())["cards"]
  self.assertEqual(len(cards),12)
  for c in cards:
   for f in ("objects","surfaces","diagnostics","incidents","experiments","evidence","forbidden"): self.assertGreaterEqual(len(c[f]),3,(c["platform"],f))
 def test_8_output_goldens(self): self.assertEqual(output_goldens(ROOT/"evaluations/d08/output-goldens")["status"],"pass")
 def test_6_skill_migration_parity(self): self.assertEqual(migration(ROOT,ROOT/"platform-store-listing-conversion/references/migration-manifest.json")["status"],"pass")
 def test_contract_and_deletion_gate(self):
  x=json.loads((ROOT/"platform-store-listing-conversion/references/golden-expert-report.json").read_text()); self.assertEqual(contract(x)["status"],"pass"); del x["optimization_units"][0]["exact_copy"]; self.assertEqual(contract(x)["status"],"fail")
 def test_object_version_normal_and_mixed(self):
  base={"platform":"p","country":"c","store_id":"s","listing_id":"l","page_version_id":"v1","as_of_time":"t"}; self.assertTrue(obj(base)["object_id"])
  bad={**base,"comparison":[base,{**base,"listing_id":"other","page_version_id":"v2"}]}; self.assertRaises(ValueError,obj,bad)
 def test_evidence_normal_and_causal_failure(self):
  e={"evidence_id":"E1","level":"E3","fingerprint":"f","observed_at":"t","allowed_uses":["diagnosis"]}; self.assertEqual(evidence({"evidence":[e],"claims":[]})["status"],"pass")
  self.assertEqual(evidence({"evidence":[e],"claims":[{"claim_id":"C1","claim_type":"causal","evidence_ids":["E1"]}]})["status"],"fail")
 def test_gates_fail_is_blocked(self): self.assertEqual(gates({"gates":{f"G{i}":("fail" if i==3 else "pass") for i in range(1,7)}})["action_limit"],"blocked")
 def test_version_compare_and_identity_failure(self):
  a={"object_id":"o","page_version_id":"v1","content":{"title":"a"}}; b={"object_id":"o","page_version_id":"v2","content":{"title":"b"}}; self.assertEqual(compare({"before":a,"after":b})["change_count"],1); self.assertRaises(ValueError,compare,{"before":a,"after":{**b,"object_id":"x"}})
 def test_cross_layer_conflict(self): self.assertEqual(check({"layers":{"title":{"quantity":1},"detail":{"quantity":2}}})["status"],"fail")
 def test_task_coverage_missing_proof(self): self.assertEqual(tasks({"tasks":[{"task_id":"fit","required_evidence":["E1"]}],"modules":[{"module_id":"m","task_ids":["fit"],"evidence_ids":[]}]})["status"],"fail")
 def test_variant_identity_and_inventory(self): self.assertEqual(variants({"product_identity":"p","variants":[{"variant_id":"a","attributes":{"s":"S"},"inventory":1,"product_identity":"x"}]})["status"],"fail")
 def test_funnel_conservation(self): self.assertEqual(funnel({"counts":{"qualified_exposure":10,"visit":11,"engage":1,"add_to_cart":1,"checkout":1,"paid_order":1}})["status"],"invalid")
 def test_experiment_guardrail_rolls_back(self): self.assertEqual(experiment({"control":{"n":100,"successes":10},"treatment":{"n":100,"successes":20},"primary_metric":"order","mature":True,"guardrail_breached":True})["decision"],"rollback")
 def test_value_bounds(self): self.assertRaises(ValueError,calculate,{"qualified_visits":10,"conversion_gap":2,"recoverable_share":.5,"mature_contribution_per_order":{"low":1,"high":2}})
 def test_rank_blocks_unmet_dependency(self): self.assertEqual(rank({"actions":[{"action_id":"a","severity":5,"impact":5,"confidence":1,"cost":0,"risk":0,"unmet_dependencies":["x"]}]})["blocked_actions"],["a"])
 def test_lineage_cycle_and_two_current(self): self.assertEqual(lineage({"nodes":[{"id":"a","current":True},{"id":"b","current":True}],"edges":[{"from":"a","to":"b"},{"from":"b","to":"a"}]})["status"],"fail")

if __name__=="__main__": unittest.main(verbosity=2)
