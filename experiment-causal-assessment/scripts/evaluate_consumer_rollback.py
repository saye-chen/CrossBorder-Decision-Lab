#!/usr/bin/env python3
"""Build an idempotent, non-causal consumer rollback posture and recompute request."""

from __future__ import annotations

from ecae_common import ECAEError, cli_main, content_hash
from validate_consumer_migration import contract_for, load_default_migration, validate_consumer_migration


def evaluate_consumer_rollback(value: dict) -> dict:
    migration = value.get("migration") or load_default_migration()
    validate_consumer_migration(migration)
    domain_id = value.get("domain_id")
    reason = value.get("reason")
    if not isinstance(domain_id, str) or not isinstance(reason, str) or not reason.strip():
        raise ECAEError("ROLLBACK_INPUT_INCOMPLETE", "domain_id and non-empty reason are required")
    contract = contract_for(migration, domain_id)
    rollback = contract["rollback"]
    request = {
        "domain_id": domain_id,
        "contract_version": contract["contract_version"],
        "reason": reason.strip(),
        "mode": rollback["mode"],
    }
    return {
        "rollback_id": f"ECAE-ROLLBACK-{domain_id}-{content_hash(request)[:16]}",
        "domain_id": domain_id,
        "mode": rollback["mode"],
        "legacy_assets": contract["legacy_assets"]["paths"],
        "causal_wording_allowed": False,
        "incremental_value": {"state": "unknown", "reason": "rollback_invalidates_qualified_incremental_input"},
        "blocked_actions": rollback["blocked_actions"],
        "recompute_request": {
            "required": True,
            "reason": reason.strip(),
            "silent_continued_consumption_forbidden": True,
        },
        "business_owner_decision_required": True,
        "external_write": False,
    }


if __name__ == "__main__":
    cli_main(evaluate_consumer_rollback, __doc__ or "Evaluate consumer rollback")
