#!/usr/bin/env python3
"""List contracts, files, validators, tests and evaluations affected by paths."""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalize_path(path: str) -> str:
    """Remove one explicit ./ prefix without corrupting dot-prefixed paths."""
    return path[2:] if path.startswith("./") else path


def analyze(paths: list[str]) -> dict:
    manifest = json.loads((ROOT / "governance/change-impact-manifest.json").read_text(encoding="utf-8"))
    normalized = {normalize_path(str(p)) for p in paths}
    affected = {}
    for contract_id, spec in manifest["contracts"].items():
        watched = set()
        for key in ("authoritative_sources", "consumers", "validators", "tests", "evaluations"):
            watched.update(spec.get(key, []))
        matches = sorted(p for p in normalized if any(p == w or p.startswith(w.rstrip("/") + "/") for w in watched))
        if matches:
            affected[contract_id] = {"changed": matches, **spec}
    return {"changed_paths": sorted(normalized), "affected_contracts": affected,
            "unmapped_paths": sorted(p for p in normalized if not any(p in v["changed"] for v in affected.values()))}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = analyze(args.paths)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for cid, spec in result["affected_contracts"].items():
            print(f"[{cid}] owner={spec['owner']}")
            for key in ("consumers", "validators", "tests", "evaluations"):
                print(f"  {key}: " + ", ".join(spec.get(key, [])))
        if result["unmapped_paths"]:
            print("[unmapped] " + ", ".join(result["unmapped_paths"]))
    return 0 if result["affected_contracts"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
