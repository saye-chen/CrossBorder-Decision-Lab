#!/usr/bin/env python3
"""WP5 D03-D06 compatibility and selective recomputation tests."""
from __future__ import annotations
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


impact = load("pipm_impact", Path(__file__).with_name("compute_product_change_impact.py"))
contract = load("pipm_xdomain", Path(__file__).with_name("validate_cross_domain_envelope.py"))


def envelope(sender="product-innovation-product-management", receiver="pricing-profit-finance-cashflow-decision"):
    claims = [
        {"claim_id": "C-COST", "field": "target_unit_cost", "value": "12.50"},
        {"claim_id": "C-PACK", "field": "packaging_dimensions", "value": "20x10x5cm"},
    ]
    return {
        "contract": "PIPM-XDOMAIN-2026.07",
        "message_id": "M-001",
        "message_version": "PIPM-XMSG-2026.07",
        "correlation_id": "COR-001",
        "idempotency_key": "idem-0001",
        "sender": sender,
        "receiver": receiver,
        "object_ref": {"object_id": "P-1", "object_version": "v3", "object_type": "market_product"},
        "scope": {"country": "US", "platform": "Amazon", "currency": "USD", "tax_basis": "tax_exclusive", "as_of_time": "2026-07-28T00:00:00Z"},
        "payload_type": "recompute_request",
        "status": "proposed",
        "claims": claims,
        "claim_acceptance": [],
        "changed_fields": ["target_unit_cost"],
        "recomputation": {"status": "complete", "changed_fields": ["target_unit_cost"], "recompute_fields": ["contribution_margin"], "preserved_fields": ["packaging_dimensions"], "expired_claim_ids": ["C-COST"], "reaccept_claim_ids": ["C-COST"], "blocked_reason": None},
        "allowed_uses": ["decision_support", "selective_recomputation"],
        "forbidden_uses": ["external_write", "change_price", "release_funds", "place_order", "publish_listing"],
        "external_write": False,
        "validity": {"valid_from": "2026-07-28T00:00:00Z", "valid_to": None, "recorded_at": "2026-07-28T00:01:00Z"},
        "lineage": {"input_hash": "sha256:abc", "parameter_snapshot_id": "PS-1", "runtime_version": "PIPM-2026.07", "supersedes": None},
    }


class WP5Tests(unittest.TestCase):
    def test_d03_to_d06_recompute_request(self):
        self.assertTrue(contract.validate(envelope())["valid"])

    def test_d06_constraint_and_partial_claim_acceptance(self):
        value = envelope("pricing-profit-finance-cashflow-decision", "product-innovation-product-management")
        value["payload_type"] = "acceptance"
        value["lineage"]["runtime_version"] = "PPFC-2026.07"
        value["claim_acceptance"] = [
            {"claim_id": "C-COST", "decision": "accepted", "reason": None},
            {"claim_id": "C-PACK", "decision": "rejected", "reason": "dimension basis stale"},
        ]
        result = contract.validate(value)
        self.assertEqual(result["accepted_claim_ids"], ["C-COST"])
        self.assertEqual(result["rejected_claim_ids"], ["C-PACK"])

    def test_identity_currency_tax_time_and_version_mismatch_block(self):
        mutations = [
            ("object_ref", "object_version", ""),
            ("scope", "currency", "usd"),
            ("scope", "tax_basis", ""),
            ("scope", "as_of_time", "not-time"),
            (None, "message_version", "PIPM-XMSG-2025.01"),
        ]
        for section, key, bad in mutations:
            value = envelope()
            (value if section is None else value[section])[key] = bad
            with self.assertRaises(contract.ContractError):
                contract.validate(value)

    def test_idempotent_retry_is_noop(self):
        seen = set()
        self.assertFalse(contract.validate(envelope(), seen)["duplicate"])
        result = contract.validate(envelope(), seen)
        self.assertTrue(result["duplicate"])
        self.assertEqual(result["effect"], "no_op")

    def test_selective_recompute_preserves_unaffected_claims(self):
        result = impact.compute({
            "changed_fields": ["target_unit_cost"],
            "all_fields": ["target_unit_cost", "contribution_margin", "cash_peak", "packaging_dimensions"],
            "dependencies": {"target_unit_cost": ["contribution_margin"], "contribution_margin": ["cash_peak"]},
            "claim_fields": {"C1": "contribution_margin", "C2": "packaging_dimensions"},
            "rejected_claim_ids": [],
        })
        self.assertEqual(result["recompute_fields"], ["cash_peak", "contribution_margin"])
        self.assertEqual(result["preserved_fields"], ["packaging_dimensions"])
        self.assertEqual(result["expired_claim_ids"], ["C1"])

    def test_cycle_blocks(self):
        with self.assertRaises(impact.ImpactError):
            impact.compute({"changed_fields": ["a"], "all_fields": ["a", "b"], "dependencies": {"a": ["b"], "b": ["a"]}})

    def test_legacy_ppfc_contract_is_unchanged_and_still_passes(self):
        schema = json.loads((ROOT / "pricing-profit-finance-cashflow-decision/schemas/cross-domain-envelope.schema.json").read_text())
        self.assertEqual(schema["properties"]["contract"]["const"], "PPFC-XDOMAIN-2026.07")
        test = subprocess.run([sys.executable, str(ROOT / "pricing-profit-finance-cashflow-decision/scripts/test_cross_domain_contract.py")], capture_output=True, text=True)
        self.assertEqual(test.returncode, 0, (test.stdout, test.stderr))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(WP5Tests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
