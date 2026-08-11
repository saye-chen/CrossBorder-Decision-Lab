#!/usr/bin/env python3
"""Build or verify owner-authorized D01-D13 controlled-pilot acceptance evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ecae_common import content_hash


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
MIGRATION = ROOT / "integrations" / "consumer-migration.json"
OUTPUT = ROOT / "evaluations" / "consumer-controlled-pilot-acceptance"
PRODUCTION_PLAN = ROOT / "integrations" / "consumer-production-acceptance-plan.json"
CONDITIONS = [
    "controlled_pilot_non_production_only",
    "business_owner_decision_required",
    "production_and_high_stakes_use_requires_L4_evidence",
    "external_write_forbidden",
]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def build() -> tuple[dict, dict[Path, dict]]:
    migration = load(MIGRATION)
    migration["status"] = "controlled_pilot_accepted_production_l4_pending"
    records: dict[Path, dict] = {}
    for contract in migration["consumers"]:
        domain_id = contract["domain_id"]
        accepted_uses = [
            item["use"] for item in contract["use_requirements"]
            if item["requires_independent_review"] is False
        ]
        record_ref = f"experiment-causal-assessment/evaluations/consumer-controlled-pilot-acceptance/{domain_id}.json"
        contract["acceptance"] = {
            "scope": "controlled_pilot_non_production",
            "status": "conditionally_accepted",
            "consumer_owner_role": f"{domain_id}_consumer_owner",
            "signed_record_ref": record_ref,
            "accepted_uses": accepted_uses,
            "conditions": CONDITIONS,
            "production_status": "not_executed",
            "production_signed_record_ref": None,
        }

    migration["local_verification"]["controlled_pilot_owner_acceptance"] = "verified_by_owner_authorization"
    migration["completion_gate"] = {
        "local_contract_implementation_complete": True,
        "all_controlled_pilot_consumer_acceptances_signed": True,
        "wp11_controlled_pilot_complete": True,
        "all_production_dual_runs_completed": False,
        "all_production_differences_dispositioned": False,
        "all_production_consumer_acceptances_signed": False,
        "all_production_rollback_drills_passed": False,
        "l4_production_acceptance_complete": False,
    }

    for contract in migration["consumers"]:
        domain_id = contract["domain_id"]
        record = {
            "schema_version": "1.0.0",
            "record_id": f"ECAE-CONSUMER-ACCEPTANCE-{domain_id}-CONTROLLED-PILOT-20260810",
            "migration_id": migration["migration_id"],
            "domain_id": domain_id,
            "contract_version": contract["contract_version"],
            "contract_content_hash": content_hash(contract),
            "acceptance_scope": "controlled_pilot_non_production",
            "decision": "conditionally_accepted",
            "reviewed_at": "2026-08-10T00:00:00+08:00",
            "expires_at": "2027-08-10T00:00:00+08:00",
            "reviewer": {
                "identity": "Miles Chen",
                "role": contract["acceptance"]["consumer_owner_role"],
                "affiliation": "consumer_domain",
                "independent_of_producer_implementation": True,
            },
            "authorization_basis": "Explicit repository-owner instruction in the Codex task on 2026-08-10.",
            "evidence_refs": [
                contract["dual_run"]["local_fixture_ref"],
                "experiment-causal-assessment/evaluations/consumer-migration-local-verification.json",
                f"experiment-causal-assessment/evaluations/consumer-production-preflight/{domain_id}-evaluation.json",
            ],
            "accepted_uses": contract["acceptance"]["accepted_uses"],
            "conditions": CONDITIONS,
            "consumer_owner_attestation": True,
            "producer_self_acceptance": False,
            "production_evidence_claimed": False,
            "external_write": False,
            "content_hash": "0" * 64,
        }
        record["content_hash"] = content_hash(record)
        records[REPO / contract["acceptance"]["signed_record_ref"]] = record
    return migration, records


def domain_summaries(migration: dict) -> dict[Path, dict]:
    outputs: dict[Path, dict] = {}
    for contract in migration["consumers"]:
        path = REPO / contract["dual_run"]["local_fixture_ref"]
        summary = load(path)
        summary["controlled_pilot_owner_accepted"] = True
        summary["controlled_pilot_acceptance_scope"] = "non_production"
        summary["independent_owner_accepted"] = False
        summary["owner_acceptance_status"] = "conditionally_accepted_controlled_pilot"
        summary["signed_owner_acceptance_ref"] = contract["acceptance"]["signed_record_ref"]
        summary["production_dual_run_completed"] = False
        summary["production_difference_dispositioned"] = False
        summary["production_ready"] = False
        outputs[path] = summary
    return outputs


def production_plan(migration: dict) -> dict:
    plan = load(PRODUCTION_PLAN)
    plan["status"] = "l4_fixture_preflight_passed_waiting_production_snapshot"
    contracts = {item["domain_id"]: item for item in migration["consumers"]}
    for row in plan["domains"]:
        row["contract_content_hash"] = content_hash(contracts[row["domain_id"]])
    plan["completion_gate"] = {
        "owners_assigned": True,
        "fixture_preflights_passed": True,
        "production_snapshots_bound": False,
        "production_dual_runs_completed": False,
        "differences_dispositioned": False,
        "rollback_drills_passed": False,
        "owner_acceptances_signed": False,
        "l4_production_acceptance_complete": False,
    }
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    migration, records = build()
    outputs = {MIGRATION: migration, PRODUCTION_PLAN: production_plan(migration), **records, **domain_summaries(migration)}
    mismatches = [path.relative_to(REPO).as_posix() for path, value in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != dump(value)]
    if args.write:
        for path, value in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(dump(value), encoding="utf-8")
        print(json.dumps({"written": len(outputs), "controlled_pilot_acceptances": 13, "production_claim": False}, sort_keys=True))
        return 0
    print(json.dumps({"valid": not mismatches, "mismatches": mismatches, "controlled_pilot_acceptances": 13, "production_claim": False}, sort_keys=True))
    return 0 if not mismatches else 2


if __name__ == "__main__":
    raise SystemExit(main())
