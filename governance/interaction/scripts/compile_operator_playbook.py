#!/usr/bin/env python3
"""Compile a validated Decision Packet into a non-authoritative operator view."""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import argparse

ROOT = pathlib.Path(__file__).resolve().parents[3]


def canonical_hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def compile_playbook(packet: dict, *, trusted_packet_hash: str | None = None) -> dict:
    if not trusted_packet_hash or canonical_hash(packet) != trusted_packet_hash:
        raise ValueError("source packet does not match independently trusted hash")
    domains = {d["domain_id"] for d in json.loads((ROOT / "governance/domain-architecture-registry.json").read_text())["domains"] if d["availability"] == "current"}
    if packet.get("owner_domain") not in domains:
        raise ValueError("unknown owner domain")
    validation = packet.get("erdg_validation", {})
    if validation.get("status") != "passed" or validation.get("contract") != "ERDG-CONTRACT-2026.07":
        raise ValueError("only ERDG-passed packets compile")
    if packet.get("external_write") is True:
        raise ValueError("Decision Packet cannot self-authorize external writes")
    if packet["decision"]["status"] not in {"proposed", "validated", "approved", "blocked", "inconclusive"}:
        raise ValueError("unsupported decision status")
    if packet.get("actions") and packet["decision"]["status"] in {"blocked", "inconclusive"}:
        raise ValueError("blocked/inconclusive source cannot carry operating actions")
    if packet.get("actions") and packet["owner_domain"] == "D14":
        raise ValueError("D14 coordination summary cannot own business actions")
    actions = []
    ids = set()
    for action in packet.get("actions", []):
        required = ("action_id", "instruction", "owner_role", "success_conditions", "guardrails", "stop_conditions")
        if any(not action.get(key) for key in required):
            raise ValueError(f"action {action.get('action_id', '<unknown>')} lacks execution controls")
        if action["action_id"] in ids:
            raise ValueError("duplicate action id")
        ids.add(action["action_id"])
        if action.get("external_write") is True:
            raise ValueError("source action cannot self-authorize external write")
        if not isinstance(action.get("approval_required", True), bool):
            raise ValueError("approval_required must be boolean")
        actions.append({
            "action_id": action["action_id"], "instruction": action["instruction"], "status": "proposed",
            "owner_role": action["owner_role"], "dependencies": action.get("dependencies", []),
            "success_conditions": action["success_conditions"], "guardrails": action["guardrails"],
            "stop_conditions": action["stop_conditions"], "approval_required": bool(action.get("approval_required", True)),
            "external_write": False,
        })
    decision = packet["decision"]
    return {
        "contract": "CBDS-OPERATOR-PLAYBOOK-2026.07", "playbook_id": f"PB-{packet['packet_id']}",
        "source_packet": {"packet_id": packet["packet_id"], "packet_hash": canonical_hash(packet), "erdg_contract": validation["contract"], "validation_status": "passed"},
        "owner_domain": packet["owner_domain"],
        "decision": {"decision_id": decision["decision_id"], "status": decision["status"], "posture": decision["posture"], "action_ceiling": decision["action_ceiling"]},
        "object": packet["object"], "as_of_time": packet["as_of_time"], "actions": actions,
        "rollback": packet["rollback"], "outcome_feedback": packet["outcome_feedback"], "external_write": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=pathlib.Path)
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("--trusted-packet-hash", required=True)
    args = parser.parse_args()
    try:
        packet = json.loads(args.packet.read_text())
        result = compile_playbook(packet, trusted_packet_hash=args.trusted_packet_hash)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 1
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"compiled {result['playbook_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
