#!/usr/bin/env python3
"""CLI for deterministic OSL-v1 signal-family evaluation."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from opportunity_models import ModelError, evaluate

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="JSON with signal_type, data and calibrated thresholds")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if set(payload) != {"signal_type", "data", "calibration"}:
            raise ModelError("input must contain exactly signal_type, data and calibration")
        result = evaluate(payload["signal_type"], payload["data"], payload["calibration"])
    except (OSError, json.JSONDecodeError, ModelError) as exc:
        raise SystemExit(f"opportunity model rejected: {exc}") from exc
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
