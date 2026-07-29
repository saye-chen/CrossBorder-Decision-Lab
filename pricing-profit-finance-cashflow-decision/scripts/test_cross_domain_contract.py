#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from ppfc_common import PPFCError
from validate_cross_domain_envelope import validate


def fixture() -> dict:
    return {
        "contract": "PPFC-XDOMAIN-2026.07", "message_id": "m1",
        "message_version": "PPFC-XMSG-2026.07", "correlation_id": "c1",
        "idempotency_key": "idem-0001", "sender": "pricing-profit-finance-cashflow-decision",
        "receiver": "advertising-analysis-measurement-optimization",
        "object_ref": {"object_id": "batch-1", "object_version": "v1", "object_type": "batch"},
        "scope": {"country": "US", "platform": "TikTok Shop", "currency": "USD", "tax_basis": "tax_exclusive", "as_of_time": "2026-07-28T10:00:00+08:00"},
        "payload_type": "economic_constraint", "status": "proposed",
        "claims": [{"claim": "break_even_roas", "value": "1.80"}], "evidence_ids": ["E1"],
        "calculations": [{"id": "CAL1", "input_hash": "sha256:abc"}],
        "allowed_uses": ["decision_support"], "forbidden_uses": sorted({"external_write", "change_price", "change_budget", "place_order", "send_sample", "sign_contract", "release_funds"}),
        "blocked_actions": [], "accepted_by_receiver": False,
        "validity": {"valid_from": "2026-07-28T09:00:00+08:00", "valid_to": "2026-08-01T09:00:00+08:00", "recorded_at": "2026-07-28T10:00:00+08:00"},
        "lineage": {"input_hash": "sha256:abc", "output_hash": "sha256:def", "parameter_snapshot_id": "ps-1", "runtime_version": "PPFC-2026.07", "supersedes": None},
    }


class CrossDomainContractTests(unittest.TestCase):
    def test_valid_proposed_constraint(self):
        self.assertEqual(validate(fixture())["action_ceiling"], "controlled_test")

    def test_cannot_self_accept(self):
        payload = fixture(); payload["accepted_by_receiver"] = True
        with self.assertRaises(PPFCError): validate(payload)

    def test_cannot_authorize_external_action(self):
        payload = fixture(); payload["forbidden_uses"].remove("change_price")
        with self.assertRaises(PPFCError): validate(payload)

    def test_ppfc_cannot_claim_validated_outbound(self):
        payload = fixture(); payload["status"] = "validated"
        with self.assertRaises(PPFCError): validate(payload)

    def test_ppfc_cannot_accept_for_domain(self):
        payload = fixture(); payload["payload_type"] = "acceptance"
        with self.assertRaises(PPFCError): validate(payload)

    def test_partial_failure_retains_analysis_only(self):
        payload = fixture(); payload["status"] = "inconclusive"; payload["blocked_actions"] = ["change_budget"]
        self.assertEqual(validate(payload)["action_ceiling"], "analysis_only")

    def test_identity_and_time_fail_closed(self):
        for mutate in (
            lambda p: p["object_ref"].pop("object_version"),
            lambda p: p["validity"].update(valid_to="2026-07-01T00:00:00Z"),
            lambda p: p.update(receiver=p["sender"]),
        ):
            payload = copy.deepcopy(fixture()); mutate(payload)
            with self.assertRaises(PPFCError): validate(payload)


if __name__ == "__main__":
    unittest.main()
