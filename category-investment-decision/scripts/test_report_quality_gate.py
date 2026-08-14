#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_quality_gate import detect_depth, validate_report


class ReportQualityGateTests(unittest.TestCase):
    def test_detailed_request_forces_diligence(self):
        self.assertEqual(detect_depth("给我一个详细的多国家投资报告"), "Investment Diligence")
        self.assertEqual(detect_depth("快速判断这个产品"), "Decision Card")

    def test_short_report_is_blocked_for_diligence(self):
        result = validate_report("当前结论：建议进入。P1 高端产品。", "Investment Diligence")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertGreater(len(result["findings"]), 3)

    def test_complete_skeleton_passes(self):
        report = """# 报告
## 决策页
## 决策对象与范围
## 市场与竞品证据
## 候选产品池
### P1：产品
产品定义 目标用户 场景 售价 成本 竞品 证据 假设 风险 渠道 评分 停止
### P2：产品
产品定义 目标用户 场景 售价 成本 竞品 证据 假设 风险 渠道 评分 停止
### P3：产品
产品定义 目标用户 场景 售价 成本 竞品 证据 假设 风险 渠道 评分 停止
## 评分与资本判断
### 5.2 五道门槛
市场需求、竞争可进入性、利润与现金、合规/支付、供应/IP/安全。当前状态、关键证据、反对证据、判断标准、放行条件、停止条件、复核角色、下一步、对决策影响。成功条件。
## 国家与渠道矩阵
## 单位经济与三场景
## 供应链与质量
## 90天验证计划
## Go / Hold / Stop
## Evidence / Assumption Ledger
## 最终决策
当前结论 投资姿态。证据 来源 截至日期。反对证据、反例、替代解释。
五道门槛 合规 IP 安全。七维评分：市场需求、竞争、利润空间。
基准 压力 乐观。敏感性 翻转点。国家 渠道 矩阵。
动作：行动 验证 里程碑。停止 回滚 退出。
Evidence E1 Assumption A1 假设。售价 US$100（待验证区间）。
评分 | 权重 | 原始分 | 加权分 | 置信度 |
"""
        self.assertEqual(validate_report(report, "Investment Diligence")["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
