#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from ppfc_common import PPFCError
from validate_localization_contract import validate_localization, validate_migration


def localization() -> dict:
    return {
        "contract": "F02-temporary-localization-contract-v1", "localization_id": "loc-us-1",
        "version": "F02-TEMP-2026.07", "country_code": "US", "platform_id": "fixture",
        "currency_code": "USD",
        "fx": {"source": "authorized:fx", "rate": "1", "base_currency": "USD", "quote_currency": "USD", "verified_at": "2026-07-28T00:00:00Z", "valid_until": "2026-08-28T00:00:00Z"},
        "tax": {"basis": "tax_exclusive_revenue", "inclusive": False, "source": "official:tax", "verified_at": "2026-07-28T00:00:00Z", "valid_until": "2026-08-28T00:00:00Z"},
        "unit_system": "imperial", "time_zone": "America/Los_Angeles",
        "settlement_calendar": {"calendar_id": "cal-1", "settlement_days": 7, "cutoff_time": "23:59"},
        "dynamic_rule": {"source": "contract:store-1", "effective_at": "2026-07-01T00:00:00Z", "expires_at": "2026-08-28T00:00:00Z", "refresh_trigger": ["expiry", "fee_schedule_change"], "supersedes_rule_id": None, "rollback_rule_id": "rule-default"},
        "localization_status": "validated", "evidence_grade": "E4", "action_ceiling": "reversible_action",
        "validity": {"valid_from": "2026-07-01T00:00:00Z", "valid_until": "2026-08-28T00:00:00Z", "recorded_at": "2026-07-28T01:00:00Z"},
        "lineage": {"input_hash": "sha256:abc", "runtime_version": "PPFC-2026.07", "evidence_ids": ["E1"]},
        "external_write": False,
    }


def migration() -> dict:
    return {
        "migration_id": "mig-1", "source_contract": "F02-temporary-localization-contract-v1",
        "target_contract": "F02-CONTRACT-2027.01", "state": "dual_run",
        "field_mappings": [{"source_field": "country_code", "target_field": "market.country", "transform": "identity", "loss": "none"}],
        "dual_run": {"same_input_hash": "sha256:abc", "source_result_hash": "sha256:same", "target_result_hash": "sha256:same"},
        "differences": [], "acceptance": {"accepted": False, "accepted_by": None, "accepted_at": None},
        "rollback": {"supported": True, "deadline": "2027-03-01T00:00:00Z", "source_readable": True},
        "lineage": {"input_hash": "sha256:abc", "runtime_version": "PPFC-2026.07"},
    }


class LocalizationTests(unittest.TestCase):
    def test_current_contract(self):
        self.assertEqual(validate_localization(localization())["effective_status"], "validated")

    def test_expired_fx_forces_recompute(self):
        payload = localization(); payload["action_ceiling"] = "analysis_only"
        result = validate_localization(payload, "2026-09-01T00:00:00Z")
        self.assertEqual(result["effective_status"], "expired")
        self.assertIn("fx", result["expired_components"])

    def test_expired_contract_cannot_keep_execution_ceiling(self):
        with self.assertRaises(PPFCError):
            validate_localization(localization(), "2026-09-01T00:00:00Z")

    def test_tax_basis_conflict(self):
        payload = localization(); payload["tax"]["inclusive"] = True
        with self.assertRaises(PPFCError): validate_localization(payload)

    def test_unknown_timezone_and_external_write(self):
        for key, value in (("time_zone", "Mars/Olympus"), ("external_write", True)):
            payload = localization(); payload[key] = value
            with self.assertRaises(PPFCError): validate_localization(payload)

    def test_low_evidence_downgrades(self):
        payload = localization(); payload["evidence_grade"] = "E1"
        with self.assertRaises(PPFCError): validate_localization(payload)

    def test_dual_run_before_acceptance(self):
        self.assertFalse(validate_migration(migration())["cutover_allowed"])

    def test_safe_cutover(self):
        payload = migration(); payload["state"] = "cutover_ready"
        payload["acceptance"] = {"accepted": True, "accepted_by": "finance-owner", "accepted_at": "2027-01-10T00:00:00Z"}
        self.assertTrue(validate_migration(payload)["cutover_allowed"])

    def test_material_loss_and_unexplained_difference_block_cutover(self):
        for mutate in (
            lambda p: p["field_mappings"][0].update(loss="material"),
            lambda p: p["dual_run"].update(target_result_hash="sha256:different"),
        ):
            payload = copy.deepcopy(migration()); payload["state"] = "cutover_ready"
            payload["acceptance"] = {"accepted": True, "accepted_by": "owner", "accepted_at": "2027-01-10T00:00:00Z"}
            mutate(payload)
            with self.assertRaises(PPFCError): validate_migration(payload)

    def test_input_hash_and_rollback_fail_closed(self):
        for mutate in (
            lambda p: p["lineage"].update(input_hash="sha256:other"),
            lambda p: p["rollback"].update(source_readable=False),
        ):
            payload = copy.deepcopy(migration()); mutate(payload)
            with self.assertRaises(PPFCError): validate_migration(payload)


if __name__ == "__main__":
    unittest.main()
