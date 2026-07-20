#!/usr/bin/env python3
"""Validate the shared contract plus D09-specific advertising invariants."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = ROOT / "category-investment-decision/scripts/validate_decision_contract.py"
SPEC = importlib.util.spec_from_file_location("decision_contract_core", CORE_PATH)
CORE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(CORE)

D09 = "advertising-analysis-measurement-optimization"
QUANTIFIED_ACTIONS = {"scale", "reduce", "pause", "stop", "rebuild", "budget", "bid", "target"}


def validate_d09(payload: dict) -> list[str]:
    """Return advertising-specific errors without weakening the shared kernel."""
    errors: list[str] = []
    owner = payload.get("decision_owner")
    if owner != D09:
        return errors

    context = payload.get("advertising_context")
    if not isinstance(context, dict):
        errors.append("D09 requires advertising_context")
        return errors

    for key in ("country", "platform", "as_of_time", "lifecycle"):
        if not context.get(key):
            errors.append(f"D09 advertising_context requires {key}")

    axes = context.get("axes")
    required_axes = {"traffic_scenario", "control_mode", "billing_mode", "optimization_goal"}
    if not isinstance(axes, dict) or not required_axes.issubset(axes):
        errors.append("D09 requires all four advertising axes")

    maturity = context.get("maturity", {})
    for key in ("data", "tracking", "attribution", "orders"):
        if maturity.get(key) not in {"mature", "immature", "blocked", "unknown"}:
            errors.append(f"D09 maturity requires valid {key} state")

    ledgers = context.get("ledgers", {})
    if not {"platform_attribution", "business_orders", "mature_contribution"}.issubset(ledgers):
        errors.append("D09 requires three separate ledgers")

    action = payload.get("action", {})
    action_type = str(action.get("type", "")).lower()
    quantified = any(token in action_type for token in QUANTIFIED_ACTIONS) or action.get("amount") is not None
    if quantified:
        required = set(payload.get("required_calculation_ids", []))
        if not required:
            errors.append("D09 quantified action requires deterministic calculation ids")
        if action.get("stop_condition") in (None, ""):
            errors.append("D09 quantified action requires stop_condition")
        if action.get("rollback") in (None, ""):
            errors.append("D09 quantified action requires rollback")

    forbidden = " ".join(map(str, payload.get("forbidden_claims", []))).lower()
    if context.get("incrementality_status") != "validated" and "platform roas is incremental" in forbidden:
        pass
    elif context.get("incrementality_status") != "validated" and payload.get("claims_incremental") is True:
        errors.append("D09 cannot claim incrementality without validated design")

    if any(value != "mature" for value in maturity.values()) and action_type in {"scale", "stop"}:
        if action.get("status") not in {"proposed", "inconclusive", "blocked"}:
            errors.append("D09 immature evidence cannot directly validate Scale/Stop")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("INVALID: root must be an object", file=sys.stderr)
        return 2
    errors = CORE.validate(payload) + validate_d09(payload)
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 1
    print("PASS: shared and D09-specific contracts are complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
