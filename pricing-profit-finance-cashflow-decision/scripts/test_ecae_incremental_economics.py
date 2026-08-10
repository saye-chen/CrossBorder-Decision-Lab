#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(REPO / "experiment-causal-assessment" / "scripts"))

from calculate_incremental_economics import calculate
from ecae_common import content_hash
from ppfc_common import PPFCError, canonical_hash
from validate_consumer_migration import contract_for, load_default_migration
from validate_ecae_financial_handoff import build_receipt, validate_receipt


def snapshot(valid_until: str = "2026-09-10T00:00:00+08:00") -> dict:
    value = {"snapshot_id": "PPFC-PARAM-D06-FIXTURE", "currency": "USD", "unit_contribution_interval": {"lower": "8", "point": "10", "upper": "12"}, "valid_until": valid_until, "content_hash": "PENDING"}
    value["content_hash"] = canonical_hash({key: item for key, item in value.items() if key != "content_hash"})
    return value


def context(*, grade: str = "CE4", expires_at: str = "2026-09-10T00:00:00+08:00") -> dict:
    handoff = {
        "schema_version": "1.0.0", "object_id": "ECAE-HANDOFF-PPFC-FIXTURE", "object_version": "1.0.0", "status": "handed_off",
        "as_of_time": "2026-08-10T00:00:00+08:00", "owner": "ECAE", "created_at": "2026-08-10T00:00:00+08:00", "updated_at": "2026-08-10T00:00:00+08:00",
        "source_refs": ["ECAE-RESULT-PPFC"], "lineage_refs": ["ECAE-BUNDLE-PPFC"], "jurisdiction_refs": [], "parameter_refs": ["PPFC-PARAM-D06-FIXTURE"], "assumption_refs": [], "limitations": ["fixture_non_production"],
        "producer": "ECAE", "consumer": "D06", "causal_result_ref": "ECAE-RESULT-PPFC", "estimand_ref": "ECAE-ESTIMAND-PPFC",
        "causal_evidence_grade": grade, "claim_ceiling": grade, "allowed_actions": ["consider_within_consumer_decision_contract"],
        "prohibited_actions": ["automatic_external_write", "treat_as_final_business_decision", "upgrade_causal_grade"],
        "allowed_wording": ["qualified incremental effect"], "prohibited_wording": ["guaranteed financial return"],
        "applicability": {"population": "authorized_finance_v1", "platforms": ["Amazon-US"], "countries": ["US"], "time_window": "2026-08", "treatment_version": "PRICE-T1"},
        "invalidation_triggers": ["treatment_changed"], "recompute_triggers": ["cost_parameter_changed"], "expires_at": expires_at,
        "reproducibility_bundle_ref": "ECAE-BUNDLE-PPFC", "review_status": "internal_reviewed", "business_owner_decision_required": True,
        "external_write": False, "content_hash": "PENDING",
    }
    handoff["content_hash"] = content_hash(handoff)
    return {
        "intended_use": "incremental_economic_input", "handoff": handoff, "as_of_time": "2026-08-15T00:00:00+08:00", "active_events": [],
        "target_context": {"platform": "Amazon-US", "country": "US", "population": "authorized_finance_v1", "treatment_version": "PRICE-T1"},
        "consumer_payload": {"effect_estimate": "0.10", "effect_interval": {"lower": "0.05", "point": "0.10", "upper": "0.15"}, "economic_parameter_snapshot": snapshot()},
    }


def pending_owner_migration() -> dict:
    migration = copy.deepcopy(load_default_migration())
    contract = contract_for(migration, "D06")
    contract["acceptance"] = {
        "scope": "controlled_pilot_non_production",
        "status": "pending_consumer_owner",
        "consumer_owner_role": "D06_consumer_owner",
        "signed_record_ref": None,
        "accepted_uses": [],
        "conditions": [],
        "production_status": "not_executed",
        "production_signed_record_ref": None,
    }
    migration["completion_gate"]["all_controlled_pilot_consumer_acceptances_signed"] = False
    migration["completion_gate"]["wp11_controlled_pilot_complete"] = False
    return migration


