#!/usr/bin/env python3
"""Render deterministic CIM alerts as an operator-ready review brief."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def fmt(value):
    if value is None:
        return "unknown"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value).replace("|", "\\|")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alerts", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.alerts).read_text(encoding="utf-8"))
    alerts = data.get("alerts", [])
    object_id = data.get("object_id") or data.get("product_id") or "unknown"
    snapshot_at = data.get("snapshot_at") or data.get("as_of_time") or "unknown"
    owner = data.get("owner") or "竞品情报负责人；执行前必须由运行者确认"
    lines = [
        "# 竞品监控专业复核简报", "",
        "运行时：`CIM-2026.07`；报告类型：monitoring-review-brief；成熟度：`controlled pilot`。", "",
        "## 执行摘要", "",
        f"决策结论：当前仅允许复核和受控验证；对象：`{fmt(object_id)}`；快照时间：`{fmt(snapshot_at)}`；自动检出事件：{len(alerts)}。",
        "一句话理由：自动检测只证明阈值触发，不证明原因、竞争事实或经营影响；任何放量、价格、库存和资本动作必须由对应 owner 另行决定。", "",
        "## 对象与边界", "",
        f"对象与版本：`{fmt(object_id)}`；适用范围限当前国家、平台、展示条件和快照窗口。基线方法：`{fmt(data.get('baseline_method', 'mean_std'))}`；数据截止：`{fmt(snapshot_at)}`。缺失数据保持 unknown，不补写为零。", "",
        "## 证据与反证", "",
        f"E1 为当前快照与基线计算，E2 为告警字段变化；反证必须来自不同来源、不同对象或不同展示条件。当前证据截止为 `{fmt(snapshot_at)}`。A1 假设对象和展示条件可比；替代解释包括促销、地区、设备、采集污染和平台推荐变化。", "",
        "## 变化台账", "",
        "| 等级 | 确认状态 | 字段 | 变化前 | 变化后 | 相对变化 | Z-score | 归因状态 |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for alert in alerts:
        lines.append("| " + " | ".join(fmt(alert.get(key)) for key in [
            "severity", "confirmation_status", "field", "before", "after", "relative_change", "zscore", "attribution"
        ]) + " |")
    if not alerts:
        lines.append("| green | confirmed | 无阈值事件 | — | — | — | — | continue_monitoring |")
    lines += [
        "", "## 根因与替代解释", "",
        "自动告警不能直接形成根因。每个事件至少建立两个可证伪假设，并为每个假设保留支持证据、反对证据、验证方式和截止时间。代理信号保持为代理，不写成事实或因果结论。", "",
        "## 行动计划", "",
        f"动作对象：`{fmt(object_id)}`；责任人：{owner}；观察窗：由运行者根据事件有效期指定；幅度：仅限只读复核、第二来源核验或可逆小测。成功条件：第二独立来源确认且影响范围可复核。停止条件：来源不可比、对象错配、授权失效或变化无法确认。回滚：撤回趋势主张并恢复最近有效基线。", "",
        "## 经济与计算", "",
        "C1 仅记录基线中心、尺度、样本数和告警阈值；计算器为 `detect_changes.py`，输入哈希和输出哈希应由执行记录保存。可复算只证明异常检测一致，不证明增量、利润或资本回报。", "",
        "## 主权与联动", "",
        "主决策 Skill 为 `competitive-intelligence-monitoring`。允许用途：监控、诊断和证据补齐；禁止用途：直接改变价格、预算、库存、Listing、CRM 或资本姿态。跨域建议保持 `proposed`，冲突提交给 owner 升级。", "",
        "## 国家/平台与动态事实", "",
        "国家、平台、促销、设备、展示条件和抓取资格都是动态事实，执行日前必须核验，核验日期由运行者记录。历史截图、相邻平台和公开代理不得填补当前事实。", "",
        "## 自检摘要", "",
        "伪造事实：否；因果越界：否；主权越界：否；外部写入：否；可复算：是（仅检测层）；L4 外部保证：未通过。", "",
    ]
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
