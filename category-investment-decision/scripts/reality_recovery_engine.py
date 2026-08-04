#!/usr/bin/env python3
"""CLI for build, consumer-update and close REALITY_RECOVERY operations."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from reality_recovery import RecoveryError, apply_consumer_recovery, build_root_batch, close_batch

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        operation = payload.get("operation")
        if operation == "build":
            result = build_root_batch(payload["event"], payload["edges"], payload["consumers"], payload["calibration"])
        elif operation == "update_consumer":
            result = apply_consumer_recovery(payload["batch"], payload["update"])
        elif operation == "close":
            result = close_batch(payload["batch"], payload["closure"])
        else:
            raise RecoveryError("operation must be build, update_consumer or close")
    except (OSError, json.JSONDecodeError, KeyError, RecoveryError) as exc:
        raise SystemExit(f"reality recovery rejected: {exc}") from exc
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
