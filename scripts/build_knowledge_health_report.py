#!/usr/bin/env python3
"""Build an auditable health report without mutating governance state."""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("kq", ROOT / "scripts/validate_knowledge_quality.py")
KQ = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(KQ)


def build(as_of: dt.date) -> dict:
    data = KQ.load(KQ.REGISTER)
    errors = KQ.validate(data, as_of)
    findings = []
    for index, error in enumerate(errors, 1):
        findings.append({
            "finding_id": f"KQ-{as_of.isoformat()}-{index:03d}",
            "owner": "repository",
            "detected_at": f"{as_of.isoformat()}T00:00:00Z",
            "due_at": f"{(as_of + dt.timedelta(days=7)).isoformat()}T00:00:00Z",
            "affected_consumers": ["repository-governance"],
            "freeze_action": "freeze affected formal use until revalidation",
            "recovery_batch_id": f"KQ-RR-{as_of.isoformat()}",
            "closure_evidence": [],
            "status": "open",
            "error": error,
        })
    return {"contract": data["contract"], "as_of": as_of.isoformat(), "status": "pass" if not findings else "fail", "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--as-of", default=dt.date.today().isoformat()); parser.add_argument("--output", required=True); args = parser.parse_args()
    report = build(dt.date.fromisoformat(args.as_of))
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__": raise SystemExit(main())
