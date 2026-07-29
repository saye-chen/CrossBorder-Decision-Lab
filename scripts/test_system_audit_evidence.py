#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "audit_evidence", ROOT / "scripts/generate_system_audit_evidence.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class AuditEvidenceTests(unittest.TestCase):
    def test_inventory_separates_files_cases_and_assertions(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            path = Path(directory) / "test_fixture.py"
            path.write_text(
                "def test_one():\n    assert True\n"
                "class T:\n    def test_two(self):\n        self.assertEqual(1, 1)\n",
                encoding="utf-8",
            )
            result = MODULE.discover_tests([path])
            self.assertEqual(result["test_files"], 1)
            self.assertEqual(result["static_test_cases"], 2)
            self.assertEqual(result["static_assertion_calls"], 2)

    def test_security_scan_reports_path_without_secret_value(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            path = Path(directory) / "fixture.txt"
            path.write_text("token=ghp_" + "A" * 24, encoding="utf-8")
            result = MODULE.security_scan([path])
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["findings"][0]["pattern"], "github_token")
            self.assertNotIn("ghp_", str(result["findings"]))

    def test_change_impact_fails_closed_for_unmapped_path(self):
        result = MODULE.change_impact(["not-registered/example.txt"])
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["unmapped_paths"], ["not-registered/example.txt"])

    def test_change_impact_maps_audit_governance(self):
        result = MODULE.change_impact(["governance/system-audit-standard.md"])
        self.assertEqual(result["status"], "PASS")
        self.assertIn("repository-release-governance", result["affected_contracts"])

    def test_clean_and_dirty_verdicts_are_distinct(self):
        checks = [{"status": "PASS"}]
        self.assertEqual(
            MODULE.audit_verdict(checks, "PASS", "PASS", True), "PASS_CLEAN_CANDIDATE"
        )
        self.assertEqual(
            MODULE.audit_verdict(checks, "PASS", "PASS", False), "PASS_WORKTREE_DIAGNOSTIC"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
