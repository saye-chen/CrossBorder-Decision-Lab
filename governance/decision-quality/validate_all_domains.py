#!/usr/bin/env python3
"""Audit every registered domain and optionally validate a joint report bundle."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = Path(__file__).with_name("domain-registry.json")
CONTRACT_MARKERS = ("decision-quality/validate_domain_quality.py", "decision-quality/validate_all_domains.py", "DQ-CONTRACT-2026.08")


def audit_registry() -> dict:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    findings = []
    for domain in registry["required_domains"]:
        skill = ROOT / domain / "SKILL.md"
        if not skill.exists():
            findings.append({"domain": domain, "reason": "missing SKILL.md"})
            continue
        text = skill.read_text(encoding="utf-8")
        if not any(marker in text for marker in CONTRACT_MARKERS):
            findings.append({"domain": domain, "reason": "shared decision-quality contract is not wired into SKILL.md"})
    return {"status": "BLOCKED" if findings else "PASS", "findings": findings, "checked": len(registry["required_domains"])}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", nargs="*", type=Path)
    parser.add_argument("--handoff", action="store_true")
    args = parser.parse_args()
    registry_result = audit_registry()
    result = {"registry": registry_result}
    if args.reports:
        validator = Path(__file__).with_name("validate_domain_quality.py")
        command = [sys.executable, str(validator), *(str(p) for p in args.reports)]
        if args.handoff:
            command.append("--handoff")
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        result["bundle"] = json.loads(completed.stdout)
    blocked = registry_result["status"] == "BLOCKED" or result.get("bundle", {}).get("status") == "BLOCKED"
    result["status"] = "BLOCKED" if blocked else "PASS"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
