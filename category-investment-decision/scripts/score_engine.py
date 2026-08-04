#!/usr/bin/env python3
"""Deterministic seven-dimension category score with sensitivity and redline gates."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

WEIGHTS = {
    "market_demand": 20,
    "competitive_entry": 20,
    "profit_space": 20,
    "content_communication": 10,
    "supply_control": 10,
    "risk_control": 10,
    "opportunity_window": 10,
}

def evaluate_score(payload):
    scores = payload.get("scores")
    if not isinstance(scores, dict) or set(scores) != set(WEIGHTS):
        raise ValueError(f"scores must contain exactly: {sorted(WEIGHTS)}")
    clean = {}
    for key, value in scores.items():
        try: number = float(value)
        except (TypeError, ValueError) as exc: raise ValueError(f"score must be numeric: {key}") from exc
        if not math.isfinite(number) or not 0 <= number <= 10: raise ValueError(f"score must be finite and between 0 and 10: {key}")
        clean[key] = number
    caps = payload.get("sensitivity_caps", {})
    if not isinstance(caps, dict): raise ValueError("sensitivity_caps must be an object")
    applied_caps = {}
    for key, cap in caps.items():
        if key not in clean or isinstance(cap,bool) or not isinstance(cap,(int,float)) or not math.isfinite(cap) or not 0 <= cap <= 10: raise ValueError(f"invalid sensitivity cap: {key}")
        if clean[key] > cap: clean[key]=float(cap); applied_caps[key]=float(cap)
    redlines = payload.get("hard_redlines", [])
    if not isinstance(redlines,list) or any(not isinstance(x,str) or not x for x in redlines): raise ValueError("hard_redlines must be a list of nonempty strings")
    total=round(sum(clean[k]*WEIGHTS[k]/10 for k in WEIGHTS),2)
    band = "建议进入" if total >= 80 else "谨慎小测" if total >= 65 else "仅观察/内容测款" if total >= 50 else "不建议进入"
    return {"decision_status":"Blocked" if redlines else "Scored","decision_band":"不建议进入" if redlines else band,"weighted_score":total,"scores_after_caps":clean,"applied_caps":applied_caps,"hard_redlines":sorted(set(redlines)),"weight_total":sum(WEIGHTS.values())}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid score input: {exc}") from exc
    try: result = evaluate_score(payload)
    except ValueError as exc: raise SystemExit(str(exc)) from exc
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
