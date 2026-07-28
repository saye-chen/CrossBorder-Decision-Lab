#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_structure_contract.py")
SPEC = importlib.util.spec_from_file_location("ppfc_structure", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
ROOT = MODULE.ROOT


class StructureContractTests(unittest.TestCase):
    def test_repository_structure_and_schemas(self):
        MODULE.validate_structure()
        MODULE.validate_schema_contracts()

    def test_platform_pricing_cards_cover_mechanism_families_and_fail_closed(self):
        text = (ROOT / "references/platform-pricing-mechanism-cards.md").read_text(encoding="utf-8")
        for marker in (
            "Amazon Marketplace", "TikTok Shop", "Shopee 与 Lazada",
            "Temu 与 SHEIN Marketplace", "Shopify 与其他 DTC",
            "Walmart、eBay 与 Etsy", "未知平台与新模式",
            "机制边界", "价格对象", "动态栈", "诊断与证伪", "竞争反馈",
        ):
            self.assertIn(marker, text)
        self.assertIn("禁止复制", text)

    def test_initial_state_must_be_draft(self):
        MODULE.validate_transition(None, "draft")
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_transition(None, "proposed")

    def test_forbidden_transitions_fail_closed(self):
        for transition in MODULE.FORBIDDEN_TRANSITIONS:
            with self.subTest(transition=transition):
                with self.assertRaises(MODULE.ContractError):
                    MODULE.validate_transition(*transition)

    def test_dynamic_rule_requires_one_value_form(self):
        base = {
            "value": "0.15",
            "rule_expression": None,
            "calculation_basis": "tax_exclusive_revenue",
            "scope": {"country_code": "US", "platform_id": "marketplace"},
            "valid_from": "2026-07-28T00:00:00Z",
            "recorded_at": "2026-07-28T00:00:00Z",
            "source": {"content_fingerprint": "a" * 64},
            "approval_status": "approved",
        }
        MODULE.validate_dynamic_rule_semantics(base)
        invalid = dict(base, rule_expression="rate(price)", value="0.15")
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_dynamic_rule_semantics(invalid)

    def test_unapproved_rule_is_not_authoritative(self):
        rule = {
            "value": "0.15",
            "rule_expression": None,
            "calculation_basis": "tax_exclusive_revenue",
            "scope": {"country_code": "US"},
            "valid_from": "2026-07-28T00:00:00Z",
            "recorded_at": "2026-07-28T00:00:00Z",
            "source": {"content_fingerprint": "b" * 64},
            "approval_status": "proposed",
        }
        with self.assertRaises(MODULE.ContractError):
            MODULE.validate_dynamic_rule_semantics(rule)


if __name__ == "__main__":
    unittest.main()
