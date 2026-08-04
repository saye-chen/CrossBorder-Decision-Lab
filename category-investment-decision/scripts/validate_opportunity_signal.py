#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path
from opportunity_signals import ContractError, validate_signal_card

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        card = json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(validate_signal_card(card), ensure_ascii=False, indent=2, sort_keys=True))
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        raise SystemExit(f"opportunity signal rejected: {exc}") from exc
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
