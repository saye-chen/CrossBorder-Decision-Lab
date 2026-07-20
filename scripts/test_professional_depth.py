#!/usr/bin/env python3
"""Substantive depth gates that complement structural contract tests."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ProfessionalDepth(unittest.TestCase):
    def assert_semantics(self, path: Path, anchors: list[str], minimum_lines: int = 40):
        text = path.read_text(encoding="utf-8")
        self.assertGreaterEqual(len(text.splitlines()), minimum_lines, path)
        for anchor in anchors:
            self.assertIn(anchor, text, f"{path}: missing {anchor}")

    def test_d09_platform_cards_have_platform_dna(self):
        directory = ROOT / "advertising-analysis-measurement-optimization/references/platforms"
        excluded = {"platform-card-contract.md", "universal-platform-routing.md"}
        cards = [path for path in directory.glob("*.md") if path.name not in excluded]
        self.assertEqual(len(cards), 10)
        for card in cards:
            self.assert_semantics(card, ["竞价与交付", "优化反馈", "归因差异", "特有失败", "反事实"], 60)

    def test_core_reference_semantics(self):
        groups = {
            "advertising-analysis-measurement-optimization": ["机制", "计算", "证据", "反事实", "停止", "回滚"],
            "consumer-insights-customer-growth": ["对象", "计算", "授权", "反事实", "不触达", "回填"],
            "competitive-intelligence-monitoring": ["对象", "基线", "代理", "归因", "反事实", "结果"],
            "logistics-inventory-fulfillment-decision": ["对象", "守恒", "交期", "反事实", "停止", "退出"],
            "platform-store-listing-conversion": ["对象", "版本", "G1", "反事实", "具体方案", "回滚"],
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
        domains = ["advertising-analysis-measurement-optimization", "consumer-insights-customer-growth", "competitive-intelligence-monitoring", "logistics-inventory-fulfillment-decision", "platform-store-listing-conversion"]
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
