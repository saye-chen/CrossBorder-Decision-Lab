#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(n,f):s=importlib.util.spec_from_file_location(n,ROOT/"scripts"/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
runner=load("runner","run_wp8_evaluations.py");coverage=load("coverage","validate_wp8_coverage.py");golden=load("golden","run_golden_evaluations.py")
class WP8(unittest.TestCase):
 def test_catalog_executes_101_cases_and_mutations(self):
  cat=json.loads((ROOT/"evaluations/fixtures/evaluation-catalog.json").read_text());r=runner.run(cat);self.assertEqual((r["passed"],r["total"],r["failures"]),(101,101,[]))
  self.assertEqual(set(r["engine_invocations"]),coverage.EXECUTABLES);self.assertEqual(sum(r["engine_invocations"].values()),101)
 def test_expert_coverage_is_closed(self):self.assertEqual(coverage.validate(),[])
 def test_mutation_is_not_expected_answer_leakage(self):
  cat=json.loads((ROOT/"evaluations/fixtures/evaluation-catalog.json").read_text())
  self.assertTrue(all("expected" not in x["fixture"] for x in cat["cases"]))
 def test_l4_remains_controlled(self):
  cat=json.loads((ROOT/"evaluations/fixtures/evaluation-catalog.json").read_text());self.assertEqual({x["expected"]["maturity"] for x in cat["cases"]},{"controlled pilot"})
 def test_golden_is_bound_to_actual_professional_execution(self):
  recorded=json.loads((ROOT/"evaluations/golden-execution-results.json").read_text())
  self.assertEqual(golden.validate(recorded),[])
  self.assertTrue(recorded["passed"])
  self.assertTrue(all(x["passed"] for x in recorded["results"]))
  self.assertTrue(all(x["execution_source"]=="scenario_owned_fixture" for x in recorded["results"]))
  self.assertTrue(all(x["actual_output"]!=x["mutation_output"] for x in recorded["results"]))
 def test_golden_hash_tamper_is_detected(self):
  recorded=json.loads((ROOT/"evaluations/golden-execution-results.json").read_text())
  recorded["results"][0]["report_hash"]="sha256:"+"0"*64
  self.assertIn("GOLDEN_EXECUTION_EVIDENCE_DRIFT",golden.validate(recorded))
if __name__=="__main__":unittest.main(verbosity=2)
