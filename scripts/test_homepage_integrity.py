#!/usr/bin/env python3
"""Protect the investor-facing homepage from inventory drift and bloat."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "CIDM": ("CIDM-2026.07", "category-investment-decision/SKILL.md"),
    "CIM": ("CIM-2026.07", "competitive-intelligence-monitoring/SKILL.md"),
    "VLB": ("VLB-2026.07", "video-link-breakdown/SKILL.md"),
    "CIG": ("CIG-2026.07", "consumer-insights-customer-growth/SKILL.md"),
    "AAMO": ("AAMO-2026.07", "advertising-analysis-measurement-optimization/SKILL.md"),
    "LIFD": ("LIFD-2026.07", "logistics-inventory-fulfillment-decision/SKILL.md"),
    "PLCO": ("PLCO-2026.07", "platform-store-listing-conversion/SKILL.md"),
    "CAPM": ("CAPM-2026.07", "creator-affiliate-partnership-management/SKILL.md"),
    "MBCM": ("MBCM-2026.07", "marketing-brand-campaign-management/SKILL.md"),
    "PPFC": ("PPFC-2026.07", "pricing-profit-finance-cashflow-decision/SKILL.md"),
    "PIPM": ("PIPM-2026.07", "product-innovation-product-management/SKILL.md"),
    "SPPQ": ("SPPQ-2026.07", "supplier-procurement-production-quality-decision/SKILL.md"),
}


class HomepageIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.zh = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.en = (ROOT / "README.en.md").read_text(encoding="utf-8")

    def test_chinese_homepage_is_concise_and_has_english_entry(self):
        self.assertLessEqual(len(self.zh.splitlines()), 300)
        self.assertIn("[English](README.en.md)", self.zh)
        for stale in ("# 出海决策实验室", "## Why This System Exists", "## Current Release Status"):
            self.assertNotIn(stale, self.zh)

    def test_investor_value_and_both_architecture_views_exist(self):
        for anchor in ("## 系统价值与长期壁垒", "### D01—D14 目标架构",
                       "### D01—D14 连续决策闭环", "ERDG 治理控制面",
                       "决策资产", "经营基准"):
            self.assertIn(anchor, self.zh)
        self.assertGreaterEqual(self.zh.count("```mermaid"), 2)

    def test_mermaid_class_definitions_use_github_compatible_statements(self):
        for page in (self.zh, self.en):
            self.assertEqual(page.count("```mermaid"), page.count("```mermaid") and len(re.findall(r"```mermaid\n[\s\S]*?\n```", page)))
            for diagram in re.findall(r"```mermaid\n([\s\S]*?)\n```", page):
                self.assertNotRegex(diagram, r"classDef[^\n]*;\s*class\s")
                for line in diagram.splitlines():
                    if line.strip().startswith("classDef "):
                        self.assertRegex(line.strip(), r"^classDef\s+[A-Za-z][\w-]*\s+[^;]+$")

    def test_erdg_is_visible_without_taking_business_ownership(self):
        for page in (self.zh, self.en):
            self.assertIn("ERDG-CONTRACT-2026.07", page)
            self.assertIn("governance/erdg/ERDG.md", page)
        self.assertIn("旧 v1 运行主链已经退役", self.zh)
        self.assertIn("old v1 runtime path is retired", self.en)
        architecture = self.zh.split("### D01—D14 目标架构", 1)[1].split("```", 2)[1]
        for term in ("对象 · 证据 · 计算 · 经济 · 风险 · 状态 · 参数 · 血缘",
                     "合同与红线校验", "D14 跨域协同姿态与决策编排"):
            self.assertIn(term, architecture)
        self.assertIn("ERDG 只做中立治理与确定性计算，不替代任何专业域作出业务结论", self.zh)

    def test_all_registered_skills_have_one_quick_route_and_current_runtime(self):
        table = self.zh.split("## Skill 快速定位", 1)[1].split("## 统一决策基础设施", 1)[0]
        for skill, (runtime, path) in SKILLS.items():
            self.assertEqual(len(re.findall(rf"^\| \*\*{skill}\*\* \|", table, re.M)), 1, skill)
            self.assertIn(runtime, table)
            self.assertIn(path, table)

    def test_collaboration_graph_has_no_missing_or_duplicate_root_nodes(self):
        graph = self.zh.split("### D01—D14 目标架构", 1)[1].split("```", 2)[1]
        for index in range(1, 15):
            domain_id = f"D{index:02d}"
            self.assertEqual(len(re.findall(rf"\b{domain_id}\[", graph)), 1, domain_id)
        self.assertIn("D04 SPPQ", graph)
        self.assertIn("D05 合规与市场准入", graph)
        self.assertIn("D14 跨域协同姿态与决策编排", graph)
        self.assertIn("不裁决专业结论、不批准资本、不拥有外部写入", self.zh)
        self.assertIn(
            "cannot adjudicate professional conclusions, approve capital, or write externally",
            self.en,
        )

    def test_homepage_uses_completed_capability_and_long_term_calibration_language(self):
        self.assertIn("已经形成十二个可独立运行、可跨域联动的专业决策 Skill", self.zh)
        self.assertIn("随着持续使用", self.zh)
        for forbidden in ("当前尚未完成：真实授权", "需数据验证", "等待真实授权"):
            self.assertNotIn(forbidden, self.zh)

    def test_english_page_is_separate_and_complete(self):
        self.assertIn("[中文首页](README.md)", self.en)
        paired_sections = (
            ("## 系统价值与长期壁垒", "## System Value and Long-Term Defensibility"),
            ("### 为什么它不容易被更强的通用模型替代", "### Why stronger general-purpose models do not replace it"),
            ("### 面向长期使用的复利机制", "### The compounding mechanism of long-term use"),
            ("### D01—D14 目标架构", "### D01-D14 target architecture"),
            ("### D01—D14 连续决策闭环", "### Continuous D01-D14 decision loop"),
            ("## Skill 快速定位", "## Skill Directory"),
            ("## 统一决策基础设施", "## Shared Decision Infrastructure"),
            ("## 当前能力", "## Current Capabilities"),
            ("## 如何使用", "## How to Use"),
            ("## 仓库导航", "## Repository Navigation"),
            ("## 质量与安全边界", "## Quality and Safety"),
            ("## Copyright", "## Copyright"),
        )
        for zh_heading, en_heading in paired_sections:
            self.assertIn(zh_heading, self.zh)
            self.assertIn(en_heading, self.en)
        self.assertEqual(self.zh.count("```mermaid"), self.en.count("```mermaid"))
        for skill, (_, path) in SKILLS.items():
            self.assertIn(skill, self.en)
            self.assertIn(path, self.en)
        for anchor in ("complete core workflows", "Current Capabilities",
                       "operating benchmarks", "stopping", "rollback", "exit"):
            self.assertIn(anchor, self.en)


if __name__ == "__main__":
    unittest.main(verbosity=2)
