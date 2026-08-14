#!/usr/bin/env python3
"""Deterministic quality gate for CIDM report depth and completeness.

This is intentionally a structural gate, not a substitute for expert review.
It prevents a long-looking Decision Card from being delivered as diligence.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DETAILED_INTENT = (
    "详细报告", "完整报告", "专业报告", "投资报告", "尽调", "投委会",
    "多国家", "多国", "多平台", "重仓", "具体的产品",
)

REQUIRED_DILIGENCE_SECTIONS = {
    "决策页": ("当前结论", "投资姿态", "决策页"),
    "对象与口径": ("国家", "生命周期", "卖家画像"),
    "证据层": ("证据", "来源", "截至"),
    "反对证据": ("反对", "反例", "替代解释"),
    "五道门槛": ("门槛", "合规", "IP", "安全"),
    "七维评分": ("七维", "市场需求", "竞争", "利润空间"),
    "三场景利润": ("基准", "压力", "乐观"),
    "敏感性": ("敏感性", "翻转点"),
    "国家渠道矩阵": ("国家", "渠道", "矩阵"),
    "行动计划": ("行动", "验证", "里程碑"),
    "停止回滚": ("停止", "回滚", "退出"),
    "证据假设账": ("Evidence", "Assumption", "假设"),
}

REQUIRED_TOP_LEVEL_ORDER = (
    "决策页",
    "决策对象",
    "市场与竞品",
    "候选产品",
    "评分",
    "国家",
    "单位经济",
    "供应链",
    "验证计划",
    "Go / Hold / Stop",
    "Evidence",
    "最终决策",
)

PRODUCT_FIELDS = (
    "产品定义", "目标用户", "场景", "售价", "成本", "竞品", "证据", "假设",
    "风险", "渠道", "评分", "停止",
)

GATE_FIELDS = (
    "当前状态", "关键证据", "反对证据", "判断标准", "放行条件", "停止条件",
    "复核角色", "下一步", "对决策影响",
)

VAGUE_PHRASES = (
    "有潜力", "竞争激烈", "提升质量", "做品牌", "需要差异化", "值得关注",
)


def detect_depth(intent: str) -> str:
    """Return the strongest required delivery tier for a user request."""
    return "Investment Diligence" if any(k in intent for k in DETAILED_INTENT) else "Decision Card"


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term.lower() in text.lower() for term in terms)


def _headings(report: str) -> list[tuple[int, str, int]]:
    headings = []
    for line_no, line in enumerate(report.splitlines(), 1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append((len(match.group(1)), match.group(2), line_no))
    return headings


def _audit_heading_tree(report: str) -> list[dict]:
    findings = []
    headings = _headings(report)
    if not headings or headings[0][0] != 1:
        findings.append({"severity": "BLOCKED", "module": "标题树", "reason": "report must start with a level-1 title"})

    # No heading may jump more than one level, which creates unreadable nesting.
    previous = 0
    for level, title, line_no in headings:
        if previous and level > previous + 1:
            findings.append({"severity": "BLOCKED", "module": "标题树", "reason": f"heading jump at line {line_no}: H{previous} to H{level}"})
        previous = level

    top_titles = [title for level, title, _ in headings if level == 2]
    cursor = -1
    for required in REQUIRED_TOP_LEVEL_ORDER:
        matches = [i for i, title in enumerate(top_titles) if required.lower() in title.lower()]
        if not matches:
            findings.append({"severity": "BLOCKED", "module": "章节顺序", "reason": f"missing top-level section: {required}"})
            continue
        if matches[0] < cursor:
            findings.append({"severity": "BLOCKED", "module": "章节顺序", "reason": f"out-of-order section: {required}"})
        cursor = max(cursor, matches[0])
    return findings


def _audit_product_blocks(report: str) -> list[dict]:
    findings = []
    headings = _headings(report)
    product_positions = [(i, title) for i, (level, title, _) in enumerate(headings) if re.search(r"\bP\d+\s*[：:]", title)]
    for position, title in product_positions:
        next_position = product_positions[product_positions.index((position, title)) + 1][0] if product_positions.index((position, title)) + 1 < len(product_positions) else len(headings)
        block = "\n".join(report.splitlines()[headings[position][2] - 1: (headings[next_position][2] - 1 if next_position < len(headings) else len(report.splitlines()))])
        missing = [field for field in PRODUCT_FIELDS if field not in block]
        if missing:
            findings.append({"severity": "BLOCKED", "module": title, "reason": "missing product fields", "missing": missing})
    if len(product_positions) < 3:
        findings.append({"severity": "BLOCKED", "module": "具体产品", "reason": "fewer than 3 structured product sections"})
    return findings


def _audit_gate_arguments(report: str) -> list[dict]:
    """Require each of the five gates to close an evidence-to-action argument."""
    findings = []
    headings = _headings(report)
    gate_heading = next(((i, title, level) for i, (level, title, _) in enumerate(headings)
                         if "五道门槛" in title), None)
    if gate_heading is None:
        return findings

    start_index, _, _ = gate_heading
    next_h2 = next((i for i in range(start_index + 1, len(headings)) if headings[i][0] <= 2), len(headings))
    start_line = headings[start_index][2] - 1
    end_line = headings[next_h2][2] - 1 if next_h2 < len(headings) else len(report.splitlines())
    gate_text = "\n".join(report.splitlines()[start_line:end_line])

    # The five gates are expected to be named explicitly in the gate table.
    gate_names = ("市场需求", "竞争可进入性", "利润与现金", "合规/支付", "供应/IP/安全")
    for gate in gate_names:
        if gate not in gate_text:
            findings.append({"severity": "BLOCKED", "module": f"门槛:{gate}", "reason": "gate is not explicitly represented"})

    missing = [field for field in GATE_FIELDS if field not in gate_text]
    if missing:
        findings.append({"severity": "BLOCKED", "module": "五道门槛论证闭环", "reason": "missing gate decision fields", "missing": missing})
    return findings


def _audit_tables_and_arguments(report: str) -> list[dict]:
    findings = []
    lines = report.splitlines()
    score_tables = [i for i, line in enumerate(lines) if "评分" in line and "|" in line]
    if score_tables:
        window = "\n".join(lines[score_tables[0]: score_tables[0] + 12])
        for field in ("权重", "原始分", "加权", "置信度"):
            if field not in window:
                findings.append({"severity": "BLOCKED", "module": "评分表", "reason": f"missing score-table column: {field}"})

    if not re.search(r"E\d+", report) or not re.search(r"A\d+", report):
        findings.append({"severity": "BLOCKED", "module": "证据回指", "reason": "Evidence and Assumption IDs are required"})

    paragraph_lengths = []
    current = []
    for line in lines + [""]:
        if line.strip() and not line.startswith("#") and not line.startswith("|") and not line.startswith("-"):
            current.append(line.strip())
        elif current:
            paragraph_lengths.append((len("".join(current)), current[0][:40]))
            current = []
    if any(length > 500 for length, _ in paragraph_lengths):
        findings.append({"severity": "WARN", "module": "段落密度", "reason": "long prose paragraph should be split into bullets/table or argument steps"})

    vague_hits = sorted({phrase for phrase in VAGUE_PHRASES if phrase in report})
    if vague_hits:
        findings.append({"severity": "WARN", "module": "论证表达", "reason": "vague phrases require evidence and action immediately after use", "phrases": vague_hits})

    # Every report must contain an explicit decision chain, not only isolated labels.
    closure_terms = ("证据", "判断", "评分", "门槛", "动作", "成功条件", "停止条件")
    if not all(term in report for term in closure_terms):
        findings.append({"severity": "BLOCKED", "module": "决策闭环", "reason": "missing one or more evidence→judgment→action chain elements", "missing": [term for term in closure_terms if term not in report]})
    return findings


def validate_report(report: str, required_depth: str) -> dict:
    """Validate structural completeness and return machine-readable findings."""
    findings: list[dict] = []
    if required_depth == "Investment Diligence":
        findings.extend(_audit_heading_tree(report))
        findings.extend(_audit_product_blocks(report))
        findings.extend(_audit_gate_arguments(report))
        findings.extend(_audit_tables_and_arguments(report))
        for name, terms in REQUIRED_DILIGENCE_SECTIONS.items():
            if not _has_any(report, terms):
                findings.append({"severity": "BLOCKED", "module": name, "reason": "missing required evidence/module"})

        # A concrete-product report needs at least three identifiable product rows.
        product_ids = set(re.findall(r"\bP\d{1,2}\b", report))
        if len(product_ids) < 3:
            findings.append({"severity": "BLOCKED", "module": "具体产品", "reason": "fewer than 3 product candidates"})

        # Prevent unsupported precision from being presented as confirmed fact.
        numeric_lines = [line for line in report.splitlines() if re.search(r"(?:US\$|€|£|毛利|利润率|成本)", line)]
        assumption_markers = ("假设", "待验证", "估算", "区间", "来源")
        if numeric_lines and not any(marker in report for marker in assumption_markers):
            findings.append({"severity": "BLOCKED", "module": "数字口径", "reason": "numeric claims lack assumption/source markers"})

    blocking = [finding for finding in findings if finding["severity"] == "BLOCKED"]
    return {
        "status": "BLOCKED" if blocking else "PASS_WITH_WARNINGS" if findings else "PASS",
        "required_depth": required_depth,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intent", required=True, help="original user request")
    parser.add_argument("--report", type=Path, help="markdown report to validate")
    args = parser.parse_args()

    required_depth = detect_depth(args.intent)
    result = {"required_depth": required_depth}
    if args.report:
        result.update(validate_report(args.report.read_text(encoding="utf-8"), required_depth))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("status") == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
