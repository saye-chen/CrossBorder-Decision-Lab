#!/usr/bin/env python3
"""Mutation checks for the repository-wide report contract gate."""

from __future__ import annotations

import unittest

from validate_report_contracts import _validate_card, _validate_structured_row, validate


class ReportContractTests(unittest.TestCase):
    def test_registered_report_inventory_is_clean(self):
        self.assertEqual(validate(), [])

    def test_card_without_execution_controls_is_rejected(self):
        errors = _validate_card("对象 A；运行时 R；结论 test；证据 E1；反证 E2；主权 owner；翻转条件 flip")
        self.assertIn("missing_card_field:action owner", errors)
        self.assertIn("missing_card_field:rollback", errors)

    def test_structured_report_with_external_write_is_rejected(self):
        row = {
            "report_id": "R1", "object_ref": "O1", "status": "blocked",
            "evidence": ["E1"], "counterevidence": ["E2"], "actions": ["review"],
            "success_conditions": ["condition"], "stop_conditions": ["stop"],
            "rollback": ["restore"], "lineage": {"input_hash": "sha256:x"},
            "allowed_uses": ["review"], "forbidden_uses": ["external_write"],
            "external_write": True,
        }
        self.assertIn("fixture:external_write_must_be_false", _validate_structured_row(row, "fixture"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
