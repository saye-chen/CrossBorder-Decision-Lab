#!/usr/bin/env python3
"""Validate OSL-specific professional report depth beyond the generic report gate."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REQUIRED_SECTIONS = ["数据运行模式", "机会信号卡", "跨域专业复核", "Do Not Do Yet", "失效与恢复"]
REQUIRED_TERMS = [
    "online_realtime", "reserved_interface", "mcp_required=false", "candidate",
    "CIM", "PPFC", "SPPQ", "LIFD", "PLCO", "CIDM", "REALITY_RECOVERY",
    "机制", "计算", "反证", "允许用途", "禁止用途", "停止条件", "回滚",
]

def section(text: str, heading: str) -> str:
    match = re.search(rf"^#+\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^#+\s+|\Z)", text, re.M)
    return match.group(1).strip() if match else ""

def validate(text: str) -> list[str]:
    errors: list[str] = []
    for heading in REQUIRED_SECTIONS:
        body = section(text, heading)
        if len(re.sub(r"[`#|*\s]", "", body)) < 60:
            errors.append(f"missing_or_shallow_section:{heading}")
    for term in REQUIRED_TERMS:
        if term not in text:
            errors.append(f"missing_term:{term}")
    cross = section(text, "跨域专业复核")
    for domain in ["CIM", "PPFC", "SPPQ", "LIFD", "PLCO", "CIDM"]:
        if not re.search(rf"\|\s*{domain}\s*\|[^\n]{{30,}}", cross):
            errors.append(f"shallow_domain_review:{domain}")
    if "决策结论：`Do Not Do Yet`" not in text:
        errors.append("unsafe_or_missing_decision")
    if "资本承诺为 0" not in text:
        errors.append("missing_zero_commitment")
    return errors

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    errors = validate(args.input.read_text(encoding="utf-8"))
    if errors:
        raise SystemExit("\n".join(errors))
    print("OSL professional report: PASS")

if __name__ == "__main__":
    main()
