#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate_consumer_adapters import EXPECTED_DOMAINS, validate


ROOT = Path(__file__).resolve().parents[1]


class ConsumerAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(
            (ROOT / "evaluations/consumer-adapters.json").read_text(encoding="utf-8")
        )

    def test_all_consumer_adapters_and_exact_dual_runs_pass(self):
        self.assertEqual(validate(self.payload), [])

    def test_all_seven_business_consumers_are_inventoried(self):
        self.assertEqual(
            {item["domain"] for item in self.payload["adapters"]},
            EXPECTED_DOMAINS,
        )

    def test_unclassified_difference_blocks(self):
        payload = copy.deepcopy(self.payload)
        adapter = payload["adapters"][0]
        adapter["status"] = "adapter_ready"
        adapter.pop("difference_class", None)
        self.assertTrue(any("UNCLASSIFIED_DIFFERENCE" in error for error in validate(payload)))

    def test_false_migrated_status_blocks(self):
        payload = copy.deepcopy(self.payload)
        payload["adapters"][0]["status"] = "migrated"
        self.assertTrue(any("INVALID_MIGRATION_STATUS" in error for error in validate(payload)))

    def test_external_write_blocks(self):
        payload = copy.deepcopy(self.payload)
        payload["external_write"] = True
        self.assertIn("EXTERNAL_WRITE_FORBIDDEN", validate(payload))

    def test_missing_business_sovereignty_blocks(self):
        payload = copy.deepcopy(self.payload)
        payload["adapters"][0]["retained_sovereignty"] = []
        self.assertTrue(any("retained_sovereignty" in error for error in validate(payload)))


if __name__ == "__main__":
    unittest.main()
