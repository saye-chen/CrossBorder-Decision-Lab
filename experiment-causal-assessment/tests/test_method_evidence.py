import json
import pathlib
import sys
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from run_simulation_evaluations import run
from validate_method_qualification import validate


class MethodEvidenceTests(unittest.TestCase):
    def test_every_method_has_closed_evidence_and_a_release_disposition(self):
        registry=json.loads((ROOT/"evaluations/method-evidence-registry.json").read_text())
        required=set(registry["evidence_classes"])
        for method in registry["methods"]:
            self.assertEqual(set(method["evidence"]),required)
            self.assertTrue((ROOT/method["script"]).exists())
            self.assertTrue(set(method["evidence"].values()) <= {"pass","not_applicable_with_reason"})
            self.assertTrue(method["release_disposition"])
            self.assertTrue(method["limitations"])

    def test_l3_controlled_pilot_is_closed_without_claiming_l4(self):
        registry=json.loads((ROOT/"evaluations/method-evidence-registry.json").read_text())
        review=json.loads((ROOT/"evaluations/controlled-pilot-method-review.json").read_text())
        external=json.loads((ROOT/"evaluations/independent-review-template.json").read_text())
        self.assertEqual(registry["registry_status"],"L3_controlled_pilot_complete")
        self.assertTrue(review["l3_controlled_pilot_gate_closed"])
        self.assertFalse(review["authorization"]["external_independence_claimed"])
        self.assertFalse(external["l4_external_review_gate_closed"])

    def test_method_qualification_reproduces_and_keeps_advanced_backends_withheld(self):
        result=validate()
        self.assertTrue(result["valid"],result["failures"])
        self.assertEqual(result["active_native_method_count"],8)
        self.assertEqual(result["advanced_backend_count_withheld"],11)
        self.assertFalse(result["l4_external_review_gate_closed"])

    def test_mutation_catalog_has_required_failures(self):
        catalog=json.loads((ROOT/"evaluations/mutation-catalog.json").read_text())
        self.assertEqual({item["id"] for item in catalog["mutations"]},{f"M{i:02d}" for i in range(1,16)})
        by_id={item["id"]:item for item in catalog["mutations"]}
        self.assertIn("INDIVIDUAL_CAUSAL_CLAIM_PROHIBITED",by_id["M12"]["expected_detection"])
        self.assertIn("SURROGATE_PARADOX_RISK",by_id["M14"]["expected_detection"])
        self.assertEqual(catalog["status"],"controlled_pilot_mutation_suite_pass_l4_backend_qualification_separate")

    def test_seeded_simulation_report_is_reproducible(self):
        stored=json.loads((ROOT/"evaluations/simulation-report.json").read_text())
        current=run()
        self.assertEqual(current["checks"],stored["checks"])
        self.assertEqual(current["status"],"pass")


if __name__=="__main__": unittest.main()
