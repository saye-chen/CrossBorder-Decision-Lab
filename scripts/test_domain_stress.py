#!/usr/bin/env python3
"""Pressure-test the four upgraded decision domains and their cross-domain contract."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "category-investment-decision" / "scripts" / "validate_decision_contract.py"
spec = importlib.util.spec_from_file_location("decision_contract", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validator)

FILES = {
    "cidm": ROOT / "category-investment-decision" / "references" / "capital-portfolio-and-lifecycle.md",
    "cim": ROOT / "competitive-intelligence-monitoring" / "references" / "extended-competitive-signal-domains.md",
    "vlb": ROOT / "video-link-breakdown" / "references" / "content-creative-and-propagation.md",
    "cig": ROOT / "consumer-insights-customer-growth" / "references" / "customer-experience-service-loyalty-reputation.md",
}


class UpgradedDomainCoverage(unittest.TestCase):
    def assert_terms(self, key: str, terms: list[str]) -> None:
        text = FILES[key].read_text(encoding="utf-8")
        for term in terms:
            with self.subTest(domain=key, term=term):
                self.assertIn(term, text)

    def test_cidm_standard_missing_conflict_extreme_and_lifecycle(self):
        self.assert_terms("cidm", [
            "动态组合配置", "生命周期资本动作", "产品迁移", "卖家资源禀赋",
            "退出与资金释放", "数据截止时间冲突", "币税/利润口径冲突",
            "全部候选负贡献", "再进入", "停止条件",
        ])

    def test_cim_six_signals_proxy_conflict_and_routing(self):
        self.assert_terms("cim", [
            "广告竞争", "达人竞争", "价格促销", "渠道竞争", "供应物流",
            "品牌口碑", "代理信号", "单次快照", "替代解释", "禁止用途",
        ])

    def test_vlb_multiformat_production_testing_fatigue_and_migration(self):
        self.assert_terms("vlb", [
            "静态图", "轮播", "直播切片", "创意策略地图", "素材生产合同",
            "创意测试矩阵", "防疲劳素材", "跨国家/语言", "停止条件",
        ])

    def test_cig_journey_service_loyalty_reputation_and_crm(self):
        self.assert_terms("cig", [
            "全客户旅程", "客服与售后", "服务恢复", "会员与忠诚度",
            "评价与声誉", "CRM 编排", "不触达", "公平", "升级人工",
        ])


class CrossDomainRedlines(unittest.TestCase):
    def minimal(self, decision_type: str, owner: str) -> dict:
        return {
            "mode": "single", "decision_type": decision_type, "decision_owner": owner,
            "participating_skills": [owner], "runtime_versions": {owner: "TEST"},
            "professional_core": {
                "object_boundary": "SKU-US-platform-LC3", "conclusion": "Test only",
                "evidence_summary": ["E1"], "counterevidence": ["alternative"],
                "commercial_constraints": ["budget"], "risks_and_redlines": ["risk"],
                "actions": ["test"], "success_conditions": ["pass"],
                "stop_conditions": ["stop"], "limitations_and_missing_data": ["missing"],
            },
            "objects": [{"canonical_id": "o1", "country": "US", "platform": "P",
                         "category": "C", "lifecycle": "LC3"}],
            "evidence": [], "claims": [], "calculations": [],
            "required_calculation_ids": [], "unresolved_redlines": [], "adjustments": [],
        }

    def test_each_upgraded_decision_type_accepts_only_its_owner(self):
        cases = {
            "capital_portfolio": "category-investment-decision",
            "competitive_intelligence": "competitive-intelligence-monitoring",
            "content_creative": "video-link-breakdown",
            "customer_experience": "consumer-insights-customer-growth",
            "reputation": "consumer-insights-customer-growth",
            "advertising": "advertising-analysis-measurement-optimization",
        }
        for decision_type, owner in cases.items():
            payload = self.minimal(decision_type, owner)
            if owner == "category-investment-decision":
                payload["calculations"] = [{"id": "c", "calculator": "deterministic",
                                            "input_hash": "i", "output_hash": "o", "status": "complete"}]
                payload["required_calculation_ids"] = ["c"]
            with self.subTest(decision_type=decision_type, state="correct"):
                self.assertEqual(validator.validate(payload), [])
            payload["decision_owner"] = "video-link-breakdown" if owner != "video-link-breakdown" else "category-investment-decision"
            with self.subTest(decision_type=decision_type, state="wrong-owner"):
                self.assertTrue(any("decision_owner" in error for error in validator.validate(payload)))

    def test_missing_professional_module_always_blocks(self):
        payload = self.minimal("customer_experience", "consumer-insights-customer-growth")
        for field in validator.PROFESSIONAL_FIELDS:
            trial = {**payload, "professional_core": dict(payload["professional_core"])}
            trial["professional_core"][field] = ""
            with self.subTest(field=field):
                self.assertTrue(any(field in error for error in validator.validate(trial)))

    def test_proxy_signal_cannot_be_promoted_to_observed_fact(self):
        payload = self.minimal("competitive_intelligence", "competitive-intelligence-monitoring")
        payload["evidence"] = [{
            "id": "E1", "source_skill": "competitive-intelligence-monitoring",
            "evidence_type": "ad_count", "evidence_class": "proxy",
            "source_ref": "visible-page", "observed_at": "2026-07-16", "fingerprint": "fp1",
        }]
        payload["claims"] = [{
            "id": "C1", "producer_skill": "competitive-intelligence-monitoring",
            "claim_domain": "competitive_intelligence", "state": "observed",
            "object_id": "o1", "evidence_ids": ["E1"], "allowed_uses": ["monitor"],
            "forbidden_uses": ["ad_spend_fact"], "effective_now": False,
        }]
        self.assertTrue(any("non-direct evidence" in error for error in validator.validate(payload)))

    def test_economic_action_requires_complete_deterministic_calculation(self):
        payload = self.minimal("loyalty", "consumer-insights-customer-growth")
        payload["calculation_required"] = True
        self.assertTrue(any("required_calculation_ids" in error for error in validator.validate(payload)))
        payload["calculations"] = [{"id": "niv", "calculator": "loyalty_niv",
                                    "input_hash": "i", "output_hash": "o", "status": "complete"}]
        payload["required_calculation_ids"] = ["niv"]
        self.assertEqual(validator.validate(payload), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
