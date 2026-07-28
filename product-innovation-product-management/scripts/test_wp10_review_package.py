#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

import validate_wp10_review_package as validator

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evaluations/review-package"


class WP10ReviewPackage(unittest.TestCase):
    def test_package_is_current_and_fail_closed(self):
        self.assertEqual(validator.validate(), [])

    def test_evidence_tamper_is_detected(self):
        path = OUT / "evidence-index.json"
        original = path.read_text(encoding="utf-8")
        try:
            payload = json.loads(original)
            payload["evidence"][0]["sha256"] = "sha256:" + "0" * 64
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertTrue(any("HASH_DRIFT" in error for error in validator.validate()))
        finally:
            path.write_text(original, encoding="utf-8")

    def test_self_signed_or_partial_shortcut_is_blocked(self):
        path = OUT / "independent-signoff.json"
        original = path.read_text(encoding="utf-8")
        try:
            payload = json.loads(original)
            payload["required_roles"][0]["decision"] = "approved"
            payload["required_roles"][0]["reviewer_id"] = "implementation-team"
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertIn("PARTIAL_SIGNOFF_STATE_INVALID", validator.validate())
        finally:
            path.write_text(original, encoding="utf-8")

    def test_l4_shortcut_is_blocked(self):
        path = OUT / "evidence-index.json"
        original = path.read_text(encoding="utf-8")
        try:
            payload = json.loads(original)
            payload["maturity_constraint"]["l4"] = "passed"
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertIn("MATURITY_SHORTCUT", validator.validate())
        finally:
            path.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main(verbosity=2)
