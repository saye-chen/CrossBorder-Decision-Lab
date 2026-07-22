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
BOUTIQUE = ROOT / "category-investment-decision" / "references" / "boutique-zero-to-one-operating-system.md"
SELLER_MODELS = ROOT / "category-investment-decision" / "references" / "seller-operating-models-and-topologies.md"
REPORT_LINEAGE = ROOT / "category-investment-decision" / "references" / "report-lineage-and-progressive-rebase.md"


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

    def test_boutique_zero_to_one_scale_cost_and_redline_depth(self):
        text = BOUTIQUE.read_text(encoding="utf-8")
        for term in ["产品先天投资质量卡", "精品组织攻坚卡", "Boutique Venture Test", "G0 投资立项", "G10 修复/退出", "九条并行工作流", "规模—成本桥", "validated cost", "停止条件", "回滚"]:
            with self.subTest(term=term):
                self.assertIn(term, text)
        self.assertIn("不能直接加到 CIDM 七维分数", text)
        self.assertIn("不能抵消硬红线", text)

    def test_seller_operating_models_cover_asymmetry_playbooks_and_topologies(self):
        text = SELLER_MODELS.read_text(encoding="utf-8")
        for term in ["无货源 / 轻资产验证", "铺货 / 数据筛选", "精铺 / 漏斗式升级", "品牌商家 / 资产复利", "供应链型 / 反向定义产品", "竞品流量承接", "跟卖 / 同商品竞争", "多链接 A/B 测试", "多店 / AB 店", "单一国家、多平台布局", "多国家、单平台协同", "多国家、多平台协同", "约束解除合同", "Seller-specific Feasibility"]:
            with self.subTest(term=term):
                self.assertIn(term, text)
        for forbidden_guard in ["不得提供商标滥用", "侵权、假货或商品不一致跟卖", "不提供规避关联和风控步骤"]:
            self.assertIn(forbidden_guard, text)

    def test_progressive_report_rebase_has_single_current_state_and_depth_accumulation(self):
        text = REPORT_LINEAGE.read_text(encoding="utf-8")
        for term in ["Current Effective Decision", "Information Delta Card", "Addendum", "Revision", "Recalculation", "Rebase", "New Decision Object", "Impact Set", "继承、替换与撤销矩阵", "Consolidated Report", "Correction", "Current Decision State"]:
            with self.subTest(term=term):
                self.assertIn(term, text)
        self.assertIn("任何时点只允许一个", text)
        self.assertIn("连续对话只能提高证据密度", text)
        self.assertIn("不得让用户自行从多轮消息中拼接", text)

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
        versions = {
            "category-investment-decision": "CIDM-2026.14",
            "competitive-intelligence-monitoring": "CIM-2026.10",
            "video-link-breakdown": "VLB-2026.10",
            "consumer-insights-customer-growth": "CIG-2026.09",
            "advertising-analysis-measurement-optimization": "AAMO-2026.08",
            "logistics-inventory-fulfillment-decision": "LIFD-2026.04",
        }
        return {
            "mode": "single", "decision_type": decision_type, "decision_owner": owner,
            "participating_skills": [owner], "runtime_versions": {owner: versions[owner]},
            "participant_results": {owner: {"status": "contributed"}},
            "professional_core": {
                "object_boundary": "SKU-US-platform-LC3", "conclusion": "Test only",
                "evidence_summary": ["E1"], "counterevidence": ["alternative"],
                "commercial_constraints": ["budget"], "risks_and_redlines": ["risk"],
                "actions": ["test"], "success_conditions": ["pass"],
                "stop_conditions": ["stop"], "limitations_and_missing_data": ["missing"],
            },
            "objects": [{"canonical_id": "o1", "country": "US", "platform": "P",
                         "category": "C", "lifecycle": "LC3"}],
            "evidence": [{"id": "E1", "source_skill": owner, "evidence_type": "authorized_fixture",
                          "evidence_class": "direct", "source_ref": "fixture:E1", "observed_at": "2026-07-17",
                          "fingerprint": "fixture-E1"}],
            "claims": [{"id": "C1", "producer_skill": owner, "claim_domain": decision_type,
                        "state": "validated", "object_id": "o1", "evidence_ids": ["E1"],
                        "allowed_uses": ["decision_support"], "forbidden_uses": [], "effective_now": True}],
            "calculations": [],
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
