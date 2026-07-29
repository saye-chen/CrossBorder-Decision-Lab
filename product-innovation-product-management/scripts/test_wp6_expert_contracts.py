#!/usr/bin/env python3
"""Fifteen expert-grade WP6 failure, adversarial and migration assertions."""
from __future__ import annotations
import copy
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


validator = load("wp6_validator", "validate_wp6_contracts.py")
migrator = load("wp6_migrator", "evaluate_temporary_contract_migration.py")


def good() -> dict:
    obj = {"object_id": "P-1", "object_version": "v3"}
    return {
        "d04": {
            "contract": "PIPM-D04-TEMP-2026.07", "handoff_id": "H4", "object_ref": {**obj, "object_type": "market_product", "sample_batch_id": "B-1"},
            "bom_version": "BOM-3", "packaging_version": "PKG-2", "status": "proposed",
            "specifications": [
                {"field_id": "weight", "nominal": "500", "lsl": "490", "usl": "510", "unit": "g", "measurement_method": "calibrated_scale", "method_version": "M1", "owner_domain": "product-innovation-product-management", "criticality": "major", "depends_on": [], "evidence_ids": ["E1"], "state": "proposed"},
                {"field_id": "drop_survival", "nominal": "1", "lsl": "1", "usl": "1", "unit": "boolean", "measurement_method": "drop_protocol", "method_version": "M2", "owner_domain": "product-innovation-product-management", "criticality": "safety_critical", "depends_on": ["weight"], "evidence_ids": ["E2"], "state": "proposed"}
            ],
            "ctqs": [{"ctq_id": "CTQ-1", "source": "hazard analysis", "failure_effect": "injury", "sample_plan": "request:D04-plan", "acceptance_rule": "zero critical failure", "measurement_system_status": "requested", "state": "proposed"}],
            "materials": [{"material_id": "MAT-1", "version": "2", "substitution": "candidate", "revalidation_scope": ["drop_survival", "market_access"]}],
            "reliability_requests": [{"mission_profile": "normal use", "status": "requested"}], "open_questions": ["process capability"], "blocked_actions": ["mass_production_release"], "preserved_results": ["user_need"], "external_write": False
        },
        "d05": {
            "contract": "PIPM-D05-TEMP-2026.07", "request_id": "H5", "object_ref": obj,
            "scope": {"jurisdiction": "US", "country": "US", "platform": "Amazon", "sales_model": "marketplace", "business_time": "2026-07-28T00:00:00Z"},
            "status": "proposed", "intended_use": "consumer storage", "foreseeable_misuse": ["child access"], "users": {"age_scope": "adult", "contact_scenarios": ["skin"]},
            "product_facts": {"materials": ["MAT-1"], "energy": "none", "connectivity": "none", "packaging": "PKG-2"},
            "claims": [{"claim_id": "CL-1", "text": "durable", "language": "en-US", "medium": "listing", "object_version": "v3", "evidence_ids": ["E2"], "state": "proposed", "allowed_uses": ["professional_review"]}],
            "review_questions": [{"question_id": "Q-1", "topic": "market_access", "source_ref": "official:rule", "rule_version": "2026-01", "verified_at": "2026-07-28T00:00:00Z", "expires_at": "2026-12-31T00:00:00Z", "state": "proposed"}],
            "blocked_actions": ["market_release"], "external_write": False
        },
        "opinion": {
            "opinion_id": "O-1", "evidence_type": "professional_opinion", "subject_role": "authorized reviewer", "credential_scope": ["market_access"], "jurisdictions": ["US"], "conflict_of_interest": "none", "basis_refs": ["official:rule"], "issued_at": "2026-07-28T00:00:00Z", "verified_at": "2026-07-28T01:00:00Z", "expires_at": "2026-12-31T00:00:00Z", "object_ref": obj, "opinion_state": "accepted_as_evidence", "claim_upgrade_allowed": False, "limitations": ["not legal conclusion"]
        },
        "localization": {
            "profile_id": "L-1", "object_ref": obj, "country": "US", "platform": "Amazon", "locale": "en-US", "status": "proposed",
            "market_facts": [{"item_id": "LF-1", "topic": "measurement_unit", "value_state": "observed", "source_ref": "authorized:research", "verified_at": "2026-07-28T00:00:00Z", "expires_at": "2026-12-31T00:00:00Z", "refresh_trigger": "policy_or_market_change", "owner_domain": "product-innovation-product-management", "state": "proposed"}],
            "adaptation_requirements": [{"item_id": "LA-1", "topic": "instructions", "value_state": "observed", "source_ref": "authorized:test", "verified_at": "2026-07-28T00:00:00Z", "expires_at": "2026-12-31T00:00:00Z", "refresh_trigger": "product_change", "owner_domain": "product-innovation-product-management", "state": "proposed"}],
            "cultural_usage_hypotheses": [{"item_id": "LH-1", "topic": "usage_context", "value_state": "unknown", "source_ref": None, "verified_at": None, "expires_at": None, "refresh_trigger": "local_user_test", "owner_domain": "product-innovation-product-management", "state": "inconclusive"}],
            "regulated_policy_questions": [{"item_id": "LR-1", "topic": "warning", "value_state": "unknown", "source_ref": None, "verified_at": None, "expires_at": None, "refresh_trigger": "D05_review", "owner_domain": "future-d05", "state": "blocked"}],
            "translation_complete": True, "localization_complete": False, "evidence_gaps": ["local usage validation", "D05 warning review"], "blocked_actions": ["market_release"]
        },
        "migration": {
            "migration_id": "MG-1", "temporary_contract": "PIPM-D05-TEMP-2026.07", "formal_contract": "D05-FUTURE-1", "snapshot_id": "S-1", "object_version": "v3",
            "mappings": [{"source_field": "claims", "target_field": "claims", "classification": "lossless", "criticality": "safety_critical"}],
            "consumer_acceptance": [{"consumer": "product-innovation-product-management", "status": "accepted"}], "rollback_deadline": "2026-12-31T00:00:00Z", "legacy_read_preserved": True
        }
    }


