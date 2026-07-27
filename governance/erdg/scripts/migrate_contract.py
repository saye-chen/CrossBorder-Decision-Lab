#!/usr/bin/env python3
"""Create an ERDG shadow envelope from an established domain contract without changing its business decision."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from erdg_common import sha256_payload


def migrate(payload: dict[str, Any]) -> dict[str, Any]:
    required = ("decision_owner", "decision_type", "objects", "runtime_versions")
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValueError(f"legacy contract missing {missing}")
    result = deepcopy(payload)
    result["erdg_contract"] = "ERDG-CONTRACT-2026.01"
    result["external_write"] = False
    result["migration"] = {
        "mode": "shadow_dual_read",
        "source_contract_hash": sha256_payload(payload),
        "business_decision_changed": False,
        "rollback": "legacy compatibility validator",
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(migrate(payload), ensure_ascii=False, indent=2))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
