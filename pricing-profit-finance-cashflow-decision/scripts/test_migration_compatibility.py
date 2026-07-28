#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate_migration_compatibility import EXPECTED_DOMAINS, validate


ROOT = Path(__file__).resolve().parents[1]


class MigrationCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(
            (ROOT / "evaluations/migration-compatibility.json").read_text(encoding="utf-8")
        )

    def test_inventory_and_equivalence_cases_pass(self):
        self.assertEqual(validate(self.payload), [])

    def test_all_current_consumers_are_inventoried(self):
        self.assertEqual(
            {item["domain"] for item in self.payload["consumers"]},
            EXPECTED_DOMAINS,
        )

    def test_retirement_is_blocked_before_consumer_migration(self):
        payload = copy.deepcopy(self.payload)
        payload["retirement_allowed"] = True
        self.assertIn("RETIREMENT_MUST_REMAIN_BLOCKED", validate(payload))

    def test_false_migration_claim_is_blocked(self):
        payload = copy.deepcopy(self.payload)
        payload["consumers"][1]["migration_status"] = "migrated"
        self.assertIn("UNSUPPORTED_MIGRATION_CLAIM", validate(payload))

    def test_equivalence_difference_is_not_silently_accepted(self):
        payload = copy.deepcopy(self.payload)
        payload["equivalence_cases"][0]["expected"]["operating_profit"] = "23"
        self.assertIn("EQ-PRICE-001:EQUIVALENCE_DIFFERENCE", validate(payload))

    def test_comparison_without_same_snapshot_is_blocked(self):
        payload = copy.deepcopy(self.payload)
        del payload["equivalence_cases"][0]["parameter_snapshot_version"]
        errors = validate(payload)
        self.assertTrue(any("MISSING_DIMENSIONS" in error for error in errors))

    def test_rollback_cannot_write_external_systems(self):
        payload = copy.deepcopy(self.payload)
        payload["rollback"]["external_write"] = True
        self.assertIn("ROLLBACK_EXTERNAL_WRITE_FORBIDDEN", validate(payload))


if __name__ == "__main__":
    unittest.main()
