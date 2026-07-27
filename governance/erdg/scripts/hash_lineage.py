#!/usr/bin/env python3
"""Generate or verify a canonical SHA-256 hash for an ERDG payload."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from erdg_common import sha256_payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--expect")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        digest = sha256_payload(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    if args.expect and digest != args.expect:
        print(f"INVALID: hash mismatch expected={args.expect} actual={digest}", file=sys.stderr)
        return 1
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
