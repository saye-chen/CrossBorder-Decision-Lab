#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from evaluate_business_model_scenario import joint_stress, marginal_scale, spreadsheet_value
from ppfc_common import PPFCError
from validate_l3_audit import validate


ROOT = Path(__file__).resolve().parents[1]


class L3AuditMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads((ROOT / "evaluations/l3-audit-matrix.json").read_text(encoding="utf-8"))

    def test_all_eight_dimensions_and_standalone_reports_pass(self):
        result = validate(self.matrix)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["dimensions_passed"], 8)
        self.assertEqual(result["scenario_count"], 17)
        self.assertEqual(result["golden_reports_valid"], 3)
        self.assertEqual(result["l4_status"], "controlled pilot")

    def test_missing_continuous_challenge_is_blocking(self):
        payload = copy.deepcopy(self.matrix)
        payload["dimensions"] = [item for item in payload["dimensions"] if item["id"] != "continuous_challenge"]
        self.assertIn("AUDIT_DIMENSION_COVERAGE_INCOMPLETE", validate(payload)["errors"])

    def test_report_registry_is_authoritative_and_self_contained(self):
        payload = copy.deepcopy(self.matrix)
        payload["report_types"] = []
        self.assertIn("REPORT_TYPE_REGISTRY_MUST_HAVE_THREE", validate(payload)["errors"])

    def test_joint_pressure_recomputes_all_shocks(self):
        result = joint_stress("1000", "0.55", "0.22", "0.18", "390", "25")
        self.assertEqual(result["net_revenue"], "429")
        self.assertEqual(result["fees"], "77.22")
        self.assertEqual(result["contribution"], "-38.22")
        self.assertEqual(result["status"], "blocked")

    def test_repeated_pressure_cannot_override_negative_marginal(self):
        stages = [
            {"spend":"100","contribution":"30"},
            {"spend":"200","contribution":"25"},
            {"spend":"300","contribution":"10"},
        ]
        first = marginal_scale(stages)
        second = marginal_scale(list(reversed(stages)))
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "blocked_negative_marginal")

    def test_extreme_spreadsheet_failures_never_become_zero(self):
        for value in ("#NAME?", "#DIV/0!", "#N/A", "#VALUE!"):
            with self.subTest(value=value):
                with self.assertRaises(PPFCError):
                    spreadsheet_value(value)

    def test_production_claim_is_blocked_without_real_replay(self):
        payload = copy.deepcopy(self.matrix)
        payload["production_claim_allowed"] = True
        self.assertIn("PRODUCTION_CLAIM_FORBIDDEN", validate(payload)["errors"])


if __name__ == "__main__":
    unittest.main()
