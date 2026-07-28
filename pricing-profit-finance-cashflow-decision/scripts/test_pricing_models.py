#!/usr/bin/env python3

import copy
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS))
import calculate_dynamic_freight as freight
import calculate_pricing_economics as economics
import resolve_dynamic_parameters as parameters
import route_pricing_model as routing
from ppfc_common import PPFCError


def pricing_payload(price="100"):
    return {
        "currency": "USD", "price": price, "quantity": "1",
        "discount_rate": "0.1", "pass_through_tax_rate": "0.1", "refund_rate": "0",
        "other_reversals": "0", "product_cogs": "30", "fulfillment_cost": "10",
        "expected_return_cost": "0", "variable_marketing_cost": "0",
        "variable_service_cost": "0", "avoidable_period_cost": "0",
        "allocated_operating_expense": "0", "ad_spend": "10",
        "required_profit": "0", "risk_buffer": "0",
        "fees": [{"fee_id": "platform", "type": "rate", "basis": "recognized_net_revenue", "rate": "0.1"}],
    }


def rule(parameter_id, value, scope, *, priority=0, start="2026-01-01T00:00:00Z", end=None):
    return {
        "parameter_id": parameter_id, "semantic_code": "PLATFORM_FEE_RATE",
        "parameter_type": "rate", "version": "v1", "value": value,
        "rule_expression": None, "currency": None, "unit": "rate",
        "calculation_basis": "recognized_net_revenue", "scope": scope,
        "valid_from": start, "valid_to": end, "recorded_at": "2026-01-01T00:00:00Z",
        "superseded_at": None, "approval_status": "approved", "priority": priority,
        "source": {"source_id": f"S-{parameter_id}"},
    }


def parameter_payload(rules):
    return {
        "business_as_of_time": "2026-07-28T00:00:00Z",
        "knowledge_as_of_time": "2026-07-28T00:00:00Z",
        "context": {"country_code": "US", "platform_id": "P", "store_id": "STORE", "sku_id": "SKU"},
        "required_semantic_codes": ["PLATFORM_FEE_RATE"],
        "rules": rules,
    }


def freight_payload():
    return {
        "currency": "USD",
        "segments": [{
            "segment_id": "AIR-1", "transport_mode": "air", "eligible": True,
            "actual_weight": "8", "volume": "60", "volumetric_divisor": "6",
            "weight_rounding_increment": "1", "base_charge": "5", "minimum_charge": "40",
            "tiers": [
                {"from_inclusive": "0", "to_exclusive": "10", "rate_per_weight": "4"},
                {"from_inclusive": "10", "to_exclusive": None, "rate_per_weight": "3"}
            ],
            "surcharges": [{"type": "rate_on_base_and_tier", "value": "0.1", "applies": True, "mutual_exclusion_group": None}],
            "tax_rate": "0", "currency": "USD"
        }]
    }


