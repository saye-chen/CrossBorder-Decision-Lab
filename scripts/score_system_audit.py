#!/usr/bin/env python3
"""Score a generated audit evidence package using CBDS-AUDIT-2026.07-v1."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


WEIGHTS = {
    "A_architecture_governance": 12,
    "B_reproducibility": 12,
    "C_l1_structure": 8,
    "D_l2_contract_determinism": 12,
    "E_l3_expert_depth": 16,
    "F_cross_domain_sovereignty": 12,
    "G_scenario_resilience_capacity": 10,
    "H_security_release_supply_chain": 8,
    "I_l4_real_world_validity": 10,
}


def score(evidence: dict) -> dict:
    checks = {row["id"]: row["status"] == "PASS" for row in evidence.get("checks", [])}
    full = checks.get("full-repository-audit", False)
    compliance = checks.get("release-compliance", False)
    capacity = checks.get("erdg-capacity", False)
    security = evidence.get("security_release_scan", {}).get("status") == "PASS"
    impact = evidence.get("change_impact", {}).get("status") == "PASS"
    clean = evidence.get("workspace_clean") is True
    dimensions = {
        "A_architecture_governance": 12 if full else 0,
        "B_reproducibility": 12 if clean and full else 9 if full else 0,
        "C_l1_structure": 8 if full else 0,
        "D_l2_contract_determinism": 12 if full else 0,
        "E_l3_expert_depth": 14 if full else 0,
        "F_cross_domain_sovereignty": 12 if full else 0,
        "G_scenario_resilience_capacity": 10 if full and capacity else 8 if full else 0,
        "H_security_release_supply_chain": (
            7 if security and compliance and impact else 4 if security else 0
        ),
        "I_l4_real_world_validity": 0,
    }
    hard_gates = {
        "G0_fixed_audit_object": "PASS" if clean else "PARTIAL_DIRTY_WORKTREE",
        "G1_redline_security": "PASS" if security and compliance else "FAIL",
        "G2_l1_l2_baseline": "PASS" if full else "FAIL",
        "G3_sovereignty_lineage": "PASS" if full else "FAIL",
        "G4_change_impact_closure": "PASS" if impact else "FAIL",
        "G5_l4_real_replay": "CONTROLLED_EXTERNAL_GATE",
    }
    total = sum(dimensions.values())
    grade = "A+" if total >= 95 else "A" if total >= 90 else "B" if total >= 80 else "C" if total >= 70 else "D" if total >= 60 else "F"
    return {
        "audit_standard_version": "CBDS-AUDIT-2026.07-v1",
        "score": total,
        "maximum": 100,
        "grade": grade,
        "maturity": "controlled pilot",
        "dimensions": {
            key: {"score": dimensions[key], "maximum": WEIGHTS[key]} for key in WEIGHTS
        },
        "hard_gates": hard_gates,
        "production_ready": False,
        "limitations": [
            "L3 retains two points for independent expert review and broader platform-method evidence.",
            "H retains one point for accountable owner license/privacy review.",
            "I remains zero until authorized real replay and independent outcome review close L4.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = score(json.loads(args.evidence.read_text(encoding="utf-8")))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        if args.output.exists():
            raise SystemExit(f"Refusing to overwrite: {args.output}")
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
