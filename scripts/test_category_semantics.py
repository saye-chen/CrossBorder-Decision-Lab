#!/usr/bin/env python3
"""Semantic regression tests for CIDM decision-priority rules."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CIDM = ROOT / "category-investment-decision"


class LifecyclePriorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (CIDM / "SKILL.md").read_text(encoding="utf-8")
        cls.scoring = (CIDM / "references" / "scoring-model.md").read_text(
            encoding="utf-8"
        )
        cls.seller = (
            CIDM / "references" / "seller-endowment-matching.md"
        ).read_text(encoding="utf-8")

    def test_lc1_high_score_cannot_trigger_inventory(self):
        self.assertIn("LC-1 机会发现 | 无库存研究", self.seller)
        self.assertRegex(self.seller, r"LC-1 机会发现.*首批备货、重仓、多平台铺开")
        self.assertIn("LC-1/LC-2 不得因高分", self.skill)

    def test_decision_priority_is_explicit(self):
        expected = "门槛红线 → 生命周期动作上限 → 分数档位 → 已确认卖家资源约束"
        self.assertIn(expected, self.skill)

    def test_eight_week_boundary_is_exhaustive(self):
        self.assertIn("不足 8 个完整周，或达到 8 周但关键指标尚未稳定", self.scoring)
        self.assertIn("至少 8 个完整周，且关键指标已达到稳定条件", self.scoring)
        self.assertNotIn("（< 8 周）", self.scoring)
        self.assertNotIn("（> 8 周）", self.scoring)

    def test_confidence_caps_use_defined_values(self):
        self.assertNotIn("低→中", self.scoring)
        self.assertNotIn("中→高", self.scoring)
        self.assertIn("LC-1 阶段整体置信度上限为“低”", self.scoring)


class EvidenceAndSellerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scoring = (CIDM / "references" / "scoring-model.md").read_text(
            encoding="utf-8"
        )
        cls.seller = (
            CIDM / "references" / "seller-endowment-matching.md"
        ).read_text(encoding="utf-8")
        cls.product_line = (
            CIDM / "references" / "product-line-playbook.md"
        ).read_text(encoding="utf-8")

    def test_public_facts_remain_observations(self):
        self.assertIn("可核验事实仍标为“观察数据”", self.scoring)
        self.assertIn("推导出的销量、需求强度、竞争结论标为“分析假设”", self.scoring)

    def test_default_seller_cannot_set_heavy_actions(self):
        self.assertIn("不得直接用于确定预算比例、首批数量、多平台扩张或重仓动作", self.seller)
        self.assertNotRegex(self.seller, r"首批\s*\d+[-–]\d+\s*件")

    def test_store_numbers_are_declared_as_priors(self):
        self.assertIn("研究先验", self.product_line)
        self.assertIn("不是跨国家、平台、品类和价格带通用的健康标准", self.product_line)
        self.assertIn("美元区间仅是美国市场演示值", self.product_line)
        self.assertIn("不是固定 KPI", self.product_line)


class VersionTests(unittest.TestCase):
    def test_cidm_version_is_consistent(self):
        expected = "CIDM-2026.10"
        files = [
            CIDM / "SKILL.md",
            CIDM / "agents" / "openai.yaml",
            CIDM / "references" / "scoring-model.md",
            CIDM / "references" / "report-template.md",
            ROOT / "README.md",
        ]
        for path in files:
            self.assertIn(expected, path.read_text(encoding="utf-8"), str(path))

        stale = re.compile(r"CIDM-2026\.08")
        for path in files:
            self.assertIsNone(stale.search(path.read_text(encoding="utf-8")), str(path))


if __name__ == "__main__":
    unittest.main(verbosity=2)
