#!/usr/bin/env python3
from __future__ import annotations
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from reality_recovery import RecoveryError, apply_consumer_recovery, build_root_batch, close_batch, impact_closure, net_capital_at_risk


EDGES = [
    {"source": "E-ROOT", "target": "SIG-1"},
    {"source": "SIG-1", "target": "DEC-1"},
    {"source": "SIG-1", "target": "DEC-2"},
    {"source": "OTHER", "target": "DEC-3"},
]
CONSUMERS = [
    {"consumer_id": "C-SAFETY", "decision_id": "DEC-1", "current_effective_decision_id": "OLD-1", "dependency_ids": ["DEC-1"], "risk_flags": ["human_safety"], "assets": [{"asset_id": "A1", "committed_cash": 10}], "action_status": "executing", "blast_radius": 1},
    {"consumer_id": "C-CAPITAL", "decision_id": "DEC-2", "current_effective_decision_id": "OLD-2", "dependency_ids": ["DEC-2"], "risk_flags": [], "assets": [{"asset_id": "A2", "inventory_cost": 10000, "inventory_recovery_value": 2000}], "action_status": "approved", "blast_radius": 2},
    {"consumer_id": "C-OTHER", "decision_id": "DEC-3", "current_effective_decision_id": "OLD-3", "dependency_ids": ["DEC-3"], "risk_flags": [], "assets": [], "action_status": "planned", "blast_radius": 1},
]
CALIBRATION = {"r2_net_capital_threshold": 5000, "r3_blast_radius_threshold": 10}


def batch():
    return build_root_batch({"batch_id": "RB-1", "invalidated_evidence_ids": ["E-ROOT"], "detected_at": "2026-08-04T10:00:00+08:00"}, EDGES, copy.deepcopy(CONSUMERS), CALIBRATION)


class RealityRecoveryTests(unittest.TestCase):
    def test_impact_closure_finds_all_and_only_downstream_consumers(self):
        self.assertEqual(impact_closure(["E-ROOT"], EDGES), ["DEC-1", "DEC-2", "E-ROOT", "SIG-1"])

    def test_root_batch_uses_highest_risk_and_freezes_actions(self):
        value = batch()
        self.assertEqual(value["queue"], "R0")
        self.assertEqual([item["consumer_id"] for item in value["consumers"]], ["C-SAFETY", "C-CAPITAL"])
        self.assertEqual([item["queue"] for item in value["consumers"]], ["R0", "R2"])
        self.assertTrue(all(item["action_status"] == "paused" for item in value["consumers"]))
        self.assertFalse(value["external_actions_automated"])

    def test_net_capital_rejects_duplicate_or_double_counted_assets(self):
        with self.assertRaisesRegex(RecoveryError, "unique"):
            net_capital_at_risk([{"asset_id": "A", "committed_cash": 1}, {"asset_id": "A", "inventory_cost": 2}])
        with self.assertRaisesRegex(RecoveryError, "cannot count"):
            net_capital_at_risk([{"asset_id": "A", "committed_cash": 1, "inventory_cost": 2}])

    def test_partial_consumer_recovery_cannot_close_batch(self):
        value = batch()
        value = apply_consumer_recovery(value, {"consumer_id": "C-SAFETY", "recovery_status": "recovered", "recalculation_complete": True, "gates_rechecked": True, "consumer_notified": True, "resolution_action": "keep_frozen_until_owner_release", "new_effective_decision_id": "NEW-1", "decision_changed": True})
        self.assertEqual(value["recovery_status"], "partially_recovered")
        with self.assertRaisesRegex(RecoveryError, "partial"):
            close_batch(value, {"replacement_evidence_status": "validated"})

    def test_full_recovery_requires_new_effective_decision_and_closure_evidence(self):
        value = batch()
        base = {"recovery_status": "recovered", "recalculation_complete": True, "gates_rechecked": True, "consumer_notified": True, "resolution_action": "controlled_release", "decision_changed": True}
        with self.assertRaisesRegex(RecoveryError, "new effective"):
            apply_consumer_recovery(value, {**base, "consumer_id": "C-SAFETY"})
        value = apply_consumer_recovery(value, {**base, "consumer_id": "C-SAFETY", "new_effective_decision_id": "NEW-1"})
        value = apply_consumer_recovery(value, {**base, "consumer_id": "C-CAPITAL", "new_effective_decision_id": "NEW-2"})
        self.assertEqual(value["recovery_status"], "recovered")
        closure = {"replacement_evidence_status": "validated", "root_cause_test_id": "test_api_field_invalidation", "loss_recorded": True, "owner_recorded": True, "prevention_action": "contract_test", "closed_at": "2026-08-04T12:00:00+08:00"}
        value = close_batch(value, closure)
        self.assertEqual(value["recovery_status"], "closed")
        with self.assertRaisesRegex(RecoveryError, "append-only"):
            apply_consumer_recovery(value, {**base, "consumer_id": "C-SAFETY", "new_effective_decision_id": "NEWER-1"})

    def test_changed_decision_cannot_reuse_old_effective_id(self):
        value = batch()
        update = {"consumer_id": "C-SAFETY", "recovery_status": "recovered", "recalculation_complete": True, "gates_rechecked": True, "consumer_notified": True, "resolution_action": "exit", "new_effective_decision_id": "OLD-1", "decision_changed": True}
        with self.assertRaisesRegex(RecoveryError, "cannot retain"):
            apply_consumer_recovery(value, update)

    def test_cli_builds_same_root_batch_and_rejects_unknown_operation(self):
        script = Path(__file__).resolve().with_name("reality_recovery_engine.py")
        payload = {"operation": "build", "event": {"batch_id": "RB-CLI", "invalidated_evidence_ids": ["E-ROOT"], "detected_at": "2026-08-04T10:00:00+08:00"}, "edges": EDGES, "consumers": CONSUMERS, "calibration": CALIBRATION}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "recovery.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["queue"], "R0")
            payload["operation"] = "auto_recall"
            path.write_text(json.dumps(payload), encoding="utf-8")
            rejected = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
