#!/usr/bin/env python3
"""Compile a validated Decision Packet into a non-authoritative operator view."""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys


def canonical_hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def compile_playbook(packet: dict) -> dict:
    validation = packet.get("erdg_validation", {})
    if validation.get("status") != "passed" or validation.get("contract") != "ERDG-CONTRACT-2026.07":
        raise ValueError("only ERDG-passed packets compile")
    if packet.get("external_write") is True:
        raise ValueError("Decision Packet cannot self-authorize external writes")
    actions = []
    for action in packet.get("actions", []):
        required = ("action_id", "instruction", "owner_role", "success_conditions", "guardrails", "stop_conditions")
        if any(not action.get(key) for key in required):
            raise ValueError(f"action {action.get('action_id', '<unknown>')} lacks execution controls")
        actions.append({
            "action_id": action["action_id"], "instruction": action["instruction"], "status": "proposed",
            "owner_role": action["owner_role"], "dependencies": action.get("dependencies", []),
            "success_conditions": action["success_conditions"], "guardrails": action["guardrails"],
            "stop_conditions": action["stop_conditions"], "approval_required": bool(action.get("approval_required", True)),
            "external_write": False,
        })
    decision = packet["decision"]
    return {
        "contract": "CBDS-OPERATOR-PLAYBOOK-2026.08", "playbook_id": f"PB-{packet['packet_id']}",
        "source_packet": {"packet_id": packet["packet_id"], "packet_hash": canonical_hash(packet), "erdg_contract": validation["contract"], "validation_status": "passed"},
        "owner_domain": packet["owner_domain"],
        "decision": {"decision_id": decision["decision_id"], "status": decision["status"], "posture": decision["posture"], "action_ceiling": decision["action_ceiling"]},
        "object": packet["object"], "as_of_time": packet["as_of_time"], "actions": actions,
        "rollback": packet["rollback"], "outcome_feedback": packet["outcome_feedback"], "external_write": False,
    }


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: compile_operator_playbook.py PACKET.json OUTPUT.json")
        return 2
    packet = json.loads(pathlib.Path(sys.argv[1]).read_text())
    result = compile_playbook(packet)
    pathlib.Path(sys.argv[2]).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"compiled {result['playbook_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
