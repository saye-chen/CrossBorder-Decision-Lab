#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_domain_quality import validate_text


class SharedDecisionQualityTests(unittest.TestCase):
    def test_thin_domain_is_blocked(self):
        self.assertEqual(validate_text("当前结论：建议进入。", "pricing")["status"], "BLOCKED")

    def test_complete_domain_chain_passes(self):
        text = "对象与范围。当前结论。Evidence E1 证据。反对证据。Assumption A1 假设。门槛与红线。分析与计算 C1。动作。成功条件。停止条件。回滚退出。数据缺口与重算触发。"
        self.assertEqual(validate_text(text, "pricing")["status"], "PASS")

    def test_handoff_requires_provenance_and_bounds(self):
        text = "对象 当前结论 证据 E1 反对证据 假设 A1 门槛 分析 C1 动作 成功条件 停止条件 回滚 数据缺口。"
        self.assertEqual(validate_text(text, "pricing", handoff=True)["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
