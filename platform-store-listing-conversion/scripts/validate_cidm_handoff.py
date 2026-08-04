#!/usr/bin/env python3
"""PLCO-side consumer validator for the CIDM listing-acceptance packet."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KERNEL = ROOT / "category-investment-decision/scripts/opportunity_signals.py"
SPEC = importlib.util.spec_from_file_location("cidm_opportunity_signals", KERNEL)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        packet = json.loads(args.input.read_text(encoding="utf-8"))
        result = module.validate_cidm_plco_packet(packet)
    except (OSError, json.JSONDecodeError, module.ContractError) as exc:
        raise SystemExit(f"CIDM to PLCO packet rejected: {exc}") from exc
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
