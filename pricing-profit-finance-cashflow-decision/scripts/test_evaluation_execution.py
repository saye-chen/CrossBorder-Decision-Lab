#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate_evaluation_execution import validate_and_run


ROOT = Path(__file__).resolve().parents[1]


class EvaluationExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(
            (ROOT / "evaluations/fixtures/evaluation-catalog.json").read_text(encoding="utf-8")
        )
        cls.execution_map = json.loads(
            (ROOT / "evaluations/fixtures/evaluation-execution-map.json").read_text(encoding="utf-8")
        )

    def test_all_55_cases_execute_positive_and_counterexample_assertions(self):
        result = validate_and_run(self.catalog, self.execution_map)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["catalog_cases"], 55)
        self.assertEqual(result["executed_assertions"], 110)

    def test_missing_binding_blocks(self):
        payload = copy.deepcopy(self.execution_map)
        payload["bindings"].pop()
        result = validate_and_run(self.catalog, payload)
        self.assertFalse(result["valid"])
        self.assertIn("EXECUTION_BINDINGS_MUST_MATCH_CATALOG_ORDER", result["errors"])

    def test_same_positive_and_counterexample_is_rejected(self):
        payload = copy.deepcopy(self.execution_map)
        payload["bindings"][0]["counterexample"] = payload["bindings"][0]["positive"]
        result = validate_and_run(self.catalog, payload)
        self.assertTrue(any("POSITIVE_AND_COUNTEREXAMPLE_REQUIRED" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
