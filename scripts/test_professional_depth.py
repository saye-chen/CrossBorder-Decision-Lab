#!/usr/bin/env python3
"""Substantive depth gates that complement structural contract tests."""
from pathlib import Path
import json
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ProfessionalDepth(unittest.TestCase):
    def assert_semantics(self, path: Path, anchors: list[str], minimum_lines: int = 40):
        text = path.read_text(encoding="utf-8")
        self.assertGreaterEqual(len(text.splitlines()), minimum_lines, path)
        for anchor in anchors:
            self.assertIn(anchor, text, f"{path}: missing {anchor}")

    def test_aamo_platform_cards_have_platform_dna(self):
        directory = ROOT / "advertising-analysis-measurement-optimization/references/platforms"
        excluded = {"platform-card-contract.md", "universal-platform-routing.md"}
        cards = [path for path in directory.glob("*.md") if path.name not in excluded]
        self.assertEqual(len(cards), 10)
        for card in cards:
            self.assert_semantics(card, ["竞价与交付", "优化反馈", "归因差异", "特有失败", "反事实"], 60)

    def test_aamo_causal_claims_have_executable_estimators_and_limits(self):
        base = ROOT / "advertising-analysis-measurement-optimization"
        required = {"aamo_statistics.py", "design_incrementality_experiment.py",
                    "estimate_causal_incrementality.py", "estimate_media_response.py",
                    "test_causal_measurement.py"}
        self.assertTrue(required.issubset({p.name for p in (base / "scripts").glob("*.py")}))
        reference = (base / "references/incrementality-and-experimentation.md").read_text(encoding="utf-8")
        for anchor in ("聚类 ITT", "平行趋势", "合成控制", "时间留出", "`unavailable`", "不得标注 MMM"):
            self.assertIn(anchor, reference)
        result = subprocess.run(["python3", str(base / "scripts/test_causal_measurement.py")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))

    def test_core_reference_semantics(self):
        groups = {
            "advertising-analysis-measurement-optimization": ["机制", "计算", "证据", "反事实", "停止", "回滚"],
            "consumer-insights-customer-growth": ["对象", "计算", "授权", "反事实", "不触达", "回填"],
            "competitive-intelligence-monitoring": ["对象", "基线", "代理", "归因", "反事实", "结果"],
            "logistics-inventory-fulfillment-decision": ["对象", "守恒", "交期", "反事实", "停止", "退出"],
            "platform-store-listing-conversion": ["对象", "版本", "G1", "反事实", "具体方案", "回滚"],
            "creator-affiliate-partnership-management": ["机制", "计算", "反事实", "失效模式", "动作", "退出"],
        }
        excluded = {"professional-depth-governance.md", "skill-integration-protocol.md", "data-contract-and-automation.md", "professional-report-delivery.md", "output-protocols.md"}
        for domain, anchors in groups.items():
            for path in (ROOT / domain / "references").glob("*.md"):
                if path.name in excluded:
                    continue
                with self.subTest(path=path):
                    self.assert_semantics(path, anchors)
                    self.assertIn(f"## {path.stem} 专属决策内核", path.read_text(encoding="utf-8"), f"{path}: missing module-specific kernel")

    def test_module_specific_kernels_are_not_identical_padding(self):
        domains = ["advertising-analysis-measurement-optimization", "consumer-insights-customer-growth", "competitive-intelligence-monitoring", "logistics-inventory-fulfillment-decision", "platform-store-listing-conversion", "creator-affiliate-partnership-management"]
        kernels = []
        for domain in domains:
            for path in (ROOT / domain / "references").glob("*.md"):
                marker = f"## {path.stem} 专属决策内核"
                text = path.read_text(encoding="utf-8")
                if marker in text:
                    kernels.append(text.split(marker, 1)[1].split("\n## ", 1)[0].strip())
        self.assertGreaterEqual(len(kernels), 50)
        self.assertEqual(len(kernels), len(set(kernels)), "module-specific kernels must be unique")

    def test_golden_and_cross_skill_are_not_skeletons(self):
        for path in (ROOT / "evaluations/golden").glob("*-single.md"):
            self.assert_semantics(path, ["完整评测输入", "预期推理链路", "预期失败断言", "本域独立输入与预期中间状态", "翻转/失败"], 50)
        for path in (ROOT / "evaluations/cross-skill").glob("XS-*.md"):
            self.assert_semantics(path, ["完整评测输入", "预期推理链路", "预期输出状态", "cross-skill-executable-fixtures.json"], 50)
        fixture = __import__("json").loads((ROOT / "evaluations/cross-skill-executable-fixtures.json").read_text(encoding="utf-8"))["scenarios"]
        self.assertEqual(len(fixture), 10)
        self.assertEqual(len({str(item["input"]) for item in fixture}), 10)
        for item in fixture:
            self.assertTrue(item["evidence_conflicts"] and item["expected_states"] and item["calculation_expectations"] and item["forbidden"])

    def test_adversarial_coverage(self):
        names = {path.stem for path in (ROOT / "evaluations/adversarial-cases").glob("*.md")}
        required = {"fabricated-data", "sovereignty-overreach", "version-pollution", "hallucinated-numbers", "partial-tool-failure", "keyword-stuffed", "contradictory-scale"}
        self.assertTrue(required.issubset(names))

    def test_historical_replay_remains_honest(self):
        for rel in ["evaluations/d07/historical-replay-template.json", "evaluations/d08/historical-replay-template.json"]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn('"minimum_authorized_cases": 3', text)
            self.assertIn('"production_ready": false', text)
            self.assertIn('"cases": []', text)

    def test_mbcm_six_axis_professional_depth(self):
        base = ROOT / "marketing-brand-campaign-management"
        modules = sorted((base / "references/modules").glob("s*.md"))
        self.assertEqual(len(modules), 13)
        mechanisms = []
        for path in modules:
            text = path.read_text(encoding="utf-8")
            self.assertGreaterEqual(len(text.splitlines()), 14, path)
            self.assertIn("专属机制", text, path)
            self.assertIn("失败断言", text, path)
            self.assertIn("停止/回滚", text, path)
            self.assertIn("最小专业合同", text, path)
            self.assertIn("翻转条件", text, path)
            self.assertIn("跨域请求", text, path)
            mechanisms.append(next(line for line in text.splitlines() if "专属机制" in line))
        self.assertEqual(len(mechanisms), len(set(mechanisms)))
        catalog = json.loads((base / "evaluations/fixtures/evaluation-catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["total"], 120)
        self.assertEqual(len({case["mechanism"] for case in catalog["cases"]}), 120)
        self.assertTrue(all(case.get("decision_input") and case.get("expected_assertions") for case in catalog["cases"]))
        self.assertEqual(catalog["coverage"]["stress_levels"], ["T1","T2","T3","T4","T5","T6"])
        self.assertEqual(len(catalog["coverage"]["estimation_methods"]), 10)
        self.assertEqual(len(catalog["high_risk_combinations"]), 16)
        model_names = {"campaign_economics.py","offer_economics.py","incrementality_bridge.py",
            "pull_forward_cannibalization.py","resource_portfolio.py","brand_investment_scenarios.py",
            "capacity_stress.py","risk_and_sensitivity.py","clearance_exit_economics.py",
            "validate_units_currency_time.py"}
        self.assertTrue(model_names.issubset({p.name for p in (base / "scripts").glob("*.py")}))
        science_models={"experiment_design.py","causal_effects.py","uncertainty_engine.py",
            "offer_response_optimization.py","channel_response.py","aggregate_customer_economics.py",
            "channel_curve_estimation.py","brand_value_bridge.py","seasonality_competition.py",
            "incident_recovery_quantification.py"}
        self.assertTrue(science_models.issubset({p.name for p in (base / "scripts").glob("*.py")}))
        platform_cards=sorted((base/"references/platforms").glob("*-marketing-operations.md"))
        self.assertEqual(len(platform_cards),3)
        for card in platform_cards:
            text=card.read_text(encoding="utf-8")
            self.assertGreaterEqual(len(text.splitlines()),30,card)
            for anchor in ("证据与数据","专属识别风险","操作决策","停止条件"):
                self.assertIn(anchor,text,(card,anchor))
            self.assertTrue(any(anchor in text for anchor in ("动态","实时核验","随市场变化")),card)
        skill=(base/"SKILL.md").read_text(encoding="utf-8")
        self.assertIn("按十层根因",skill)
        routes={
            "s05-offer.md":"offer_response_optimization.py",
            "s07-channel.md":"channel_curve_estimation.py",
            "s09-brand-health.md":"brand_value_bridge.py",
            "s10-incrementality.md":"experiment_design.py",
        }
        for filename,tool in routes.items():
            self.assertIn(tool,(base/"references/modules"/filename).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
