#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "release_compliance", ROOT / "scripts/validate_release_compliance.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ReleaseComplianceTest(unittest.TestCase):
    def test_policy_and_repository_boundaries_pass(self):
        self.assertEqual(MODULE.validate(), [])

    def test_policy_does_not_claim_legal_or_privacy_signoff(self):
        policy = json.loads(
            (ROOT / "governance/release-compliance-policy.json").read_text(encoding="utf-8")
        )
        self.assertTrue(all(row["legal_conclusion"] is False for row in policy["direct_dependencies"]))
        self.assertEqual(
            policy["data_privacy"]["owner_review_status"], "controlled_external_gate"
        )
        self.assertTrue(policy["limitations"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
