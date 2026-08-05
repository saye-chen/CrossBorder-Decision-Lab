#!/usr/bin/env python3
"""Mutation-killing tests for the professional engineering release gate."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


decision = load("legal-tax-intellectual-property-market-access-decision/scripts/decision_engine.py", "d05_decision")
evidence_checks = load("legal-tax-intellectual-property-market-access-decision/scripts/validate_input_evidence.py", "d05_evidence")
registry_checks = load("scripts/validate_professional_evaluation_registry.py", "professional_registry")
adversarial = load("scripts/validate_adversarial_contract.py", "adversarial")
continuity = load("scripts/cross_skill_continuity.py", "continuity")
readiness = load("legal-tax-intellectual-property-market-access-decision/scripts/validate_completion_readiness.py", "readiness")
plco_consumer = load("platform-store-listing-conversion/scripts/validate_d05_consumer.py", "plco_consumer")


def valid_evidence() -> dict:
    return {
        "contract": "D05-EVIDENCE-DRAFT-1", "evidence_id": "E-1", "source_type": "official_rule",
        "source_ref": "official:1", "source_family": "issuer-a", "authorization_ref": None,
        "object_ref": "O-1@v1", "jurisdictions": ["US"], "allowed_uses": ["screening"],
        "obtained_at": "2026-08-01T00:00:00+00:00", "verified_at": "2026-08-02T00:00:00+00:00",
        "expires_at": "2026-09-01T00:00:00+00:00", "content_hash": "a" * 64,
        "supports_claims": ["C-1"], "opposes_claims": [], "limitations": [], "state": "current",
    }


class ReleaseAntiCheatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(registry_checks.REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.index = json.loads(registry_checks.INDEX_PATH.read_text(encoding="utf-8"))

    def test_remove_noncompensable_redline_is_killed(self):
        result = decision.evaluate_gate(
            redlines=["major_safety_risk"], evidence_gaps=[], professional_reviews=[],
            requested_action="external_commercial_action",
        )
        self.assertEqual((result["status"], result["action_ceiling"]), ("blocked", "collect_evidence"))

    def test_raise_action_ceiling_is_killed(self):
        result = decision.evaluate_gate(
            redlines=[], evidence_gaps=[], professional_reviews=["qualified_review"],
            requested_action="external_commercial_action",
        )
        self.assertEqual(result["action_ceiling"], "reversible_preparation")

    def test_expired_evidence_to_current_is_killed(self):
        item = valid_evidence()
        item["expires_at"] = "2026-08-04T00:00:00+00:00"
        self.assertIn(
            "expired evidence cannot be current",
            evidence_checks.validate_evidence(item, "2026-08-05T00:00:00+00:00"),
        )

    def test_synthetic_evidence_to_production_is_killed(self):
        item = valid_evidence()
        item["source_type"] = "synthetic_fixture"
        item["allowed_uses"] = ["production_decision"]
        self.assertIn(
            "synthetic evidence cannot support production decisions",
            evidence_checks.validate_evidence(item, "2026-08-05T00:00:00+00:00"),
        )

    def test_delete_counterevidence_is_killed(self):
        index = copy.deepcopy(self.index)
        index["cases"][0]["counterevidence"] = []
        self.assertTrue(any("counterevidence" in x for x in registry_checks.validate(self.registry, index)))

    def test_generic_template_substitution_is_killed(self):
        index = copy.deepcopy(self.index)
        replacement_hash = "0" * 64
        for case in index["cases"]:
            if case["domain_id"] == "D01":
                case["golden_hash"] = replacement_hash
        self.assertTrue(any("golden fingerprint drift" in x for x in registry_checks.validate(self.registry, index)))

    def test_auxiliary_domain_final_decision_is_killed(self):
        payload = {
            "evidence": [{"id": "E1", "source_ref": "authorized:x", "observed_at": "2026-08-05", "fingerprint": "f1"}],
            "actions": [{"id": "A1", "domain": "advertising", "owner": "video-link-breakdown"}],
            "claims": [{"id": "C1", "producer_skill": "video-link-breakdown", "state": "proposed", "evidence_ids": ["E1"]}],
        }
        self.assertTrue(any(x.startswith("sovereignty_overreach") for x in adversarial.validate(payload)["errors"]))

    def test_delete_consumer_rejection_is_killed(self):
        packets = json.loads((ROOT / "legal-tax-intellectual-property-market-access-decision/evaluations/d05-consumer-packets.json").read_text(encoding="utf-8"))["packets"]
        packet = copy.deepcopy(packets["D08"])
        packet["claims"][1]["publish"] = True
        self.assertTrue(plco_consumer.validate(packet))

    def test_old_version_overwrite_is_killed(self):
        ledger = continuity.Ledger()
        self.assertEqual(ledger.receive({"message_id": "new", "object_id": "O1", "version": 2, "content_hash": "h2", "status": "contributed"}), "accepted")
        self.assertEqual(ledger.receive({"message_id": "old", "object_id": "O1", "version": 1, "content_hash": "h1", "status": "contributed"}), "late_version_ignored")
        self.assertEqual(ledger.current_versions["O1"], 2)

    def test_partial_failure_overall_pass_is_killed(self):
        result = continuity.partial_failure(
            ["LIFD"],
            [{"id": "inventory", "depends_on": ["LIFD"], "state": "validated"}, {"id": "page", "depends_on": ["PLCO"], "state": "validated"}],
        )
        self.assertFalse(result["overall_pass"])
        self.assertEqual(result["affected"], ["inventory"])

    def test_manual_completion_tamper_is_killed(self):
        policy = json.loads(readiness.POLICY_PATH.read_text(encoding="utf-8"))
        policy["engineering_ready"] = True
        result = readiness.compute(policy, runner=lambda _: (True, "passed"))
        self.assertFalse(result["engineering_ready"])

    def test_same_source_fake_independence_is_killed(self):
        payload = {
            "independent_source_count": 2,
            "evidence": [
                {"id": "E1", "source_ref": "page:a", "observed_at": "2026-08-05", "fingerprint": "f1", "source_family": "issuer-a"},
                {"id": "E2", "source_ref": "page:b", "observed_at": "2026-08-05", "fingerprint": "f2", "source_family": "issuer-a"},
            ],
            "claims": [{"id": "C1", "state": "proposed", "evidence_ids": ["E1", "E2"]}],
        }
        self.assertTrue(any(x.startswith("colluding_source_independence") for x in adversarial.validate(payload)["errors"]))

    def test_manifest_and_test_methods_are_exactly_bound(self):
        manifest = json.loads((ROOT / "governance/release-mutation-contract.json").read_text(encoding="utf-8"))
        ids = {x["id"] for x in manifest["mutations"]}
        expected = {
            "remove_noncompensable_redline", "raise_action_ceiling", "expired_evidence_to_current",
            "synthetic_evidence_to_production", "delete_counterevidence", "generic_template_substitution",
            "auxiliary_domain_final_decision", "delete_consumer_rejection", "old_version_overwrite",
            "partial_failure_overall_pass", "manual_completion_tamper", "same_source_fake_independence",
        }
        self.assertEqual(ids, expected)
        for mutation_id in ids:
            self.assertTrue(hasattr(self, f"test_{mutation_id}_is_killed"), mutation_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
