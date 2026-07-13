#!/usr/bin/env python3
"""Render deterministic CIM alerts as a reviewable Markdown brief."""

import argparse
import json
from pathlib import Path


def fmt(value):
    if value is None:
        return "—"
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
    lines = [
        "# 竞品监控简报", "",
        f"- 商品：{fmt(data.get('product_id'))}",
        f"- 快照时间：{fmt(data.get('snapshot_at'))}",
        f"- 自动检出事件：{len(alerts)}", "",
        "> 自动检测只证明阈值被触发，不构成原因结论；归因必须人工复核和交叉验证。", "",
        "| 等级 | 字段 | 变化前 | 变化后 | 相对变化 | Z-score | 归因状态 |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for alert in alerts:
        lines.append("| " + " | ".join(fmt(alert.get(key)) for key in [
            "severity", "field", "before", "after", "relative_change", "zscore", "attribution"
        ]) + " |")
    if not alerts:
        lines.append("| green | 无阈值事件 | — | — | — | — | continue_monitoring |")
    lines += ["", "## 待复核", "", "- 检查数据源、地区、设备和促销展示条件。", "- 为每个事件提出 2–3 个可证伪原因假设。", "- 明确影响、动作窗口、最小验证和停止条件。", ""]
    Path(args.output).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
