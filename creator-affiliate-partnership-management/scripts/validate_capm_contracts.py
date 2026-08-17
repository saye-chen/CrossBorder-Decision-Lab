#!/usr/bin/env python3
"""Cross-field CAPM contract invariants that JSON Schema cannot express alone."""
from __future__ import annotations
import argparse, json
from datetime import datetime
from pathlib import Path
from capm_common import emit, load_json
from validate_schema_instance import validate

ROOT = Path(__file__).resolve().parents[1]

def instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None: raise ValueError("timezone required")
    return parsed

def check(name: str, data: dict) -> dict:
    schema_path = ROOT / "schemas" / f"{name}.schema.json"
    if not schema_path.is_file(): raise ValueError(f"unknown contract: {name}")
    errors = validate(data, json.loads(schema_path.read_text(encoding="utf-8")))
    for low, mid, high in (("mature_contribution_low","mature_contribution_mid","mature_contribution_high"),("demand_low","demand_mid","demand_high")):
        if all(key in data for key in (low, mid, high)) and not data[low] <= data[mid] <= data[high]: errors.append(f"$.{low},{mid},{high}:interval_order")
    for start, end in (("effective_at","expires_at"),("valid_from","expires_at"),("window_start","window_end")):
        if start in data and end in data and instant(data[start]) >= instant(data[end]): errors.append(f"$.{start},{end}:time_order")
    allowed = set(data.get("allowed_paid_uses", data.get("allowed_uses", [])))
    forbidden = set(data.get("forbidden_uses", []))
    if allowed & forbidden: errors.append("$.allowed_forbidden:overlap")
    return {"valid":not errors,"contract":name,"errors":errors}

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("contract"); p.add_argument("input",nargs="?"); a=p.parse_args(); result=check(a.contract,load_json(a.input)); emit(result); raise SystemExit(0 if result["valid"] else 1)
