#!/usr/bin/env python3
"""Compare two CIM snapshot JSON documents without inventing semantics."""

import argparse
import json
from pathlib import Path


def flatten(value, prefix=""):
    out = {}
    if isinstance(value, dict):
        for key, item in value.items():
            out.update(flatten(item, f"{prefix}.{key}" if prefix else key))
    else:
        out[prefix] = value
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous", required=True)
    parser.add_argument("--current", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    previous = json.loads(Path(args.previous).read_text(encoding="utf-8"))
    current = json.loads(Path(args.current).read_text(encoding="utf-8"))
    old, new = flatten(previous), flatten(current)
    changes = []
    for field in sorted(set(old) | set(new)):
        before, after = old.get(field), new.get(field)
        if before == after:
            continue
        item = {"field": field, "before": before, "after": after}
        if isinstance(before, (int, float)) and isinstance(after, (int, float)):
            item["absolute_change"] = after - before
            item["relative_change"] = None if before == 0 else (after - before) / abs(before)
        changes.append(item)
    result = {
        "previous_snapshot_at": previous.get("snapshot_at"),
        "current_snapshot_at": current.get("snapshot_at"),
        "product_id": current.get("product_id") or previous.get("product_id"),
        "changes": changes,
    }
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
