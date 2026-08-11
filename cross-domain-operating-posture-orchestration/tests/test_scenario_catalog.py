#!/usr/bin/env python3
import json, sys, unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from evaluate_scenario_case import evaluate
class TestCatalog(unittest.TestCase):
 def setUp(self):self.data=json.loads((ROOT/"evaluations/scenario-cases.json").read_text());self.cases=self.data["cases"]
 def test_exactly_45_unique_semantic_cases(self):
  self.assertEqual(len(self.cases),45);self.assertEqual(len({x["id"] for x in self.cases}),45);self.assertEqual(Counter(x["scenario"] for x in self.cases),{"sales_decline":15,"profit_deterioration":15,"scale_readiness":15})
 def test_each_case_executes_expected_assertion(self):
  for case in self.cases:
   with self.subTest(case=case["id"]):self.assertEqual(evaluate(case),case["expected"])
 def test_catalog_cannot_claim_real_outcomes(self):self.assertTrue(self.data["synthetic_only"]);self.assertFalse(self.data["l4_claimed"]);self.assertFalse(self.data["external_write"])
if __name__=="__main__":unittest.main(verbosity=2)
