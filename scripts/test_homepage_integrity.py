#!/usr/bin/env python3
"""Protect the investor-facing homepage from inventory drift and bloat."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "CIDM": ("CIDM-2026.14", "category-investment-decision/SKILL.md"),
    "CIM": ("CIM-2026.10", "competitive-intelligence-monitoring/SKILL.md"),
    "VLB": ("VLB-2026.10", "video-link-breakdown/SKILL.md"),
    "CIG": ("CIG-2026.09", "consumer-insights-customer-growth/SKILL.md"),
    "AAMO": ("AAMO-2026.08", "advertising-analysis-measurement-optimization/SKILL.md"),
    "LIFD": ("LIFD-2026.04", "logistics-inventory-fulfillment-decision/SKILL.md"),
    "PLCO": ("PLCO-2026.08", "platform-store-listing-conversion/SKILL.md"),
    "CAPM": ("CAPM-2026.07", "creator-affiliate-partnership-management/SKILL.md"),
    "MBCM": ("MBCM-2026.01", "marketing-brand-campaign-management/SKILL.md"),
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
        for anchor in ("## 系统价值与长期壁垒", "### 三层价值结构",
                       "### 九 Skill 双向协同结构", "决策资产", "经营基准"):
            self.assertIn(anchor, self.zh)
        self.assertGreaterEqual(self.zh.count("```mermaid"), 2)

    def test_all_nine_skills_have_one_quick_route_and_current_runtime(self):
        table = self.zh.split("## Skill 快速定位", 1)[1].split("## 统一决策基础设施", 1)[0]
        for skill, (runtime, path) in SKILLS.items():
            self.assertEqual(len(re.findall(rf"^\| \*\*{skill}\*\* \|", table, re.M)), 1, skill)
            self.assertIn(runtime, table)
            self.assertIn(path, table)

    def test_collaboration_graph_has_no_missing_or_duplicate_root_nodes(self):
        graph = self.zh.split("### 九 Skill 双向协同结构", 1)[1].split("```", 2)[1]
        for skill in SKILLS:
            self.assertEqual(len(re.findall(rf"^\s+R --> {skill}\[", graph, re.M)), 1, skill)

    def test_homepage_uses_completed_capability_and_long_term_calibration_language(self):
        self.assertIn("已经形成九个可独立运行、可跨域联动的专业决策 Skill", self.zh)
        self.assertIn("随着持续使用", self.zh)
        for forbidden in ("当前尚未完成：真实授权", "需数据验证", "等待真实授权"):
            self.assertNotIn(forbidden, self.zh)

    def test_english_page_is_separate_and_complete(self):
        self.assertIn("[中文首页](README.md)", self.en)
        paired_sections = (
            ("## 系统价值与长期壁垒", "## System Value and Long-Term Defensibility"),
            ("### 为什么它不容易被更强的通用模型替代", "### Why stronger general-purpose models do not replace it"),
            ("### 面向长期使用的复利机制", "### The compounding mechanism of long-term use"),
            ("### 三层价值结构", "### Three-layer value architecture"),
            ("### 九 Skill 双向协同结构", "### Nine-Skill collaboration map"),
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
