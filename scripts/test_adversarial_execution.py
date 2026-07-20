#!/usr/bin/env python3
import json,unittest
from pathlib import Path
from validate_adversarial_contract import validate
ROOT=Path(__file__).resolve().parents[1]
class AdversarialExecution(unittest.TestCase):
 def test_each_case_triggers_its_specific_guard(self):
  cases=json.loads((ROOT/"evaluations/adversarial-executable-fixtures.json").read_text())["cases"]
  self.assertEqual(len(cases),5)
  for case in cases:
   with self.subTest(case=case["id"]):
    result=validate(case["payload"]);self.assertFalse(result["valid"]);self.assertTrue(any(x.startswith(case["expected_error"]) for x in result["errors"]),result)
 def test_clean_contract_passes(self):
  payload={"evidence":[{"id":"E1","source_ref":"authorized:x","observed_at":"2026-01-01","fingerprint":"f1"}],"actions":[{"id":"A1","domain":"advertising","owner":"advertising-analysis-measurement-optimization"}],"versions":[{"object_id":"o","version":"v1","current":True}],"numeric_claims":[{"id":"N1","value":23,"calculation_id":"CAL1","input_hash":"sha256:i","output_hash":"sha256:o"}],"participant_results":[],"claims":[{"id":"C1","producer_skill":"advertising-analysis-measurement-optimization","state":"validated","evidence_ids":["E1"]}]}
  self.assertTrue(validate(payload)["valid"])
if __name__=="__main__":unittest.main(verbosity=2)
