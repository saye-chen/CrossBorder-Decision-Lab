#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validator", ROOT / "scripts/validate_object_state.py")
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


def state(previous, current, blocked=None, allowed=None):
    return {
        "contract": "D05-STATE-DRAFT-1",
        "decision_id": "D-1",
        "decision_version": "v1",
        "object_ref": "O-1@v1",
        "lifecycle_stage": "qualify",
        "state": current,
        "previous_state": previous,
        "supersedes_decision_ref": None,
        "scope_hash": "a" * 64,
        "blocked_actions": blocked or [],
        "allowed_actions": allowed or [],
        "external_write": False,
        "history_refs": [],
    }


class ObjectStateTest(unittest.TestCase):
    def test_valid_fail_closed_path(self):
        self.assertEqual(validator.validate_transition(state(None, "intake")), [])
        self.assertEqual(validator.validate_transition(state("screening", "blocked", ["launch"])), [])
        self.assertEqual(validator.validate_transition(state("blocked", "remediation", ["launch"], ["collect_evidence"])), [])

    def test_direct_clearance_is_forbidden(self):
        errors = validator.validate_transition(state("screening", "cleared_for_named_use"))
        self.assertTrue(any("forbidden transition" in item for item in errors), errors)

    def test_staging_never_emits_clearance(self):
        errors = validator.validate_transition(state("conditionally_cleared", "cleared_for_named_use"), staging=True)
        self.assertIn("controlled staging cannot emit cleared_for_named_use", errors)

    def test_blocked_requires_actions_and_no_overlap(self):
        self.assertTrue(validator.validate_transition(state("screening", "blocked")))
        errors = validator.validate_transition(state("screening", "blocked", ["launch"], ["launch"]))
        self.assertIn("allowed_actions and blocked_actions overlap", errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
