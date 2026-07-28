#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate_historical_replay import validate


ROOT = Path(__file__).resolve().parents[1]


def replay(case_id: str, case_type: str) -> dict:
    return {
        "case_id": case_id,
        "case_type": case_type,
        "authorization_reference": f"AUTH-{case_id}",
        "deidentified": True,
        "decision_as_of_time": "2026-01-01T00:00:00Z",
        "input_hash": "sha256:" + case_id[-1].lower() * 64,
        "result_hash": "sha256:" + chr(ord(case_id[-1].lower()) + 3) * 64,
        "model_version": "PPFC-2026.01",
        "parameter_snapshot_version": "SNAP-1",
        "actual_outcome": {"measures": [{"metric": "contribution", "value": "1"}]},
        "matured_at": "2026-06-01T00:00:00Z",
        "concurrent_interventions": [],
        "counterfactual_and_alternatives": {"status": "reviewed"},
        "incident_and_rollback": {"incident_observed": False, "rollback_tested": True},
        "independent_review": {
            "status": "passed",
            "reviewer_role": "independent_finance_reviewer",
            "conflict_of_interest": "none"
        },
        "drift_assessment": {"status": "stable", "checked_at": "2026-07-28T00:00:00Z"}
    }


class HistoricalReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = json.loads(
            (ROOT / "evaluations/historical-replay-template.json").read_text(encoding="utf-8")
        )

    def test_empty_template_is_valid_but_controlled_pilot(self):
        result = validate(self.template)
        self.assertTrue(result["valid"])
        self.assertFalse(result["production_ready"])
        self.assertEqual(result["maturity"], "controlled pilot")

    def test_three_heterogeneous_authorized_cases_can_satisfy_computed_gate(self):
        payload = copy.deepcopy(self.template)
        payload["cases"] = [
            replay("CASE-a", "pricing"),
            replay("CASE-b", "cash_or_financial_risk"),
            replay("CASE-c", "failure_or_exit"),
        ]
        result = validate(payload)
        self.assertTrue(result["production_ready"])
        self.assertEqual(result["maturity"], "L4 Production")

    def test_manifest_cannot_self_declare_production_ready(self):
        payload = copy.deepcopy(self.template)
        payload["production_ready"] = True
        self.assertIn("production_ready_is_validator_computed", validate(payload)["errors"])

    def test_missing_authorization_and_independent_review_block(self):
        payload = copy.deepcopy(self.template)
        case = replay("CASE-d", "pricing")
        case["authorization_reference"] = ""
        case["independent_review"]["status"] = "self_reviewed"
        payload["cases"] = [case]
        errors = validate(payload)["errors"]
        self.assertTrue(any("missing_authorization" in error for error in errors))
        self.assertTrue(any("independent_review" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
