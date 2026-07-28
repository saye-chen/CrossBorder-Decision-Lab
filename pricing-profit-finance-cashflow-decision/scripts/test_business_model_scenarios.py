#!/usr/bin/env python3
from __future__ import annotations

import unittest

from evaluate_business_model_scenario import (
    b2b_terms,
    bundle_incremental,
    cac_boundaries,
    causal_ceiling,
    joint_stress,
    marginal_scale,
    net_recovery_value,
    preorder_gate,
    spreadsheet_value,
    subscription_economics,
)
from ppfc_common import PPFCError


class BusinessModelScenarioTests(unittest.TestCase):
    def test_average_profit_cannot_override_negative_marginal(self):
        result = marginal_scale([
            {"spend": "100", "contribution": "60"},
            {"spend": "200", "contribution": "50"},
        ])
        self.assertEqual(result["status"], "blocked_negative_marginal")
        self.assertEqual(result["steps"][0]["marginal_contribution"], "-10")

    def test_attribution_without_causal_evidence_stays_proposed(self):
        result = causal_ceiling("E5", "100")
        self.assertEqual(result["status"], "proposed")
        self.assertIsNone(result["incremental_value"])

    def test_accepted_causal_evidence_can_report_incremental_value(self):
        result = causal_ceiling("E6", "100")
        self.assertEqual(result["incremental_value"], "100")

    def test_markdown_uses_nrv_not_book_cost(self):
        self.assertEqual(net_recovery_value("60", "10", "5"), "45")

    def test_b2b_terms_include_bad_debt_and_financing(self):
        result = b2b_terms("1000", "600", "0.05", "20")
        self.assertEqual(result, {"bad_debt": "50", "contribution": "330"})

    def test_subscription_clv_includes_retention_and_cac(self):
        result = subscription_economics("20", "10", "0.5", 3, "25")
        self.assertEqual(result["contribution_clv"], "27.5")
        self.assertEqual(result["net_after_cac"], "2.5")

    def test_bundle_cannibalization_is_deducted(self):
        result = bundle_incremental("100", "50", "30", True)
        self.assertEqual(result["incremental_contribution"], "20")

    def test_bundle_without_incremental_evidence_is_only_proposed(self):
        result = bundle_incremental("100", "50", "0", False)
        self.assertEqual(result["status"], "proposed")
        self.assertIsNone(result["incremental_contribution"])

    def test_preorder_missing_refund_liability_blocks(self):
        self.assertEqual(preorder_gate("100", "60", None, True)["status"], "blocked")

    def test_preorder_delivery_and_refund_liability_are_reserved(self):
        result = preorder_gate("100", "60", "20", True)
        self.assertEqual(result["net_cash_after_liability"], "20")

    def test_first_order_and_lifetime_cac_are_not_merged(self):
        result = cac_boundaries("10", "50", "E5")
        self.assertEqual(result["first_order_cac_ceiling"], "10")
        self.assertIsNone(result["lifetime_cac_ceiling"])

    def test_validated_clv_can_set_lifetime_cac_boundary(self):
        self.assertEqual(cac_boundaries("10", "50", "E6")["lifetime_cac_ceiling"], "50")

    def test_joint_stress_recomputes_cvr_refund_fee_and_cash(self):
        result = joint_stress("100", "0.7", "0.2", "0.15", "60", "10")
        self.assertEqual(result["net_revenue"], "56")
        self.assertEqual(result["fees"], "8.4")
        self.assertEqual(result["status"], "blocked")

    def test_spreadsheet_errors_never_become_zero(self):
        for value in ("#NAME?", "#DIV/0!", "#N/A"):
            with self.subTest(value=value):
                with self.assertRaises(PPFCError):
                    spreadsheet_value(value)


if __name__ == "__main__":
    unittest.main()
