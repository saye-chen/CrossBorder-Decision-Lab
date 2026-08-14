#!/usr/bin/env python3
"""Shared quality gate for domain reports and cross-domain handoffs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

UNIVERSAL_FIELDS = {
    "object": ("对象", "范围", "object"),
    "conclusion": ("当前结论", "结论", "conclusion"),
    "evidence": ("证据", "Evidence", "source"),
    "counter_evidence": ("反对证据", "反例", "counter"),
    "assumptions": ("假设", "Assumption", "unknown"),
    "gates": ("门槛", "约束", "risk", "红线"),
    "analysis": ("分析", "计算", "评分", "calculation"),
    "action": ("动作", "行动", "action"),
    "success": ("成功条件", "护栏", "success"),
    "stop": ("停止条件", "暂停", "stop"),
    "rollback": ("回滚", "退出", "rollback"),
    "unknowns": ("数据缺口", "缺失", "recompute", "重算"),
}

HANDOFF_FIELDS = {
    "domain": ("domain", "域"), "packet_id": ("packet_id", "交接包"),
    "version": ("version", "版本"), "status": ("status", "状态"),
    "evidence_ids": ("evidence_ids", "证据编号"), "calculation_ids": ("calculation_ids", "计算编号"),
    "allowed_uses": ("allowed_uses", "允许用途"), "forbidden_uses": ("forbidden_uses", "禁止用途"),
    "owner": ("owner", "负责人"), "valid_until": ("valid_until", "有效期"),
    "recompute_trigger": ("recompute_trigger", "重算触发"),
}


def _has(text: str, terms: tuple[str, ...]) -> bool:
    return any(term.lower() in text.lower() for term in terms)


def validate_text(text: str, domain: str, handoff: bool = False) -> dict:
    findings = []
    for field, terms in UNIVERSAL_FIELDS.items():
        if not _has(text, terms):
            findings.append({"severity": "BLOCKED", "field": field, "reason": "missing universal decision-chain field"})
    if handoff:
        for field, terms in HANDOFF_FIELDS.items():
            if not _has(text, terms):
                findings.append({"severity": "BLOCKED", "field": field, "reason": "missing cross-domain handoff field"})
    if re.search(r"(?:建议|推荐|可放量|值得进入|scale|proceed)", text, re.I) and not re.search(r"(?:E\d+|A\d+|证据编号|假设编号)", text):
        findings.append({"severity": "BLOCKED", "field": "claim-lineage", "reason": "actionable claim has no evidence/assumption reference"})
    blocking = [f for f in findings if f["severity"] == "BLOCKED"]
    return {"domain": domain, "status": "BLOCKED" if blocking else "PASS", "findings": findings}


def validate_paths(paths: list[Path], handoff: bool = False) -> dict:
    results = [validate_text(path.read_text(encoding="utf-8"), path.parent.name, handoff=handoff) for path in paths]
    return {"status": "BLOCKED" if any(r["status"] == "BLOCKED" for r in results) else "PASS", "domains": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--handoff", action="store_true")
    args = parser.parse_args()
    result = validate_paths(args.reports, handoff=args.handoff)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
