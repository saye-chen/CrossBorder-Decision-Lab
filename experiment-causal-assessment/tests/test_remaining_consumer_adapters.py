from __future__ import annotations

import copy
import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

from domain_consumer_adapter import build_receipt, receipt_hash, validate_adapter, validate_receipt
from ecae_common import ECAEError, content_hash
from validate_consumer_migration import contract_for, load_default_migration


DOMAINS = ["D01", "D02", "D03", "D04", "D05", "D08", "D09", "D11", "D12", "D13"]


def adapter_path(domain_id: str) -> pathlib.Path:
    migration = load_default_migration()
    return REPO / contract_for(migration, domain_id)["skill"] / "integrations" / "experiment-causal-assessment" / "adapter.json"


def payload_for(fields: list[str]) -> dict:
    values = {
        "effect_estimate": "0.10",
        "effect_interval": {"lower": "0.05", "point": "0.10", "upper": "0.15"},
        "policy_value_interval": {"lower": "1", "point": "2", "upper": "3"},
        "policy_constraints": ["consent", "frequency_cap"],
    }
    return {field: values[field] for field in fields}


def handoff(domain_id: str, grade: str = "CE4", expires_at: str = "2026-09-10T00:00:00+08:00") -> dict:
    value = {
        "schema_version": "1.0.0", "object_id": f"ECAE-HANDOFF-{domain_id}-CONSUMER-FIXTURE", "object_version": "1.0.0",
        "status": "handed_off", "as_of_time": "2026-08-10T00:00:00+08:00", "owner": "ECAE",
        "created_at": "2026-08-10T00:00:00+08:00", "updated_at": "2026-08-10T00:00:00+08:00",
        "source_refs": [f"ECAE-RESULT-{domain_id}"], "lineage_refs": [f"ECAE-BUNDLE-{domain_id}"],
        "jurisdiction_refs": [], "parameter_refs": [], "assumption_refs": [], "limitations": ["fixture_non_production"],
        "producer": "ECAE", "consumer": domain_id, "causal_result_ref": f"ECAE-RESULT-{domain_id}", "estimand_ref": f"ECAE-ESTIMAND-{domain_id}",
        "causal_evidence_grade": grade, "claim_ceiling": grade,
        "allowed_actions": ["consider_within_consumer_decision_contract"],
        "prohibited_actions": ["automatic_external_write", "treat_as_final_business_decision", "upgrade_causal_grade"],
        "allowed_wording": ["qualified effect within bound scope"], "prohibited_wording": ["guaranteed", "automatic business action"],
        "applicability": {"population": f"authorized_{domain_id}_population", "platforms": ["Amazon-US"], "countries": ["US"], "time_window": "2026-08", "treatment_version": f"{domain_id}-T1"},
        "invalidation_triggers": ["treatment_changed"], "recompute_triggers": ["metric_definition_changed"],
        "expires_at": expires_at, "reproducibility_bundle_ref": f"ECAE-BUNDLE-{domain_id}", "review_status": "internal_reviewed",
        "business_owner_decision_required": True, "external_write": False, "content_hash": "PENDING",
    }
    value["content_hash"] = content_hash(value)
    return value


def context(domain_id: str, *, grade: str = "CE4", expires_at: str = "2026-09-10T00:00:00+08:00", payload: dict | None = None) -> dict:
    contract = contract_for(load_default_migration(), domain_id)
    requirement = contract["use_requirements"][0]
    return {
        "intended_use": requirement["use"], "handoff": handoff(domain_id, grade, expires_at),
        "as_of_time": "2026-08-15T00:00:00+08:00", "active_events": [],
        "target_context": {"platform": "Amazon-US", "country": "US", "population": f"authorized_{domain_id}_population", "treatment_version": f"{domain_id}-T1"},
        "consumer_payload": payload if payload is not None else payload_for(requirement["required_payload_fields"]),
    }


def accepted_migration(domain_id: str) -> dict:
    return copy.deepcopy(load_default_migration())


