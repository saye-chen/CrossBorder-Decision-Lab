#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate_acceptance_and_release import compute


ROOT = Path(__file__).resolve().parents[1]


class AcceptanceAndReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.acceptance = json.loads((ROOT / "evaluations/consumer-acceptance.json").read_text(encoding="utf-8"))
        cls.rollback = json.loads((ROOT / "evaluations/rollback-drill.json").read_text(encoding="utf-8"))
        cls.l3 = json.loads((ROOT / "evaluations/l3-review-package.json").read_text(encoding="utf-8"))

    def test_current_package_passes_l3_but_not_production(self):
        result = compute(self.acceptance, self.rollback, self.l3)
        self.assertTrue(result["valid"])
        self.assertTrue(result["release_ready"])
        self.assertFalse(result["production_ready"])
        self.assertEqual(result["accepted_consumers"], 7)
        self.assertEqual(result["rollback_drills_passed"], 7)
        self.assertEqual(result["blockers"], [])

    def test_technical_acceptance_rejects_human_signature_fields(self):
        acceptance = copy.deepcopy(self.acceptance)
        acceptance["acceptances"][0]["accepted_by"] = "self"
        result = compute(acceptance, self.rollback, self.l3)
        self.assertTrue(any("HUMAN_SIGNATURE_NOT_PART" in error for error in result["errors"]))

    def test_technical_acceptance_requires_equivalent_dual_run(self):
        acceptance = copy.deepcopy(self.acceptance)
        acceptance["acceptances"][0]["dual_run_status"] = "different"
        result = compute(acceptance, self.rollback, self.l3)
        self.assertTrue(any("DUAL_RUN_NOT_EQUIVALENT" in error for error in result["errors"]))

    def test_failed_rollback_control_blocks(self):
        rollback = copy.deepcopy(self.rollback)
        rollback["drills"][0]["business_action_unchanged"] = False
        result = compute(self.acceptance, rollback, self.l3)
        self.assertTrue(any("ROLLBACK_CONTROL_FAILED" in error for error in result["errors"]))

    def test_l3_requires_substantive_evidence_review(self):
        l3 = copy.deepcopy(self.l3)
        l3["substantive_review"]["p1_open"] = 1
        result = compute(self.acceptance, self.rollback, l3)
        self.assertIn("L3_CANNOT_PASS_WITHOUT_SUBSTANTIVE_EVIDENCE_REVIEW", result["errors"])

    def test_l4_cannot_be_closed_by_release_package(self):
        l3 = copy.deepcopy(self.l3)
        l3["l4_status"] = "production"
        result = compute(self.acceptance, self.rollback, l3)
        self.assertIn("L4_MUST_REMAIN_CONTROLLED_PILOT", result["errors"])


if __name__ == "__main__":
    unittest.main()
