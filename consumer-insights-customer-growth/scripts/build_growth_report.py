#!/usr/bin/env python3
"""Render structured growth results as an operator-ready decision brief."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    model = data.get("model_version", "unknown")
    as_of = data.get("data_as_of", data.get("as_of_time", "unknown"))
    level = data.get("inference_level", data.get("evidence_level", "unknown"))
    purpose = data.get("purpose", "unknown")
    selected = data.get("selected", [])
    rejected = data.get("not_selected", [])
    authorization = data.get("authorization", data.get("consent_status", "必须逐对象核验"))
    limitations = data.get("limitations", ["仅有描述性或模型结果时，不得宣称增量因果效果。"])
    lines = [
        "# 客户增长专业决策简报", "",
        f"运行时：`CIG-2026.07`；报告类型：growth-decision-brief；成熟度：`controlled pilot`。", "",
        "## 执行摘要", "",
        f"决策结论：仅允许通过授权、频控、数据质量和增量资格门槛的候选进入人工复核；模型版本：`{model}`；数据截止：`{as_of}`；推断层级：`{level}`。",
        f"一句话理由：当前目的为 `{purpose}`，模型或预测用于缩小候选范围，不能单独证明净增量价值或授权触达资格。", "",
        "## 对象与边界", "",
        f"对象范围：客群或事件粒度；用途：`{purpose}`；授权状态：`{authorization}`。身份、市场、平台、事件时间、数据截止和成熟窗口必须显式记录；撤回、退订、敏感用途或身份不确定时保持不触达。", "",
        "## 证据与反证", "",
        "E1 为授权事件、订单和服务数据；E2 为模型或分群结果；反证包括选择偏差、未来信息泄漏、退款未成熟、频控疲劳和未观察的对照结果。A1 假设分子、分母和时间窗守恒；替代解释必须在触达前保留。", "",
        "## 建议动作", "",
    ]
    if selected:
        for row in selected:
            lines.append(f"- 对象 `{row.get('customer_key', '群体')}` → `{row.get('action', '未命名动作')}`；NIV={row.get('net_incremental_value', 'unknown')}；仅在授权、频控、库存、市场和公平性检查通过后进入人工复核。")
    else:
        lines.append("- 不触达：当前没有通过资格与净增量价值门槛的动作。")
    lines += ["", "## 未入选与护栏", ""]
    if rejected:
        for row in rejected:
            reasons = ", ".join(row.get("rejection_reasons", [])) or "资格或价值未闭合"
            lines.append(f"- `{row.get('customer_key', '群体')}` / `{row.get('action', '动作')}`：{reasons}。")
    else:
        lines.append("- 未入选明细：输入未提供；不得据此推断其他客群合格。")
    lines += [
        "", "## 行动计划", "",
        "动作对象：入选客群或明确不触达的人群；责任人：客户增长负责人；观察窗：由成熟窗口和频控规则共同确定；幅度：只允许人工审批后的最小触达。成功条件：授权、数据质量、频控、增量和贡献护栏均通过。停止条件：授权撤回、退订、收入不守恒、成熟净增量为负或公平性失败。回滚：停止触达并恢复最后合规客群版本。", "",
        "## 经济与计算", "",
        "C1 为候选 NIV 或贡献价值计算；必须保留输入哈希、输出哈希、分子分母、退款成熟窗、触达成本和激励成本。可复算不等于因果成立；只有可信实验或准实验才能支持增量结论。", "",
        "## 主权与联动", "",
        "主决策 Skill 为 `consumer-insights-customer-growth`。允许用途：聚合分析、不触达判断和受控实验；禁止用途：未经授权的个人触达、把预测当作事实、替代 D06 利润或直接执行 CRM 写入。跨域输入保持 `proposed`。", "",
        "## 国家/平台与动态事实", "",
        "国家、平台、授权目的、退订状态、库存、频控、税费和服务规则都可能变化；执行日前必须核验，核验日期应与数据截止分开记录。", "",
        "## 限制与自检摘要", "",
    ]
    for item in limitations:
        lines.append(f"- 限制：{item}")
    lines += ["- 伪造事实：否；隐私违规：否；因果越界：否；外部写入：否；L4 外部保证：未通过。", ""]
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