class RemainingConsumerAdapterTests(unittest.TestCase):
    def test_all_ten_consumer_owned_adapters_validate_and_stay_nonproduction(self):
        for domain_id in DOMAINS:
            path = adapter_path(domain_id)
            self.assertEqual(validate_adapter(path), [], domain_id)
            acceptance = json.loads(path.with_name("acceptance.json").read_text(encoding="utf-8"))
            self.assertTrue(acceptance["automated_contract_accepted"], domain_id)
            self.assertFalse(acceptance["production_dual_run_completed"], domain_id)
            self.assertFalse(acceptance["independent_owner_accepted"], domain_id)
            self.assertTrue(acceptance["controlled_pilot_owner_accepted"], domain_id)
            self.assertFalse(acceptance["external_write"], domain_id)

    def test_controlled_pilot_owner_acceptance_enables_bounded_domain_payload(self):
        for domain_id in DOMAINS:
            receipt = build_receipt(context(domain_id), adapter_path(domain_id))
            self.assertEqual(receipt["decision"], "accept", domain_id)
            self.assertEqual(receipt["qualified_payload_state"], "qualified", domain_id)
            self.assertIsNotNone(receipt["qualified_payload"], domain_id)
            self.assertTrue(receipt["downstream_use_allowed"], domain_id)

    def test_exact_owner_acceptance_enables_only_bounded_domain_use(self):
        for domain_id in DOMAINS:
            migration = accepted_migration(domain_id)
            receipt = build_receipt(context(domain_id), adapter_path(domain_id), migration=migration)
            self.assertEqual(validate_receipt(receipt, adapter_path(domain_id), migration=migration), [], domain_id)
            self.assertTrue(receipt["downstream_use_allowed"], domain_id)
            self.assertEqual(receipt["business_action_owner"], contract_for(migration, domain_id)["runtime_prefix"], domain_id)
            self.assertFalse(receipt["external_write"], domain_id)

    def test_low_grade_expiry_trigger_and_scope_mismatch_fail_closed(self):
        for domain_id in DOMAINS:
            low = build_receipt(context(domain_id, grade="CE2"), adapter_path(domain_id))
            self.assertEqual(low["decision"], "degrade", domain_id)
            self.assertFalse(low["downstream_use_allowed"], domain_id)
            expired = build_receipt(context(domain_id, expires_at="2026-08-14T00:00:00+08:00"), adapter_path(domain_id))
            self.assertEqual(expired["decision"], "request_recompute", domain_id)
            triggered = context(domain_id)
            triggered["active_events"] = ["treatment_changed"]
            receipt = build_receipt(triggered, adapter_path(domain_id))
            self.assertEqual(receipt["decision"], "request_recompute", domain_id)
            wrong_scope = context(domain_id)
            wrong_scope["target_context"]["country"] = "GB"
            receipt = build_receipt(wrong_scope, adapter_path(domain_id))
            self.assertEqual(receipt["decision"], "reject", domain_id)

    def test_required_payloads_are_domain_specific_and_never_zero_filled(self):
        for domain_id in ("D09", "D12", "D13"):
            receipt = build_receipt(context(domain_id, payload={}), adapter_path(domain_id))
            self.assertEqual(receipt["decision"], "reject", domain_id)
            self.assertIsNone(receipt["qualified_payload"], domain_id)
            self.assertEqual(receipt["qualified_payload_state"], "unknown", domain_id)

    def test_receipt_tampering_is_detected_for_every_domain(self):
        for domain_id in DOMAINS:
            receipt = build_receipt(context(domain_id), adapter_path(domain_id))
            receipt["downstream_use_allowed"] = False
            self.assertIn("receipt_hash:mismatch", validate_receipt(receipt, adapter_path(domain_id)), domain_id)

    def test_high_stakes_use_still_requires_independent_review(self):
        for domain_id in ("D01", "D03", "D09", "D12", "D13"):
            migration = load_default_migration()
            contract = contract_for(migration, domain_id)
            requirement = next(item for item in contract["use_requirements"] if item["requires_independent_review"])
            value = context(domain_id, grade="CE5", payload=payload_for(requirement["required_payload_fields"]))
            value["intended_use"] = requirement["use"]
            receipt = build_receipt(value, adapter_path(domain_id), migration=migration)
            self.assertEqual(receipt["decision"], "degrade", domain_id)
            self.assertFalse(receipt["downstream_use_allowed"], domain_id)


if __name__ == "__main__":
    unittest.main()
