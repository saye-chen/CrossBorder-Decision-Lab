#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from evaluate_mixed_batch_scenario import evaluate, sample_target
from ppfc_common import PPFCError


def scenario() -> dict:
    channels = ["shelf", "ads", "creator", "video", "live"]
    return {
        "scenario_id": "mixed-10pct", "currency": "USD",
        "batch": {"batch_id": "b1", "initial_quantity": 100, "sample": 10, "test": 5, "initial_defect": 2, "after_sales_reserve": 3, "safety_stock": 10, "sellable_open": 70},
        "sample_policy": {"rate": "0.10", "rounding": "half_up", "minimum": 1, "maximum": 20, "posted": 8, "rights_verified": 8},
        "orders": [{"order_id": "o1", "gross_revenue": "100", "refund": "0", "paid": True, "fulfilled_units": 2}],
        "channel_claims": [{"order_id": "o1", "channel": channel, "claimed_revenue": "100", "attribution_weight": "0.2"} for channel in channels],
        "costs": [
            {"deduplication_key": "proc-1", "category": "cogs", "amount": "40"},
            {"deduplication_key": "sample-1", "category": "sample_landed", "amount": "10"},
            {"deduplication_key": "ad-1", "category": "paid_amplification", "amount": "15"},
        ],
        "cash_events": [
            {"event_id": "c1", "occurred_at": "2026-07-01T00:00:00Z", "amount": "-120"},
            {"event_id": "c2", "occurred_at": "2026-08-01T00:00:00Z", "amount": "150"},
        ],
        "ending_inventory_nrv": "20", "cash_limit": "150", "incrementality_status": "attributed_only",
    }


class MixedBatchEconomicsTests(unittest.TestCase):
    def test_complete_five_touchpoint_batch(self):
        result = evaluate(scenario())
        self.assertEqual((result["sample_target"], result["unique_orders"]), (10, 1))
        self.assertEqual(result["raw_claimed_revenue"], "500")
        self.assertEqual(result["unique_net_revenue"], "100")
        self.assertEqual(result["allocated_attributed_revenue"], "100")
        self.assertIsNone(result["incremental_contribution"])

    def test_sample_rate_increase_never_increases_sellable_capacity(self):
        base = scenario()
        for rate, expected in (("0.10", 10), ("0.15", 15), ("0.333", 20)):
            policy = copy.deepcopy(base["sample_policy"]); policy["rate"] = rate
            self.assertEqual(sample_target(100, policy), expected)
        self.assertGreaterEqual(100 - 10, 100 - 15)

    def test_capacity_violation_blocks(self):
        payload = scenario(); payload["batch"]["sellable_open"] = 71
        with self.assertRaisesRegex(PPFCError, "CAPACITY"): evaluate(payload)

    def test_five_claims_do_not_multiply_financial_revenue(self):
        result = evaluate(scenario())
        self.assertEqual(result["unique_net_revenue"], "100")
        self.assertNotEqual(result["raw_claimed_revenue"], result["unique_net_revenue"])

    def test_attribution_weights_must_reconcile(self):
        payload = scenario(); payload["channel_claims"][0]["attribution_weight"] = "0.3"
        with self.assertRaisesRegex(PPFCError, "WEIGHTS"): evaluate(payload)

    def test_duplicate_marketing_cost_is_idempotent(self):
        payload = scenario(); payload["costs"].append(copy.deepcopy(payload["costs"][-1]))
        self.assertEqual(evaluate(payload)["deduplicated_total_cost"], evaluate(scenario())["deduplicated_total_cost"])

    def test_conflicting_duplicate_cost_blocks(self):
        payload = scenario(); duplicate = copy.deepcopy(payload["costs"][-1]); duplicate["amount"] = "16"; payload["costs"].append(duplicate)
        with self.assertRaisesRegex(PPFCError, "CONFLICTING_DUPLICATE_COST"): evaluate(payload)

    def test_zero_post_blocks_paid_amplification(self):
        payload = scenario(); payload["sample_policy"]["posted"] = 0; payload["sample_policy"]["rights_verified"] = 0
        self.assertIn("NO_POSTED_CONTENT_FOR_AMPLIFICATION", evaluate(payload)["blockers"])

    def test_missing_rights_blocks_paid_amplification(self):
        payload = scenario(); payload["sample_policy"]["rights_verified"] = 7
        self.assertIn("CONTENT_RIGHTS_NOT_VERIFIED", evaluate(payload)["blockers"])

    def test_live_fulfillment_cannot_exceed_atp(self):
        payload = scenario(); payload["orders"][0]["fulfilled_units"] = 71
        with self.assertRaisesRegex(PPFCError, "ATP"): evaluate(payload)

    def test_positive_profit_does_not_override_cash_limit(self):
        payload = scenario(); payload["cash_limit"] = "100"
        result = evaluate(payload)
        self.assertGreater(float(result["batch_economic_profit"]), 0)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("CASH_LIMIT_EXCEEDED", result["blockers"])

    def test_cash_event_order_changes_peak_not_total(self):
        first = evaluate(scenario())
        payload = scenario()
        payload["cash_events"][0]["occurred_at"] = "2026-09-01T00:00:00Z"
        second = evaluate(payload)
        self.assertEqual(first["batch_cash_result"], second["batch_cash_result"])
        self.assertNotEqual(first["peak_funding_required"], second["peak_funding_required"])

    def test_refund_reduces_revenue_and_profit(self):
        base = evaluate(scenario())
        payload = scenario(); payload["orders"][0]["refund"] = "20"
        for claim in payload["channel_claims"]: claim["claimed_revenue"] = "80"
        result = evaluate(payload)
        self.assertLess(float(result["batch_economic_profit"]), float(base["batch_economic_profit"]))

    def test_partial_channel_failure_preserves_valid_financial_ledger(self):
        payload = scenario()
        payload["channel_claims"] = [claim for claim in payload["channel_claims"] if claim["channel"] != "live"]
        for claim in payload["channel_claims"]: claim["attribution_weight"] = "0.25"
        result = evaluate(payload)
        self.assertEqual(result["unique_orders"], 1)
        self.assertEqual(result["unique_net_revenue"], "100")


if __name__ == "__main__": unittest.main()
