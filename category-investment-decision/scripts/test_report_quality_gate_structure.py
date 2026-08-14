#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_quality_gate import validate_report


class StructureGateTests(unittest.TestCase):
    def test_bad_heading_order_is_blocked(self):
        report = "# 标题\n## 最终决策\n## 决策页\n"
        result = validate_report(report, "Investment Diligence")
        self.assertEqual(result["status"], "BLOCKED")

    def test_unstructured_product_is_blocked(self):
        report = "# 标题\n## 决策页\n## 决策对象\n## 市场与竞品\n## 候选产品\n### P1：产品\n只是一个产品。\n"
        result = validate_report(report, "Investment Diligence")
        self.assertEqual(result["status"], "BLOCKED")

    def test_structured_report_can_pass_structural_gate(self):
        sections = [
            "决策页", "决策对象与范围", "市场与竞品证据", "候选产品池",
            "评分与资本判断", "国家与渠道矩阵", "单位经济与三场景",
            "供应链与质量", "90天验证计划", "Go / Hold / Stop",
            "Evidence / Assumption Ledger", "最终决策",
        ]
        report = "# 报告\n" + "\n".join(f"## {s}\n" for s in sections)
        report += "### 五道门槛\n市场需求、竞争可进入性、利润与现金、合规/支付、供应/IP/安全。当前状态、关键证据、反对证据、判断标准、放行条件、停止条件、复核角色、下一步、对决策影响。成功条件。\n"
        report += """
### P1：产品定义
产品定义：x。目标用户：x。场景：x。售价：$100。成本：$30。竞品：E1。证据：E1。假设：A1。风险：A1。渠道：SEO。评分：7。停止：退货。
### P2：产品定义
产品定义：x。目标用户：x。场景：x。售价：$100。成本：$30。竞品：E1。证据：E1。假设：A1。风险：A1。渠道：SEO。评分：7。停止：退货。
### P3：产品定义
产品定义：x。目标用户：x。场景：x。售价：$100。成本：$30。竞品：E1。证据：E1。假设：A1。风险：A1。渠道：SEO。评分：7。停止：退货。
评分 | 权重 | 原始分 | 加权分 | 置信度 |
证据层：来源，截至日期。反对证据、反例、替代解释。五道门槛：合规、IP、安全。七维评分：市场需求、竞争、利润空间。
市场需求、竞争可进入性、利润与现金、合规/支付、供应/IP/安全。当前状态、关键证据、判断标准、放行条件、停止条件、复核角色、下一步、对决策影响。
Evidence E1；Assumption A1；基准、压力、乐观；敏感性、翻转点、动作、停止、回滚、退出。
"""
        self.assertNotEqual(validate_report(report, "Investment Diligence")["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
