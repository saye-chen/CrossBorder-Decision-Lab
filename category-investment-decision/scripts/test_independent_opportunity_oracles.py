#!/usr/bin/env python3
from __future__ import annotations
import inspect
import json
import unittest
from pathlib import Path
import independent_opportunity_oracles as oracle
import opportunity_models as main

ROOT = Path(__file__).resolve().parents[1]

class IndependentOracleTests(unittest.TestCase):
    def test_oracle_has_no_main_implementation_import(self):
        source = inspect.getsource(oracle)
        self.assertNotIn("import opportunity_models", source)
        self.assertNotIn("from opportunity_models", source)

    def test_all_eight_models_match_status_and_metrics(self):
        payload = json.loads((ROOT / "evaluations/opportunity-oracle-fixtures.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["cases"]), 8)
        self.assertEqual({case["signal_type"] for case in payload["cases"]}, set(main.MODELS))
        for case in payload["cases"]:
            expected = oracle.evaluate(case["signal_type"], case["data"], case["calibration"])
            actual = main.evaluate(case["signal_type"], case["data"], case["calibration"])
            self.assertEqual(actual["status"], expected["status"], case["id"])
            self.assertEqual(actual["metrics"], expected["metrics"], case["id"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
