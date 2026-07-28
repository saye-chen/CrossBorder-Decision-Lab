#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate_wp8_execution_bindings import validate_and_run

ROOT = Path(__file__).resolve().parents[1]


class WP8ExecutionBindings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(
            (ROOT / "evaluations/fixtures/evaluation-catalog.json").read_text()
        )
        cls.execution_map = json.loads(
            (ROOT / "evaluations/fixtures/evaluation-execution-map.json").read_text()
        )

    def test_101_positive_and_counterexample_bindings_execute(self):
        result = validate_and_run(self.catalog, self.execution_map)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(
            (
                result["bindings"],
                result["professional_engine_assertions"],
                result["decision_assertions"],
                result["total_assertions"],
            ),
            (101, 202, 202, 404),
        )

    def test_missing_binding_blocks(self):
        payload = copy.deepcopy(self.execution_map)
        payload["bindings"].pop()
        self.assertIn(
            "EXECUTION_BINDINGS_MUST_MATCH_CATALOG_ORDER",
            validate_and_run(self.catalog, payload)["errors"],
        )

    def test_same_positive_and_counterexample_blocks(self):
        payload = copy.deepcopy(self.execution_map)
        payload["bindings"][0]["counterexample"] = copy.deepcopy(
            payload["bindings"][0]["positive"]
        )
        self.assertTrue(
            any(
                "POSITIVE_EQUALS_COUNTEREXAMPLE" in error
                for error in validate_and_run(self.catalog, payload)["errors"]
            )
        )

    def test_engine_or_mutation_tamper_blocks(self):
        payload = copy.deepcopy(self.execution_map)
        payload["bindings"][0]["engine"] = "missing.py"
        payload["bindings"][1]["counterexample"]["mutation"]["field"] = "other"
        errors = validate_and_run(self.catalog, payload)["errors"]
        self.assertTrue(any("ENGINE_BINDING_MISMATCH" in error for error in errors))
        self.assertTrue(any("MUTATION_BINDING_MISMATCH" in error for error in errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
