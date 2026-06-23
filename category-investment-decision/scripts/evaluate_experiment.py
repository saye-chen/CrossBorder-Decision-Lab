#!/usr/bin/env python3
"""Calculate launch experiment metrics and evaluate preregistered investment gates."""

from __future__ import annotations

import argparse
import json
import math
import operator
import sys
from pathlib import Path
from typing import Any, Callable


OPERATORS: dict[str, Callable[[float, float], bool]] = {
    ">=": operator.ge,
    ">": operator.gt,
    "<=": operator.le,
    "<": operator.lt,
    "==": operator.eq,
}


def ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a non-negative number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a non-negative number") from exc
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"{name} must be a non-negative number")
    return number


def calculate_metrics(payload: dict[str, Any]) -> dict[str, float | None]:
    raw_counts = payload.get("counts", {})
    if not isinstance(raw_counts, dict):
        raise ValueError("counts must be an object")
    names = ["impressions", "clicks", "landing_visits", "leads", "add_to_cart", "checkout_started", "purchases", "refunds"]
    counts = {name: finite_number(raw_counts.get(name, 0), f"counts.{name}") for name in names}
    spend = finite_number(payload.get("spend", 0), "spend")
    revenue = finite_number(payload.get("revenue", 0), "revenue")

    if counts["clicks"] > counts["impressions"]:
        raise ValueError("clicks cannot exceed impressions")
    if counts["landing_visits"] > counts["clicks"]:
        raise ValueError("landing_visits cannot exceed clicks")
    if counts["leads"] > counts["landing_visits"]:
        raise ValueError("leads cannot exceed landing_visits")
    if counts["add_to_cart"] > counts["landing_visits"]:
        raise ValueError("add_to_cart cannot exceed landing_visits")
    if counts["checkout_started"] > counts["landing_visits"]:
        raise ValueError("checkout_started cannot exceed landing_visits")
    if counts["purchases"] > counts["landing_visits"]:
        raise ValueError("purchases cannot exceed landing_visits")
    if counts["refunds"] > counts["purchases"]:
        raise ValueError("refunds cannot exceed purchases")

    metrics: dict[str, float | None] = dict(counts)
    metrics.update(
        {
            "spend": spend,
            "revenue": revenue,
            "ctr": ratio(counts["clicks"], counts["impressions"]),
            "landing_rate": ratio(counts["landing_visits"], counts["clicks"]),
            "lead_rate": ratio(counts["leads"], counts["landing_visits"]),
            "add_to_cart_rate": ratio(counts["add_to_cart"], counts["landing_visits"]),
            "checkout_rate": ratio(counts["checkout_started"], counts["landing_visits"]),
            "purchase_rate": ratio(counts["purchases"], counts["landing_visits"]),
            "refund_rate": ratio(counts["refunds"], counts["purchases"]),
            "cpc": ratio(spend, counts["clicks"]),
            "cost_per_lead": ratio(spend, counts["leads"]),
            "cac": ratio(spend, counts["purchases"]),
            "aov": ratio(revenue, counts["purchases"]),
            "roas": ratio(revenue, spend),
        }
    )
    return metrics


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    metrics = calculate_metrics(payload)
    minimum_results = []
    minimums = payload.get("minimums", {})
    if not isinstance(minimums, dict):
        raise ValueError("minimums must be an object")
    for metric, threshold_value in minimums.items():
        if metric not in metrics:
            raise ValueError(f"unknown minimum metric: {metric}")
        threshold = finite_number(threshold_value, f"minimums.{metric}")
        value = metrics[metric]
        passed = value is not None and value >= threshold
        minimum_results.append({"metric": metric, "value": value, "required": threshold, "passed": passed})

    gate_results = []
    gates = payload.get("gates", [])
    if not isinstance(gates, list):
        raise ValueError("gates must be an array")
    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            raise ValueError(f"gates[{index}] must be an object")
        metric = gate.get("metric")
        op = gate.get("operator")
        kind = gate.get("kind", "primary")
        if metric not in metrics:
            raise ValueError(f"unknown gate metric: {metric}")
        if op not in OPERATORS:
            raise ValueError(f"unsupported operator: {op}")
        if kind not in {"primary", "redline"}:
            raise ValueError(f"unsupported gate kind: {kind}")
        threshold = finite_number(gate.get("threshold"), f"gates[{index}].threshold")
        value = metrics[metric]
        passed = value is not None and OPERATORS[op](value, threshold)
        gate_results.append({"metric": metric, "value": value, "operator": op, "threshold": threshold, "kind": kind, "passed": passed})

    if any(not result["passed"] for result in minimum_results):
        decision = "INCONCLUSIVE"
        reason = "Minimum evidence requirements were not met."
    elif any(result["kind"] == "redline" and not result["passed"] for result in gate_results):
        decision = "STOP"
        reason = "At least one preregistered redline failed."
    else:
        primary = [result for result in gate_results if result["kind"] == "primary"]
        if not primary:
            decision = "INCONCLUSIVE"
            reason = "No primary decision gates were provided."
        elif all(result["passed"] for result in primary):
            decision = "CONTINUE"
            reason = "All preregistered primary gates passed."
        else:
            decision = "ITERATE"
            reason = "Minimum evidence was met, but one or more primary gates failed."

    return {
        "experiment": payload.get("experiment", "unnamed"),
        "currency": payload.get("currency"),
        "decision": decision,
        "reason": reason,
        "metrics": metrics,
        "minimums": minimum_results,
        "gates": gate_results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Experiment JSON input")
    parser.add_argument("--output", type=Path, help="Write JSON here instead of stdout")
    parser.add_argument("--pretty", action="store_true", help="Indent JSON output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("input must be a JSON object")
        result = evaluate(payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