class D06ECAEIncrementalEconomicsTests(unittest.TestCase):
    def test_pending_owner_keeps_incremental_inputs_unknown(self):
        migration = pending_owner_migration()
        receipt = build_receipt(context(), migration=migration)
        self.assertEqual(receipt["decision"], "hold_pending_consumer_acceptance")
        self.assertEqual(receipt["incremental_input_state"], "unknown")
        self.assertIsNone(receipt["effect_estimate"])
        result = calculate({"eligible_volume": "100", "costs": {}, "ecae_handoff_context": context()}, migration=migration)
        self.assertEqual(result["status"], "inconclusive")
        self.assertIsNone(result["incremental_economics"])

    def test_signed_receipt_enables_d06_incremental_economics_only(self):
        migration = load_default_migration()
        receipt = build_receipt(context(), migration=migration)
        self.assertEqual(validate_receipt(receipt, migration=migration), [])
        result = calculate({"eligible_volume": "100", "costs": {"implementation": "20", "opportunity": "5", "risk": "5"}, "ecae_financial_receipt": receipt}, migration=migration)
        self.assertEqual(result["net_value_interval"], {"lower": "10", "point": "70", "upper": "150"})
        self.assertTrue(result["causal_claim_allowed"])
        self.assertEqual(result["financial_decision_owner"], "PPFC")
        self.assertFalse(result["automatic_price_or_cash_action_allowed"])

    def test_low_grade_and_expired_handoff_never_zero_fill(self):
        low = build_receipt(context(grade="CE2"))
        self.assertEqual(low["incremental_input_state"], "unknown")
        expired = build_receipt(context(expires_at="2026-08-14T00:00:00+08:00"))
        self.assertEqual(expired["decision"], "request_recompute")
        self.assertIsNone(expired["effect_interval"])

    def test_expired_or_tampered_economic_snapshot_fails_closed_after_acceptance(self):
        migration = load_default_migration()
        expired = context()
        expired["consumer_payload"]["economic_parameter_snapshot"] = snapshot("2026-08-14T00:00:00+08:00")
        with self.assertRaisesRegex(ValueError, "expired"):
            build_receipt(expired, migration=migration)
        receipt = build_receipt(context(), migration=migration)
        receipt["effect_estimate"] = "999"
        self.assertIn("$.receipt_hash:mismatch", validate_receipt(receipt, migration=migration))
        with self.assertRaisesRegex(PPFCError, "invalid PPFC ECAE receipt"):
            calculate({"eligible_volume": "100", "costs": {}, "ecae_financial_receipt": receipt}, migration=migration)

    def test_bare_incremental_and_attribution_fields_cannot_enter_causal_economics(self):
        for field in ("effect_estimate", "effect_interval", "incremental_contribution"):
            with self.assertRaisesRegex(PPFCError, "bare causal or legacy"):
                calculate({"eligible_volume": "100", "costs": {}, field: "1"})
        with self.assertRaisesRegex(PPFCError, "bare causal or legacy"):
            calculate({"eligible_volume": "100", "costs": {}, "ROAS_ATTR_NET": "3" , "incremental_contribution": "9"})

    def test_noncausal_financial_scenario_is_explicit_and_never_incremental(self):
        result = calculate({
            "economics_mode": "noncausal_scenario", "noncausal_scenario_label": "planning sensitivity only", "eligible_volume": "100",
            "scenario_effect_interval": {"lower": "0.05", "point": "0.10", "upper": "0.15"},
            "scenario_economic_parameter_snapshot": {"currency": "USD", "unit_contribution_interval": {"lower": "8", "point": "10", "upper": "12"}},
            "costs": {"implementation": "30"},
        })
        self.assertEqual(result["scenario_type"], "noncausal_scenario")
        self.assertFalse(result["causal_claim_allowed"])
        self.assertIsNone(result["marketing_roi_incremental"])

    def test_noncausal_mode_requires_label_and_cannot_smuggle_receipt(self):
        base = {"economics_mode": "noncausal_scenario", "eligible_volume": "1", "scenario_effect_interval": {"lower": "0", "point": "0", "upper": "0"}, "scenario_economic_parameter_snapshot": {"currency": "USD", "unit_contribution_interval": {"lower": "0", "point": "0", "upper": "0"}}, "costs": {}}
        with self.assertRaisesRegex(PPFCError, "label"):
            calculate(base)
        with self.assertRaisesRegex(PPFCError, "cannot carry"):
            calculate({**base, "noncausal_scenario_label": "stress only", "ecae_financial_receipt": {}})


if __name__ == "__main__":
    unittest.main(verbosity=2)
