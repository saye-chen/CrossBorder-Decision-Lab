#!/usr/bin/env python3
"""Score decision reports against the repository expert-release contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

DIMENSIONS = {
    "professional_completeness": (20, ["决策结论", "对象与边界", "适用范围", "生命周期", "缺失数据"]),
    "evidence_traceability": (15, ["证据与反证", "E1", "A1", "证据截止", "替代解释"]),
    "economics_calculation": (15, ["经济与计算", "C1", "输入", "币种", "可复算"]),
    "root_cause_reasoning": (10, ["根因", "反证", "替代解释", "推翻条件"]),
    "decision_sovereignty": (10, ["主权与联动", "主决策 Skill", "proposed", "允许用途", "禁止用途"]),
    "actionability": (10, ["行动计划", "动作对象", "幅度", "责任人", "观察窗"]),
    "stop_and_rollback": (10, ["成功条件", "停止条件", "回滚"]),
    "localization_current_facts": (5, ["国家/平台", "动态事实", "核验日期"]),
    "clarity_readability": (5, ["执行摘要", "一句话理由", "自检摘要"]),
}

REDLINES = {
    "unresolved_redline_scale": r"未解决红线\s*[:：]\s*是[\s\S]{0,300}(Scale|重仓|立即放量)",
    "unreproducible_economics": r"可复算\s*[:：]\s*否",
    "authority_violation": r"主权越界\s*[:：]\s*是",
    "causal_overclaim": r"因果越界\s*[:：]\s*是",
    "fabricated_fact": r"伪造事实\s*[:：]\s*是",
    "privacy_violation": r"隐私违规\s*[:：]\s*是",
}

REQUIRED_HEADINGS = ["执行摘要", "对象与边界", "证据与反证", "经济与计算", "根因", "主权与联动", "行动计划", "国家/平台与动态事实", "自检摘要"]

FULL_REQUIRED_HEADINGS = REQUIRED_HEADINGS + ["门槛与评分", "证据台账", "假设台账", "计算台账", "决策推导"]
PLACEHOLDER_PATTERNS = [r"待补充", r"\bTBD\b", r"\bTODO\b", r"示例内容", r"这里填写", r"^\s*略\s*$", r"[（\[]略[）\]]"]

def section(text: str, heading: str) -> str:
    match = re.search(rf"^#+\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^#+\s+|\Z)", text, re.M)
    return match.group(1).strip() if match else ""

def semantic_checks(text: str, profile: str) -> list[str]:
    errors = []
    for heading in REQUIRED_HEADINGS:
        body = section(text, heading)
        if len(re.sub(r"[`#|*\s]", "", body)) < 20:
            errors.append(f"shallow_section:{heading}")
    ids = {kind: set(re.findall(rf"(?<![A-Z0-9]){kind}(\d+)(?!\d)", text)) for kind in "EAC"}
    if any(not values for values in ids.values()):
        errors.append("missing_ledger_ids")
    if re.search("|".join(PLACEHOLDER_PATTERNS), text, re.I):
        errors.append("placeholder_content")
    if "可复算：是" in text and not ("输入哈希" in text and "输出哈希" in text and re.search(r"计算器|\.py", text)):
        errors.append("unsupported_reproducibility_claim")
    if re.search(r"决策结论[^\n]{0,40}(Scale|重仓|立即放量)", text, re.I) and re.search(r"(边际贡献|贡献利润)[^\n]{0,30}(为负|<\s*0|负数)", text):
        errors.append("scale_conflicts_with_negative_economics")
    if re.search(r"(代理信号|proxy)[^\n]{0,40}(已确认事实|observed fact)", text, re.I):
        errors.append("proxy_promoted_to_fact")
    if profile == "full":
        if len(text.splitlines()) < 50 or len(text) < 1200:
            errors.append("full_report_too_short")
        for heading in FULL_REQUIRED_HEADINGS:
            if not section(text, heading):
                errors.append(f"missing_full_section:{heading}")
        for term in ["支持证据", "反对证据", "最弱假设", "成功条件", "停止条件", "回滚", "置信度", "决策影响"]:
            if term not in text:
                errors.append(f"missing_full_semantic:{term}")
    return errors


def score_report(text: str, profile: str = "fixture") -> dict:
    dimensions = {}
    for name, (weight, required) in DIMENSIONS.items():
        present = [item for item in required if item in text]
        value = round(weight * len(present) / len(required), 2)
        dimensions[name] = {"score": value, "max": weight, "missing": [x for x in required if x not in text]}
    redlines = [name for name, pattern in REDLINES.items() if re.search(pattern, text, re.I)]
    missing_headings = [heading for heading in REQUIRED_HEADINGS if not re.search(rf"^#+\s+{re.escape(heading)}\s*$", text, re.M)]
    if missing_headings:
        redlines.append("missing_required_sections")
    total = round(sum(item["score"] for item in dimensions.values()), 2)
    critical = ["evidence_traceability", "economics_calculation", "decision_sovereignty", "actionability", "stop_and_rollback"]
    critical_ok = all(dimensions[name]["score"] >= dimensions[name]["max"] * .8 for name in critical)
    refs_ok = bool(re.search(r"E\d+", text) and re.search(r"A\d+", text) and re.search(r"C\d+", text))
    semantic_errors = semantic_checks(text, profile)
    threshold = 100 if profile == "full" else 85
    result = "PASS" if total >= threshold and critical_ok and refs_ok and not redlines and not semantic_errors else "FAIL"
    return {"result": result, "profile": profile, "score": total, "dimensions": dimensions, "redlines": redlines, "semantic_errors": semantic_errors, "missing_required_sections": missing_headings, "ledger_refs_ok": refs_ok}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--profile", choices=["fixture", "contract", "full"], default="contract")
    args = parser.parse_args()
    result = score_report(args.input.read_text(encoding="utf-8"), args.profile)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    raise SystemExit(0 if result["result"] == "PASS" else 2)


if __name__ == "__main__":
    main()
