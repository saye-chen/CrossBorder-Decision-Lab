#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("checks", ROOT / "scripts/validate_input_evidence.py")
checks = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(checks)
AS_OF = "2026-08-05T00:00:00+00:00"


def evidence():
    return {"contract":"D05-EVIDENCE-DRAFT-1","evidence_id":"E-1","source_type":"official_rule","source_ref":"official:1","source_family":"issuer-a","authorization_ref":None,"object_ref":"O-1@v1","jurisdictions":["US"],"allowed_uses":["screening"],"obtained_at":"2026-08-01T00:00:00+00:00","verified_at":"2026-08-02T00:00:00+00:00","expires_at":"2026-09-01T00:00:00+00:00","content_hash":"a"*64,"supports_claims":["C-1"],"opposes_claims":[],"limitations":[],"state":"current"}


def rule():
    return {"contract":"D05-RULE-DRAFT-1","rule_id":"R-1","issuer":"Authority","source_ref":"official:rule","source_family":"authority","rule_version":"v1","jurisdictions":["US"],"scope":{"object_types":["product"],"uses":["sale"],"platforms":["amazon"]},"effective_at":"2026-01-01T00:00:00+00:00","verified_at":"2026-08-01T00:00:00+00:00","expires_at":"2026-09-01T00:00:00+00:00","supersedes":None,"refresh_trigger":"monthly","content_hash":"b"*64,"state":"current"}


def opinion():
    return {"contract":"D05-OPINION-RECEIPT-DRAFT-1","receipt_id":"OR-1","opinion_id":"OP-1","subject_role":"qualified counsel","issuer_identity_ref":"I-1","credential_scope":["product regulation"],"jurisdictions":["US"],"object_refs":["O-1@v1"],"allowed_uses":["market_access_review"],"conflict_of_interest":"none","basis_refs":["E-1"],"issued_at":"2026-08-01T00:00:00+00:00","verified_at":"2026-08-02T00:00:00+00:00","expires_at":"2026-09-01T00:00:00+00:00","limitations":[],"opinion_summary":"bounded review","source_evidence_ref":"E-OP-1","state":"accepted_as_bounded_evidence","claim_upgrade_allowed":False,"issued_by_d05":False}


class InputEvidenceTest(unittest.TestCase):
    def test_current_evidence_rule_and_opinion_pass(self):
        self.assertEqual(checks.validate_evidence(evidence(), AS_OF), [])
        self.assertEqual(checks.validate_rule(rule(), AS_OF), [])
        self.assertEqual(checks.validate_opinion(opinion(), AS_OF, "US", "O-1@v1", "market_access_review"), [])

    def test_expired_evidence_and_rule_fail_current(self):
        item = evidence(); item["expires_at"] = "2026-08-01T00:00:00+00:00"
        self.assertIn("expired evidence cannot be current", checks.validate_evidence(item, AS_OF))
        item = rule(); item["expires_at"] = "2026-08-01T00:00:00+00:00"
        self.assertIn("expired rule cannot be current", checks.validate_rule(item, AS_OF))

    def test_synthetic_fixture_cannot_support_production(self):
        item = evidence(); item["source_type"] = "synthetic_fixture"; item["allowed_uses"] = ["production_decision"]
        self.assertIn("synthetic evidence cannot support production decisions", checks.validate_evidence(item, AS_OF))

    def test_opinion_scope_and_conflict_are_fail_closed(self):
        item = opinion(); item["conflict_of_interest"] = "unresolved"
        errors = checks.validate_opinion(item, AS_OF, "DE", "O-2@v1", "tax_filing")
        self.assertTrue(any("jurisdiction mismatch" in e for e in errors), errors)
        self.assertTrue(any("object mismatch" in e for e in errors), errors)
        self.assertTrue(any("use mismatch" in e for e in errors), errors)
        self.assertTrue(any("conflict of interest" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