class WP6ExpertTests(unittest.TestCase):
    def assertBlocked(self, payload: dict, marker: str):
        errors = validator.validate(payload)
        self.assertTrue(any(marker in x for x in errors), errors)

    def test_01_valid_expert_package(self):
        self.assertEqual(validator.validate(good()), [])

    def test_02_inverted_tolerance_blocks(self):
        x = good(); x["d04"]["specifications"][0].update(lsl="520", usl="510")
        self.assertBlocked(x, "inverted_limits")

    def test_03_safety_tail_without_evidence_blocks(self):
        x = good(); x["d04"]["specifications"][1]["evidence_ids"] = []
        self.assertBlocked(x, "safety_ctq_without_evidence")

    def test_04_bom_or_batch_drift_blocks_version_merge(self):
        x = good(); x["d05"]["object_ref"]["object_version"] = "v2"
        self.assertBlocked(x, "object_version_mismatch")

    def test_05_material_substitution_requires_revalidation(self):
        x = good(); x["d04"]["materials"][0]["revalidation_scope"] = []
        self.assertBlocked(x, "substitution_without_revalidation")

    def test_06_unsupported_claim_cannot_be_used(self):
        x = good(); x["d05"]["claims"][0]["evidence_ids"] = []
        self.assertBlocked(x, "unsupported_claim_has_allowed_use")

    def test_07_professional_opinion_scope_and_jurisdiction(self):
        x = good(); x["opinion"]["credential_scope"] = ["tax"]; x["opinion"]["jurisdictions"] = ["EU"]
        errors = validator.validate(x)
        self.assertTrue(any("outside_credential_scope" in e for e in errors))
        self.assertTrue(any("jurisdiction_mismatch" in e for e in errors))

    def test_08_undisclosed_conflict_blocks(self):
        x = good(); x["opinion"]["conflict_of_interest"] = "undisclosed"
        self.assertBlocked(x, "undisclosed_conflict")

    def test_09_expired_opinion_and_rule_block(self):
        x = good(); x["opinion"]["expires_at"] = "2026-07-01T00:00:00Z"; x["d05"]["review_questions"][0]["expires_at"] = "2026-07-01T00:00:00Z"
        errors = validator.validate(x)
        self.assertTrue(any("expired_not_marked" in e for e in errors))
        self.assertTrue(any("expired_rule_not_blocked" in e for e in errors))

    def test_10_dynamic_rule_without_provenance_blocks(self):
        x = good(); x["d05"]["review_questions"][0].update(source_ref=None, rule_version=None, verified_at=None)
        self.assertBlocked(x, "dynamic_rule_without_provenance")

    def test_11_unknown_market_must_degrade(self):
        x = good(); x["localization"].update(country="ZZ", platform="unknown", status="proposed")
        self.assertBlocked(x, "unknown_market_must_block")

    def test_12_translation_cannot_equal_localization(self):
        x = good()
        for key in ("market_facts", "adaptation_requirements", "cultural_usage_hypotheses", "regulated_policy_questions"):
            x["localization"][key] = []
        self.assertBlocked(x, "translation_is_not_localization")

    def test_13_dependency_cycle_and_orphan_block(self):
        x = good(); x["d04"]["specifications"][0]["depends_on"] = ["drop_survival"]; x["d04"]["specifications"][1]["depends_on"] = ["missing", "weight"]
        errors = validator.validate(x)
        self.assertTrue(any("dependency_cycle" in e for e in errors))
        self.assertTrue(any("orphan_dependency" in e for e in errors))

    def test_14_lossy_critical_migration_rolls_back(self):
        x = good(); x["migration"]["mappings"][0]["classification"] = "lossy"
        self.assertBlocked(x, "critical_not_lossless")
        result = migrator.evaluate({"mappings": x["migration"]["mappings"], "differences": [{"source_field": "claims"}], "consumer_acceptance": x["migration"]["consumer_acceptance"], "legacy_read_preserved": True, "temporary_snapshot_id": "S-1", "formal_snapshot_id": "S-1"})
        self.assertEqual(result["status"], "rollback")

    def test_15_consumer_rejection_snapshot_mismatch_and_legacy_removal_rollback(self):
        x = good()["migration"]
        result = migrator.evaluate({"mappings": x["mappings"], "differences": [], "consumer_acceptance": [{"consumer": "D03", "status": "rejected"}], "legacy_read_preserved": False, "temporary_snapshot_id": "S-1", "formal_snapshot_id": "S-2"})
        self.assertEqual(result["status"], "rollback")
        self.assertEqual(set(result["blockers"]), {"consumer_acceptance_open", "legacy_read_not_preserved", "snapshot_mismatch"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