class PricingModelTests(unittest.TestCase):
    def test_all_eighteen_model_families_are_registered(self):
        self.assertEqual(set(routing.FAMILIES), {f"P{i:02d}" for i in range(1, 19)})

    def test_known_route_and_evidence_ceiling(self):
        result = routing.route({"merchant_archetype": "marketplace_standard", "objective": "target_contribution", "evidence_capabilities": ["cost"]})
        self.assertEqual(result["primary_family"], "P02")
        self.assertEqual(result["supporting_families"], ["P04", "P12"])
        self.assertEqual(result["evidence_ceiling"], "validated_candidate")

    def test_unknown_route_degrades(self):
        self.assertEqual(routing.route({"merchant_archetype": "unknown"})["reason"], "UNKNOWN_MODEL_ROUTE")

    def test_wtp_route_without_wtp_is_only_hypothesis(self):
        result = routing.route({"merchant_archetype": "dtc_brand", "objective": "premium", "evidence_capabilities": ["cost"]})
        self.assertIn("validated_wtp", result["missing"])
        self.assertEqual(result["evidence_ceiling"], "hypothesis")

    def test_specific_parameter_rule_wins_without_scope_pollution(self):
        rules = [rule("GLOBAL", "0.15", {"country_code": "US"}), rule("SKU", "0.12", {"country_code": "US", "sku_id": "SKU"})]
        result = parameters.resolve(parameter_payload(rules))
        self.assertEqual(result["resolved"][0]["parameter_id"], "SKU")
        other = parameter_payload(rules); other["context"]["sku_id"] = "OTHER"
        self.assertEqual(parameters.resolve(other)["resolved"][0]["parameter_id"], "GLOBAL")

    def test_equal_specificity_conflict_blocks_order_independently(self):
        rules = [rule("A", "0.15", {"country_code": "US"}), rule("B", "0.16", {"country_code": "US"})]
        first = parameters.resolve(parameter_payload(rules))
        second = parameters.resolve(parameter_payload(list(reversed(rules))))
        self.assertEqual(first["unresolved"][0]["status"], "BLOCKED_AMBIGUOUS_RULE")
        self.assertEqual(first["unresolved"], second["unresolved"])

    def test_expired_parameter_does_not_silently_apply(self):
        result = parameters.resolve(parameter_payload([rule("OLD", "0.1", {"country_code": "US"}, end="2026-06-01T00:00:00Z")]))
        self.assertEqual(result["unresolved"][0]["status"], "EXPIRED_PARAMETER")

    def test_price_scenario_recomputes_percentage_fee(self):
        low = economics.calculate_scenario(pricing_payload("100"))
        high = economics.calculate_scenario(pricing_payload("200"))
        self.assertEqual(low["fees"]["platform"], "8.1")
        self.assertEqual(high["fees"]["platform"], "16.2")
        self.assertNotEqual(low["profit_bridge"]["operating_profit"], high["profit_bridge"]["operating_profit"])

    def test_fee_basis_is_not_silently_combined(self):
        payload = pricing_payload()
        payload["fees"].append({"fee_id": "gross", "type": "rate", "basis": "gross_revenue", "rate": "0.1"})
        result = economics.calculate_scenario(payload)
        self.assertEqual(result["fees"], {"platform": "8.1", "gross": "10"})

    def test_target_margin_solver_recomputes_and_meets_target(self):
        payload = pricing_payload()
        payload.update({"target_profit_margin": "0.2", "search_low": "40", "search_high": "300"})
        result = economics.solve_target(payload)
        self.assertGreaterEqual(float(result["metrics"]["PROFIT_MARGIN"]), 0.2)
        self.assertEqual(result["solved_target_profit_margin"], "0.2")

    def test_no_pre_ad_contribution_blocks_finite_roas(self):
        payload = pricing_payload("40")
        payload["product_cogs"] = "50"
        result = economics.calculate_scenario(payload)
        self.assertEqual(result["status"], "BLOCKED_NO_PRE_AD_CONTRIBUTION")
        self.assertIsNone(result["metrics"]["BREAK_EVEN_ROAS_NET"])

    def test_dynamic_freight_uses_volumetric_chargeable_weight(self):
        result = freight.calculate(freight_payload())
        segment = result["segments"][0]
        self.assertEqual(segment["volumetric_weight"], "10")
        self.assertEqual(segment["chargeable_weight"], "10")
        self.assertEqual(segment["tier_charge"], "30")
        self.assertEqual(result["route_total"], "40")

    def test_freight_minimum_charge_applies(self):
        payload = freight_payload()
        payload["segments"][0]["minimum_charge"] = "100"
        self.assertEqual(freight.calculate(payload)["route_total"], "100")

    def test_ineligible_route_blocks(self):
        payload = freight_payload(); payload["segments"][0]["eligible"] = False
        with self.assertRaises(PPFCError):
            freight.calculate(payload)

    def test_mutually_exclusive_surcharges_block(self):
        payload = freight_payload()
        payload["segments"][0]["surcharges"] = [
            {"type": "amount", "value": "5", "applies": True, "mutual_exclusion_group": "PEAK"},
            {"type": "amount", "value": "6", "applies": True, "mutual_exclusion_group": "PEAK"},
        ]
        with self.assertRaises(PPFCError):
            freight.calculate(payload)

    def test_authoritative_float_is_rejected(self):
        payload = pricing_payload(); payload["price"] = 100.0
        with self.assertRaises(PPFCError):
            economics.calculate_scenario(payload)


if __name__ == "__main__":
    unittest.main()
