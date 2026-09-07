#!/usr/bin/env python3
"""Validate operator playbook safety invariants."""

from __future__ import annotations

import json
import pathlib
import sys
import argparse
import importlib.util
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCHEMA = ROOT / "governance/interaction/schemas/operator-playbook.schema.json"


def validate(payload: dict, source_packet: dict | None = None, *, trusted_packet_hash: str | None = None) -> list[str]:
    schema = json.loads(SCHEMA.read_text())
    errors = [f"schema: {error.message}" for error in Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER).iter_errors(payload)]
    if errors:
        return errors
    if source_packet is None or not trusted_packet_hash:
        return ["independently trusted source packet and hash are required"]
    spec = importlib.util.spec_from_file_location("playbook_source_compiler", pathlib.Path(__file__).with_name("compile_operator_playbook.py"))
    compiler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compiler)
    try:
        expected = compiler.compile_playbook(source_packet, trusted_packet_hash=trusted_packet_hash)
        if payload != expected:
            errors.append("playbook differs from trusted source projection")
    except (ValueError, KeyError, TypeError) as exc:
        errors.append(f"source rejected: {exc}")
    if payload.get("contract") != "CBDS-OPERATOR-PLAYBOOK-2026.07": errors.append("unsupported playbook contract")
    source = payload.get("source_packet", {})
    if source.get("validation_status") != "passed" or source.get("erdg_contract") != "ERDG-CONTRACT-2026.07": errors.append("playbook must bind to ERDG-passed packet")
    if payload.get("external_write") is not False: errors.append("playbook cannot authorize external write")
    for action in payload.get("actions", []):
        if action.get("status") != "proposed": errors.append("compiled actions must remain proposed")
        if action.get("external_write") is not False: errors.append("compiled action cannot authorize external write")
        for key in ("success_conditions", "guardrails", "stop_conditions"):
            if not action.get(key): errors.append(f"action {action.get('action_id')} lacks {key}")
    rollback = payload.get("rollback", {})
    if not rollback.get("trigger") or not rollback.get("steps") or not rollback.get("residual_exposure_owner"): errors.append("rollback is incomplete")
    feedback = payload.get("outcome_feedback", {})
    if not feedback.get("observation_window") or not feedback.get("writeback_target"): errors.append("outcome feedback is incomplete")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=pathlib.Path)
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--trusted-packet-hash", required=True)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.input.read_text()), json.loads(args.source.read_text()), trusted_packet_hash=args.trusted_packet_hash)
    except (OSError, ValueError, TypeError) as exc:
        errors = [str(exc)]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
