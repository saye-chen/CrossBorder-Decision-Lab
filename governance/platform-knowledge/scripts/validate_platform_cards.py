#!/usr/bin/env python3
"""Validate platform cards, expiry and inference action ceilings."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "governance/platform-knowledge/platform-knowledge-card.schema.json"


def validate(card: dict, as_of: dt.date) -> list[str]:
    schema = json.loads(SCHEMA.read_text())
    errors = [f"schema: {error.message}" for error in Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER).iter_errors(card)]
    if card.get("contract") != "CBDS-PLATFORM-KNOWLEDGE-2026.08": errors.append("unsupported platform knowledge contract")
    if card.get("owner_domain") not in {"D07", "D08", "D09"}: errors.append("owner must be LIFD, PLCO, or AAMO")
    try:
        reviewed = dt.date.fromisoformat(card["reviewed_at"]); expires = dt.date.fromisoformat(card["expires_at"]); valid_from = dt.date.fromisoformat(card["valid_from"])
        if not valid_from <= reviewed <= expires: errors.append("invalid validity window")
        if as_of > expires: errors.append("card is expired")
    except (KeyError, ValueError): errors.append("valid_from, reviewed_at, expires_at must be ISO dates")
    if not card.get("sources"): errors.append("card requires sources")
    if card.get("evidence_status") == "inferred":
        forbidden = set(card.get("prohibited_uses", []))
        required = {"direct_score_change", "automatic_external_write", "causal_claim"}
        if not required <= forbidden: errors.append("inferred card must forbid score changes, external writes, and causal claims")
    for hypothesis in card.get("testable_hypotheses", []):
        for key in ("metric", "window", "success", "guardrail", "stop"):
            if not hypothesis.get(key): errors.append(f"hypothesis {hypothesis.get('hypothesis_id')} lacks {key}")
    if not card.get("invalidation_conditions"): errors.append("card requires invalidation conditions")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("paths", nargs="+"); parser.add_argument("--as-of", default=dt.date.today().isoformat()); args = parser.parse_args()
    as_of = dt.date.fromisoformat(args.as_of); failures = {}
    for raw in args.paths:
        path = pathlib.Path(raw); errors = validate(json.loads(path.read_text()), as_of)
        if errors: failures[str(path)] = errors
    print(json.dumps({"valid": not failures, "failures": failures}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__": raise SystemExit(main())
