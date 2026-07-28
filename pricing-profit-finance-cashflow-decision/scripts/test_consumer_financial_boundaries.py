#!/usr/bin/env python3
from __future__ import annotations

import unittest

from evaluate_consumer_financial_boundaries import (
    logistics_financial_boundary,
    partnership_commission_boundary,
    promotion_financial_boundary,
    recoverable_contribution_boundary,
)
from ppfc_common import PPFCError


class ConsumerFinancialBoundaryTests(unittest.TestCase):
    def test_logistics_cost_and_contribution_boundary(self):
        result = logistics_financial_boundary({
            "purchase_price": "10", "main_haul": "2", "pick_pack": "1",
            "carrier_base": "3", "holding": "1", "selling_price": "20",
            "minimum_contribution": "2",
        })
        self.assertEqual(result["total_relevant_cost"], "17")
        self.assertEqual(result["contribution"], "3")

    def test_logistics_negative_contribution_blocks_financial_boundary(self):
        result = logistics_financial_boundary({
            "purchase_price": "8", "main_haul": "3", "carrier_base": "4",
            "selling_price": "10", "minimum_contribution": "1",
        })
        self.assertEqual(result["financial_status"], "blocked")

    def test_partnership_commission_boundary(self):
        result = partnership_commission_boundary({
            "mature_net_revenue": "1000", "commission_base": "900", "target_profit": "100",
            "non_commission_costs": [
                {"cost_id": "cogs", "amount": "400"},
                {"cost_id": "fulfillment", "amount": "100"},
            ],
        })
        self.assertEqual(result["available_for_commission"], "400")
        self.assertEqual(result["max_commission_rate"], "0.4444444444444444444444444444")

    def test_partnership_duplicate_cost_blocks(self):
        payload = {
            "mature_net_revenue": "100", "commission_base": "100", "target_profit": "0",
            "non_commission_costs": [
                {"cost_id": "same", "amount": "10"},
                {"cost_id": "same", "amount": "10"},
            ],
        }
        with self.assertRaises(PPFCError):
            partnership_commission_boundary(payload)

    def test_promotion_boundary_includes_nonincremental_and_losses(self):
        result = promotion_financial_boundary({
            "eligible": "200", "redeemed_orders": "100", "incremental_orders": "30",
            "merchant_discount_per_redeemed": "3", "gift_cost_per_redeemed": "1",
            "shipping_subsidy_per_redeemed": "0", "guarantee_cost": "10",
            "fraud_loss": "5", "service_cost": "5", "incremental_cm_per_order": "20",
            "pull_forward_loss": "20", "cannibalization_loss": "20", "fixed_cost": "40",
        })
        self.assertEqual(result["non_incremental_redeemed_orders"], "70")
        self.assertEqual(result["incremental_offer_contribution"], "100")

    def test_promotion_invalid_counts_block(self):
        with self.assertRaises(PPFCError):
            promotion_financial_boundary({
                "eligible": "1", "redeemed_orders": "1", "incremental_orders": "2",
                "merchant_discount_per_redeemed": "0", "gift_cost_per_redeemed": "0",
                "shipping_subsidy_per_redeemed": "0", "guarantee_cost": "0",
                "fraud_loss": "0", "service_cost": "0", "incremental_cm_per_order": "1",
                "pull_forward_loss": "0", "cannibalization_loss": "0", "fixed_cost": "0",
            })

    def test_recoverable_contribution_range(self):
        result = recoverable_contribution_boundary({
            "qualified_visits": "1000", "conversion_gap": "0.05", "recoverable_share": "0.5",
            "mature_contribution_per_order": {"low": "2", "high": "4"},
            "implementation_cost": "10",
        })
        self.assertEqual(result["recoverable_orders"], "25")
        self.assertEqual(result["contribution_range"], ["40", "90"])

    def test_recoverable_rate_over_one_blocks(self):
        with self.assertRaises(PPFCError):
            recoverable_contribution_boundary({
                "qualified_visits": "100", "conversion_gap": "1.1", "recoverable_share": "0.5",
                "mature_contribution_per_order": {"low": "2", "high": "4"},
            })


if __name__ == "__main__":
    unittest.main()
