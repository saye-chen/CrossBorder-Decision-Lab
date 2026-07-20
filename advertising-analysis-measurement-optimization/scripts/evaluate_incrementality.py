#!/usr/bin/env python3
"""Evaluate two-arm ITT incrementality with maturity and guardrail gates."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def finite(value: object, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def arm(raw: dict, name: str) -> dict:
    n = finite(raw.get("n"), f"{name}.n")
    value = finite(raw.get("value"), f"{name}.value")
    variance = finite(raw.get("variance", 0), f"{name}.variance")
    assigned = finite(raw.get("assigned", n), f"{name}.assigned")
    exposed = finite(raw.get("exposed", n), f"{name}.exposed")
    if n <= 1 or assigned < n or exposed < 0 or exposed > assigned or variance < 0:
        raise ValueError(f"invalid {name} sample, assignment, exposure, or variance")
    return {"n": n, "value": value, "variance": variance, "assigned": assigned, "exposed": exposed}


def evaluate(payload: dict) -> dict:
    treatment = arm(payload.get("treatment", {}), "treatment")
    control = arm(payload.get("control", {}), "control")
    z = finite(payload.get("z", 1.96), "z")
    spend = finite(payload.get("incremental_spend", 0), "incremental_spend")
    margin = finite(payload.get("contribution_margin_rate", 1), "contribution_margin_rate")
    if z <= 0 or spend < 0 or not 0 <= margin <= 1:
        raise ValueError("invalid z, incremental_spend, or contribution_margin_rate")

    maturity = payload.get("maturity", {})
    maturity_states = {key: maturity.get(key, "mature") for key in ("assignment", "exposure", "outcome", "refund")}
    invalid_maturity = {key: value for key, value in maturity_states.items() if value not in {"mature", "immature", "blocked"}}
    if invalid_maturity:
        raise ValueError(f"invalid maturity states: {invalid_maturity}")

    treatment_mean = treatment["value"] / treatment["n"]
    control_mean = control["value"] / control["n"]
    effect = treatment_mean - control_mean
    standard_error = math.sqrt(treatment["variance"] / treatment["n"] + control["variance"] / control["n"])
    lower, upper = effect - z * standard_error, effect + z * standard_error
    incremental_value = effect * treatment["assigned"]
    contribution = incremental_value * margin - spend

    guardrails = []
    for item in payload.get("guardrails", []):
        observed = finite(item.get("observed"), f"guardrail.{item.get('id')}.observed")
        limit = finite(item.get("limit"), f"guardrail.{item.get('id')}.limit")
        direction = item.get("direction", "max")
        passed = observed <= limit if direction == "max" else observed >= limit
        guardrails.append({"id": item.get("id"), "passed": passed, "observed": observed, "limit": limit})

    exposure_rate = treatment["exposed"] / treatment["assigned"] if treatment["assigned"] else 0
    blockers = [key for key, value in maturity_states.items() if value != "mature"]
    if exposure_rate < finite(payload.get("minimum_exposure_rate", 0), "minimum_exposure_rate"):
        blockers.append("low_exposure")
    if any(not item["passed"] for item in guardrails):
        blockers.append("guardrail")

    if blockers:
        decision = "Inconclusive" if "guardrail" not in blockers else "Stop"
    elif lower > 0 and contribution > 0:
        decision = "Go"
    elif upper < 0 or contribution < 0 and upper <= 0:
        decision = "Stop"
    else:
        decision = "Inconclusive"

    return {
        "estimand": "intention_to_treat",
        "treatment_mean": treatment_mean,
        "control_mean": control_mean,
        "incremental_value_per_unit": effect,
        "standard_error": standard_error,
        "ci": [lower, upper],
        "incremental_value": incremental_value,
        "incremental_contribution": contribution,
        "iroas": incremental_value / spend if spend else None,
        "treatment_exposure_rate": exposure_rate,
        "maturity": maturity_states,
        "guardrails": guardrails,
        "blockers": blockers,
        "decision": decision,
        "limitations": [
            "normal approximation; use cluster/geo robust inference when assignment is clustered",
            "ITT does not identify individual treatment effects",
            "interference, noncompliance and sequential peeking require separate design analysis",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = evaluate(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
