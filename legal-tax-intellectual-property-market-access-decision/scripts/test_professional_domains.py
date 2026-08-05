#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("models", ROOT / "scripts/evaluate_professional_domains.py")
models = importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(models)


class ProfessionalDomainModelsTest(unittest.TestCase):
    def test_coverage_is_non_compensatory(self):
        required = ["model", "factory", "standard"]
        self.assertEqual(models.evaluate_coverage(required, required, [], []), "covered")
        self.assertEqual(models.evaluate_coverage(required, ["model", "standard"], ["factory"], []), "not_covered")
        self.assertEqual(models.evaluate_coverage(required, ["model", "standard"], [], ["factory"]), "partially_covered")

    def test_high_risk_claim_needs_direct_evidence_and_review(self):
        result = models.assess_claim(direct_evidence=True, object_match=True, scope_match=True, current=True, risk_tags=["medical"], professional_opinion=False)
        self.assertEqual(result["result"], "review_required")
        self.assertFalse(result["claim_upgrade_allowed"])
        result = models.assess_claim(direct_evidence=False, object_match=True, scope_match=True, current=True, risk_tags=[], professional_opinion=False)
        self.assertEqual(result["result"], "not_covered")

    def test_ip_tax_and_hs_never_become_confirmed_conclusions(self):
        for kind in ("ip_screening", "tax_customs", "customs_hs"):
            result = models.route_assessment(kind)
            self.assertEqual(result["result"], "review_required")
            self.assertFalse(result["confirmed_professional_conclusion"])

    def test_no_hit_is_only_screening(self):
        result = models.route_assessment("platform_access")
        self.assertEqual(result["result"], "screening_only")
        self.assertFalse(result["confirmed_professional_conclusion"])

    def test_certificate_requires_exact_critical_coverage(self):
        required = {"issuer":"A","holder":"B","standard":"S1","standard_version":"2026","model":"M1","bom_version":"B1","factory":"F1","sample_batch":"L1","jurisdiction":"US","use":"sale","validity":"current"}
        cert = dict(required); cert["factory"] = "F2"
        result = models.certificate_coverage(required, cert)
        self.assertEqual(result["result"], "not_covered")
        self.assertEqual(result["mismatched"], ["factory"])

    def test_transaction_chain_conflict_never_issues_tax_or_customs_conclusion(self):
        d={k:"x" for k in ("seller","buyer","importer","ship_from","ship_to","goods_flow","funds_flow","incoterm","valuation_basis","origin","hs_candidate","business_time")};d["declared_importer"]="other";r=models.assess_transaction_chain(d);self.assertEqual(r["result"],"inconclusive");self.assertFalse(r["tax_or_customs_conclusion_issued"])

    def test_claim_context_cannot_reuse_wrong_version_or_medium(self):
        d={"claim_id":"C1","text":"safe","language":"en","medium":"listing","audience":"adult","object_version":"v2","country":"US","platform":"Amazon","evidence_ids":["E1"],"valid_until":"2026-12-01","evidence_object_version":"v1","evidence_mediums":["packaging"]};r=models.assess_claim_context(d);self.assertEqual(r["result"],"not_covered");self.assertTrue(r["copy_rewrite_cannot_inherit_evidence"])


if __name__ == "__main__": unittest.main(verbosity=2)
