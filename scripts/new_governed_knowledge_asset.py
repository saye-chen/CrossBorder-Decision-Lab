#!/usr/bin/env python3
"""Create one governed knowledge asset from an approved template."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"dynamic-fact", "constraint", "missing-data-route", "health-finding"}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("kind", choices=sorted(KINDS)); parser.add_argument("destination"); parser.add_argument("--dry-run", action="store_true"); args = parser.parse_args()
    destination = Path(args.destination).resolve()
    allowed_root = (ROOT / "governance/knowledge-quality").resolve()
    if allowed_root not in destination.parents: raise SystemExit("destination must be under governance/knowledge-quality")
    if destination.exists(): raise SystemExit("destination already exists")
    template = ROOT / "governance/knowledge-quality/templates" / f"{args.kind}.json"
    payload = json.loads(template.read_text(encoding="utf-8"))
    if args.dry_run:
        print(json.dumps({"valid": True, "template": str(template.relative_to(ROOT)), "destination": str(destination.relative_to(ROOT)), "payload": payload}))
        return 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(destination)
    return 0


if __name__ == "__main__": raise SystemExit(main())
