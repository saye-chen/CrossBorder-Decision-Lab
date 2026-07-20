#!/usr/bin/env python3
"""Validate the seven-skill governance baseline and semantic anchors."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = [
    "category-investment-decision", "competitive-intelligence-monitoring",
    "video-link-breakdown", "consumer-insights-customer-growth",
    "advertising-analysis-measurement-optimization",
    "logistics-inventory-fulfillment-decision",
    "platform-store-listing-conversion",
]
FILES = [
    "professional-depth-governance.md", "skill-integration-protocol.md",
    "output-protocols/professional-report-delivery.md",
    "data-contract-and-automation.md",
]
ANCHORS = {
    "professional-depth-governance.md": ["对象", "证据", "反对证据", "停止", "回滚", "结果回填"],
    "skill-integration-protocol.md": ["主权", "允许用途", "禁止用途", "部分失败", "版本", "冲突"],
    "output-protocols/professional-report-delivery.md": ["Decision Card", "Decision Memo", "Diligence", "成功", "停止", "回滚"],
    "data-contract-and-automation.md": ["object_id", "as_of_time", "缺失", "零值", "幂等", "外部写入"],
}

errors = []
for skill in SKILLS:
    skill_text = (ROOT / skill / "SKILL.md").read_text()
    for rel in FILES:
        path = ROOT / skill / "references" / rel
        if not path.is_file():
            errors.append(f"{skill}: missing {rel}")
            continue
        text = path.read_text()
        missing = [anchor for anchor in ANCHORS[rel] if anchor not in text]
        if missing:
            errors.append(f"{skill}/{rel}: missing semantic anchors {missing}")
        if rel not in skill_text and Path(rel).name not in skill_text:
            errors.append(f"{skill}: SKILL.md does not route {rel}")
    for heading in ["## 专业性与决策可用性硬约束", "## 入口与交付层级", "## 跨域边界与双向数据交换"]:
        if heading not in skill_text:
            errors.append(f"{skill}: missing heading {heading}")

if errors:
    raise SystemExit("Governance baseline failed:\n- " + "\n- ".join(errors))
print("Governance baseline passed for 7 skills.")
