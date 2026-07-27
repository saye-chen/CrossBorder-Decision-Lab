#!/usr/bin/env python3
"""Validate ERDG seven-mode coverage and substantive expert-report depth."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVAL = ROOT / "evaluations/erdg"
MODES = {"single_skill", "cross_skill", "composite", "multi_turn", "complex", "extreme", "stress"}
REPORTS = {
    "single_skill": "single-skill-economic-review.md",
    "cross_skill": "cross-skill-conflict.md",
    "composite": "composite-launch.md",
    "multi_turn": "multi-turn-recalculation.md",
    "complex": "complex-multi-entity.md",
    "extreme": "extreme-safety-recall.md",
    "stress": "stress-lineage.md",
}
CASE_FIELDS = {
    "id", "mode", "title", "business_context", "decision_question", "mechanisms",
    "required_inputs", "evidence_conflicts", "calculations", "expected_states",
    "actions", "success_stop_rollback", "forbidden",
}
COMMON_MARKERS = (
    "ERDG-2026.01", "controlled pilot", "对象", "版本", "证据", "反证", "冲突",
    "主权", "计算", "风险", "候选", "不行动", "动作", "成功", "停止", "回滚",
    "状态", "血缘", "L4",
)
MODE_MARKERS = {
    "single_skill": ("E0", "E7", "边际", "不可比"),
    "cross_skill": ("Envelope", "partially_accepted", "部分失败", "目标主权域"),
    "composite": ("红线瀑布", "参与域", "动作顺序", "选择性重算"),
    "multi_turn": ("Information Delta", "Preserve", "Recompute", "唯一"),
    "complex": ("法人", "货权", "合并", "守恒"),
    "extreme": ("召回", "冻结", "不可补偿", "退出"),
    "stress": ("十万", "千节点", "幂等", "循环"),
}


def validate() -> list[str]:
    errors: list[str] = []
    catalog = json.loads((EVAL / "evaluation-catalog.json").read_text(encoding="utf-8"))
    if catalog.get("runtime") != "ERDG-2026.01":
        errors.append("catalog runtime mismatch")
    cases = catalog.get("cases", [])
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        errors.append("duplicate case ids")
    for mode in MODES:
        selected = [case for case in cases if case.get("mode") == mode]
        if len(selected) < 2:
            errors.append(f"{mode}: requires at least two decision-distinct cases")
        if len({case.get("title") for case in selected}) != len(selected):
            errors.append(f"{mode}: duplicate titles")
    for case in cases:
        missing = CASE_FIELDS - set(case)
        if missing:
            errors.append(f"{case.get('id')}: missing {sorted(missing)}")
        for field in CASE_FIELDS - {"id", "mode", "title", "business_context", "decision_question"}:
            if not isinstance(case.get(field), list) or not case[field]:
                errors.append(f"{case.get('id')}: {field} must be non-empty list")
        if len(case.get("mechanisms", [])) < 3 or len(case.get("forbidden", [])) < 3:
            errors.append(f"{case.get('id')}: insufficient mechanism or failure depth")
    reports = {}
    for mode, filename in REPORTS.items():
        path = EVAL / "golden" / filename
        if not path.is_file():
            errors.append(f"{mode}: missing report")
            continue
        text = path.read_text(encoding="utf-8")
        reports[mode] = text
        if len(text) < 700:
            errors.append(f"{mode}: report too shallow")
        for marker in COMMON_MARKERS + MODE_MARKERS[mode]:
            if marker not in text:
                errors.append(f"{mode}: missing depth marker {marker}")
        if len(re.findall(r"^## ", text, re.MULTILINE)) < 7:
            errors.append(f"{mode}: insufficient independent sections")
    if len({text for text in reports.values()}) != len(reports):
        errors.append("reports are not decision-distinct")
    turns = json.loads((EVAL / "multiturn-challenges.json").read_text(encoding="utf-8"))
    if len(turns) < 8:
        errors.append("multi-turn requires at least eight challenges")
    for turn in turns:
        for field in ("delta_type", "changed_fields", "must_preserve", "must_recompute", "must_answer", "forbidden"):
            if field not in turn:
                errors.append(f"turn {turn.get('turn')}: missing {field}")
        if not turn.get("must_answer") or not turn.get("forbidden"):
            errors.append(f"turn {turn.get('turn')}: insufficient depth")
    recomputation = EVAL / "report-recomputation-manifest.json"
    if not recomputation.is_file():
        errors.append("missing report recomputation manifest")
    else:
        bindings = json.loads(recomputation.read_text(encoding="utf-8")).get("checks", [])
        if {row.get("mode") for row in bindings} != MODES:
            errors.append("report recomputation does not cover all seven modes")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print("ERDG expert-depth validation passed for 7 modes, 14 cases and 7 reports.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
