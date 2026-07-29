#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "score_system_audit", ROOT / "scripts/score_system_audit.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def evidence(clean: bool) -> dict:
    return {
        "workspace_clean": clean,
        "security_release_scan": {"status": "PASS"},
        "change_impact": {"status": "PASS"},
        "checks": [
            {"id": "full-repository-audit", "status": "PASS"},
            {"id": "release-compliance", "status": "PASS"},
            {"id": "erdg-capacity", "status": "PASS"},
        ],
    }


class ScoreSystemAuditTest(unittest.TestCase):
    def test_dirty_worktree_is_capped_and_never_production_ready(self):
        result = MODULE.score(evidence(False))
        self.assertEqual((result["score"], result["grade"]), (84, "B"))
        self.assertEqual(result["hard_gates"]["G0_fixed_audit_object"], "PARTIAL_DIRTY_WORKTREE")
        self.assertFalse(result["production_ready"])

    def test_clean_worktree_does_not_fake_l4(self):
        result = MODULE.score(evidence(True))
        self.assertEqual(result["score"], 87)
        self.assertEqual(result["hard_gates"]["G5_l4_real_replay"], "CONTROLLED_EXTERNAL_GATE")
        self.assertEqual(result["dimensions"]["I_l4_real_world_validity"]["score"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
