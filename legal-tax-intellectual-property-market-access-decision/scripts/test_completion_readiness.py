#!/usr/bin/env python3
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("readiness", ROOT / "scripts/validate_completion_readiness.py")
readiness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readiness)


class CompletionReadinessTests(unittest.TestCase):
    def policy(self):
        return json.loads(readiness.POLICY_PATH.read_text(encoding="utf-8"))

    def test_engineering_readiness_is_computed_while_external_assurance_stays_separate(self):
        result = readiness.compute(self.policy(), runner=lambda _: (True, "passed"))
        self.assertTrue(result["engineering_ready"])
        self.assertEqual(result["engineering_label"], "controlled_pilot_engineering_ready")
        self.assertFalse(result["external_assurance"]["external_assurance_complete"])
        self.assertFalse(result["external_assurance"]["l4_passed"])
        self.assertFalse(result["production_ready"])
        self.assertFalse(result["l4_is_an_engineering_gate"])

    def test_manual_completion_status_cannot_bypass_computation(self):
        policy = self.policy()
        policy["engineering_ready"] = True
        result = readiness.compute(policy, runner=lambda _: (True, "passed"))
        self.assertFalse(result["engineering_ready"])
        self.assertTrue(any("self-reported" in x for x in result["engineering_errors"]))

    def test_required_validator_cannot_be_deleted(self):
        policy = self.policy()
        policy["required_validators"].pop()
        result = readiness.compute(policy, runner=lambda _: (True, "passed"))
        self.assertFalse(result["engineering_ready"])

    def test_any_actual_validator_failure_blocks_engineering_readiness(self):
        def runner(path):
            return (False, "mutated failure") if path.endswith("test_decision_engine.py") else (True, "passed")
        result = readiness.compute(self.policy(), runner=runner)
        self.assertFalse(result["engineering_ready"])
        self.assertTrue(any("test_decision_engine.py" in x for x in result["engineering_errors"]))

    def test_claim_boundary_widening_is_rejected(self):
        policy = copy.deepcopy(self.policy())
        policy["claim_boundaries"]["production_ready"] = True
        result = readiness.compute(policy, runner=lambda _: (True, "passed"))
        self.assertFalse(result["engineering_ready"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
