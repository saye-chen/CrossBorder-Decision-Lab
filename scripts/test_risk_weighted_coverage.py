#!/usr/bin/env python3
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("coverage", ROOT / "scripts/validate_risk_weighted_coverage.py")
coverage = importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(coverage)


class RiskWeightedCoverageTest(unittest.TestCase):
    def test_full_contract_passes(self):
        self.assertEqual(coverage.validate(), [])

    def test_domain_root_hash_is_explicitly_not_case_report_hash(self):
        index = json.loads((ROOT / "evaluations/professional-evaluation-index.json").read_text())
        for case in index["cases"]:
            self.assertEqual(case["golden_binding"]["level"], "domain_root")
            self.assertIsNone(case["golden_binding"]["case_report_path"])
            self.assertEqual(case["golden_hash"], case["golden_binding"]["domain_golden_root_hash"])

    def test_structured_expected_state_preserves_pipm_object(self):
        index = json.loads((ROOT / "evaluations/professional-evaluation-index.json").read_text())
        pipm = next(x for x in index["cases"] if x["domain_id"] == "D03")
        self.assertEqual(pipm["expected_state_structured"]["source_type"], "object")
        self.assertIsInstance(pipm["expected_state_structured"]["value"], dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)
