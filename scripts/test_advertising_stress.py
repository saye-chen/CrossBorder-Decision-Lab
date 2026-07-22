#!/usr/bin/env python3
"""AAMO structural, platform-depth, sovereignty and deterministic-model stress tests."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AAMO = ROOT / "advertising-analysis-measurement-optimization"
SKILL = (AAMO / "SKILL.md").read_text(encoding="utf-8")
PLATFORMS = AAMO / "references" / "platforms"
REQUIRED_CARDS = {
    "tiktok-shop.md", "amazon.md", "shopee.md", "shein.md", "temu.md",
    "mercado-libre.md", "google-search.md", "google-shopping-pmax.md",
    "meta-ads.md", "tiktok-ads-dtc.md", "universal-platform-routing.md",
}


def run_model(script: str, payload: object) -> dict | list:
    with tempfile.TemporaryDirectory() as td:
        inp, out = Path(td) / "in.json", Path(td) / "out.json"
        inp.write_text(json.dumps(payload), encoding="utf-8")
        result = subprocess.run(
            ["python3", str(AAMO / "scripts" / script), "--input", str(inp), "--output", str(out)],
            capture_output=True, text=True,
        )
        if result.returncode:
            raise AssertionError(result.stderr)
        return json.loads(out.read_text(encoding="utf-8"))


class AdvertisingStress(unittest.TestCase):
    def test_required_platform_cards_exist_and_are_routed(self):
        actual = {path.name for path in PLATFORMS.glob("*.md")}
        self.assertTrue(REQUIRED_CARDS <= actual)
        for name in REQUIRED_CARDS:
            self.assertIn(name, SKILL)

    def test_platform_cards_have_expert_execution_depth(self):
        required = ["对象与最小诊断单元", "数据与测量门禁", "平台特有诊断", "利润、放量与退出", "禁止推断"]
        for name in REQUIRED_CARDS - {"universal-platform-routing.md"}:
            text = (PLATFORMS / name).read_text(encoding="utf-8")
            with self.subTest(platform=name):
                self.assertGreaterEqual(len(text.splitlines()), 15)
                for phrase in required:
                    self.assertIn(phrase, text)

    def test_universal_route_blocks_invented_platform_facts(self):
        text = (PLATFORMS / "universal-platform-routing.md").read_text(encoding="utf-8")
        for phrase in ["不得猜测", "inconclusive", "成熟经营账", "停止和回滚", "不得从相似平台复制"]:
            self.assertIn(phrase, text)

    def test_douyin_is_explicitly_excluded(self):
        for phrase in ["不用于抖音", "明确排除抖音", "不包含抖音"]:
            self.assertIn(phrase, SKILL)
        self.assertFalse(any("douyin" in path.name.lower() for path in PLATFORMS.glob("*.md")))

    def test_four_axes_lifecycle_and_three_books_are_mandatory(self):
        for phrase in ["流量场景", "控制模式", "计费方式", "优化目标", "冷启动", "放量", "衰退", "平台归因不等于利润", "利润不等于增量"]:
            self.assertIn(phrase, SKILL)

    def test_nine_layer_and_rollback_contract_is_present(self):
        diagnosis = (AAMO / "references" / "decision-and-nine-layer-diagnosis.md").read_text(encoding="utf-8")
        for phrase in ["账户", "交付", "流量", "创意", "承接", "转化", "经济", "增量", "运营", "反证", "替代解释"]:
            self.assertIn(phrase, diagnosis)
        for phrase in ["停止", "回滚", "缺失数据"]:
            self.assertIn(phrase, SKILL)

    def test_all_cost_modes_are_deterministic(self):
        cases = {
            "cpc": {"clicks": 100, "cpc": 1}, "cpm": {"impressions": 10000, "cpm": 10},
            "cpv": {"views": 1000, "cpv": .1}, "cpa": {"actions": 10, "cpa": 10},
            "cps": {"cps_rate": .1}, "fixed": {"fixed_cost": 100},
            "mixed": {"fixed_cost": 20, "variable_spend": 30, "cps_rate": .05},
        }
        for mode, fields in cases.items():
            with self.subTest(mode=mode):
                result = run_model("ad_economics.py", {"mode": mode, "revenue": 1000, "pre_ad_cm_rate": .3, **fields})
                self.assertIn("ad_contribution_profit", result)

    def test_negative_profit_cannot_be_reported_as_safe(self):
        result = run_model("ad_economics.py", {"mode": "fixed", "revenue": 100, "pre_ad_cm_rate": .2, "fixed_cost": 50})
        self.assertLess(result["ad_contribution_profit"], 0)
        self.assertNotEqual(result["status"], "profitable")

    def test_average_efficiency_cannot_hide_negative_margin(self):
        result = run_model("marginal_analysis.py", [
            {"spend": 100, "mature_revenue": 400, "contribution_profit": 60},
            {"spend": 200, "mature_revenue": 480, "contribution_profit": 40},
        ])
        self.assertGreater(result["stages"][1]["average_roas"], 1)
        self.assertLess(result["stages"][1]["marginal_contribution"], 0)

    def test_allocator_rejects_negative_and_respects_caps(self):
        result = run_model("allocate_budget.py", {"budget": 500, "candidates": [
            {"id": "safe", "step": 100, "max_budget": 200, "marginal_contribution_per_currency": .2},
            {"id": "loss", "step": 100, "max_budget": 500, "marginal_contribution_per_currency": -.1},
        ]})
        allocation = {item["id"]: item["allocated"] for item in result["allocations"]}
        self.assertEqual(allocation, {"safe": 200, "loss": 0})
        self.assertEqual(result["unallocated"], 300)

    def test_dynamic_platform_facts_require_current_verification(self):
        self.assertIn("动态平台事实执行时联网核验", SKILL)
        for name in REQUIRED_CARDS - {"universal-platform-routing.md"}:
            with self.subTest(platform=name):
                self.assertRegex((PLATFORMS / name).read_text(encoding="utf-8"), r"执行时.*核验")

    def test_advertising_ownership_is_registered(self):
        validator = (ROOT / "category-investment-decision" / "scripts" / "validate_decision_contract.py").read_text(encoding="utf-8")
        for decision_type in ["advertising", "advertising_measurement", "advertising_scaling"]:
            self.assertIn(f'"{decision_type}": "advertising-analysis-measurement-optimization"', validator)


if __name__ == "__main__":
    unittest.main(verbosity=2)
