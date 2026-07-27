#!/usr/bin/env python3
"""Evaluate ERDG non-compensable redlines and comparable expected loss."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from erdg_common import decimal_string, decimal_value

REDLINE_TYPES = {
    "legal", "safety", "ip_block", "privacy_authorization", "unapproved_negative_contribution",
    "cash_rupture", "identity_rights_reconciliation", "irreversible_action_authorization",
    "unreproducible_calculation",
}


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    risks = payload.get("risks")
    if not isinstance(risks, list):
        raise ValueError("risks must be a list")
    blocked = []
    expected_loss = Decimal("0")
    unknown_probability = []
    for index, risk in enumerate(risks):
        if not isinstance(risk, dict) or not risk.get("risk_id") or not risk.get("risk_type"):
            raise ValueError(f"risks[{index}] requires risk_id and risk_type")
        is_redline = bool(risk.get("redline")) or risk["risk_type"] in REDLINE_TYPES
        if is_redline and risk.get("status") not in {"mitigated", "closed"}:
            blocked.append(risk["risk_id"])
            continue
        probability = risk.get("probability")
        impact = risk.get("impact")
        if probability is None:
            unknown_probability.append(risk["risk_id"])
            continue
        p = decimal_value(probability, f"risks[{index}].probability")
        if not Decimal("0") <= p <= Decimal("1"):
            raise ValueError(f"risks[{index}].probability must be within [0,1]")
        loss = decimal_value(impact, f"risks[{index}].impact")
        if loss < 0:
            raise ValueError(f"risks[{index}].impact must be a non-negative loss magnitude")
        expected_loss += p * loss
    return {
        "contract": "ERDG-CONTRACT-2026.01",
        "status": "blocked" if blocked else ("inconclusive" if unknown_probability else "comparable"),
        "blocked_redlines": blocked,
        "unknown_probability": unknown_probability,
        "expected_loss": decimal_string(expected_loss),
        "redlines_not_compensated": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(evaluate(payload), ensure_ascii=False, indent=2))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
