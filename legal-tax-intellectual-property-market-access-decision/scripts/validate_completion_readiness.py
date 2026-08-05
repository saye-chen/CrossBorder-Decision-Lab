#!/usr/bin/env python3
"""Compute D05 engineering readiness; report external assurance separately."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
POLICY_PATH = ROOT / "evaluations/completion-readiness.json"
MANDATORY_VALIDATORS = (
    "legal-tax-intellectual-property-market-access-decision/scripts/validate_release_candidate.py",
    "legal-tax-intellectual-property-market-access-decision/scripts/validate_consumer_acceptance.py",
    "legal-tax-intellectual-property-market-access-decision/scripts/test_input_evidence.py",
    "legal-tax-intellectual-property-market-access-decision/scripts/test_decision_engine.py",
    "legal-tax-intellectual-property-market-access-decision/scripts/test_professional_domains.py",
    "legal-tax-intellectual-property-market-access-decision/scripts/test_professional_signoff.py",
    "legal-tax-intellectual-property-market-access-decision/scripts/test_integration_migration.py",
    "scripts/validate_professional_evaluation_registry.py",
)
ALLOWED_POLICY_KEYS = {
    "contract", "determination", "engineering_scope", "required_validators",
    "external_assurance_sources", "claim_boundaries",
}


def default_runner(relative_path: str) -> tuple[bool, str]:
    path = REPO / relative_path
    if not path.is_file():
        return False, "validator missing"
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    detail = (result.stdout + result.stderr).strip()[-1000:]
    return result.returncode == 0, detail


def policy_errors(policy: dict) -> list[str]:
    errors: list[str] = []
    if set(policy) != ALLOWED_POLICY_KEYS:
        errors.append("completion policy keys drifted or contain self-reported status")
    if policy.get("determination") != "computed_from_repository_evidence":
        errors.append("readiness determination must be computed")
    if tuple(policy.get("required_validators", [])) != MANDATORY_VALIDATORS:
        errors.append("mandatory validator set or order changed")
    boundaries = policy.get("claim_boundaries", {})
    expected_false = (
        "production_ready", "qualified_legal_tax_certainty",
        "l4_may_be_inferred_from_synthetic_evidence", "external_write",
    )
    if boundaries.get("engineering_ready_label") != "controlled_pilot_engineering_ready":
        errors.append("engineering readiness label drifted")
    if any(boundaries.get(key) is not False for key in expected_false):
        errors.append("controlled-pilot claim boundary was widened")
    expected_sources = {
        "consumer_owner_acceptance": "legal-tax-intellectual-property-market-access-decision/evaluations/consumer-contract-acceptance.json",
        "qualified_professional_signoff": "legal-tax-intellectual-property-market-access-decision/evaluations/qualified-professional-signoff-template.json",
        "authorized_real_replays": "legal-tax-intellectual-property-market-access-decision/evaluations/historical-replay-template.json",
    }
    if policy.get("external_assurance_sources") != expected_sources:
        errors.append("external assurance sources drifted")
    return errors


def external_assurance(policy: dict) -> dict:
    sources = policy["external_assurance_sources"]
    consumer = json.loads((REPO / sources["consumer_owner_acceptance"]).read_text(encoding="utf-8"))
    signoff = json.loads((REPO / sources["qualified_professional_signoff"]).read_text(encoding="utf-8"))
    replay = json.loads((REPO / sources["authorized_real_replays"]).read_text(encoding="utf-8"))
    owner_acceptance = bool(consumer.get("records")) and all(
        x.get("independent_owner_status") == "accepted" for x in consumer["records"]
    )
    qualified_signoff = (
        signoff.get("review_id") not in (None, "", "PENDING")
        and signoff.get("signature_ref") not in (None, "", "PENDING")
        and signoff.get("decision") in {"approved", "approved_with_conditions"}
    )
    required_replays = int(replay.get("minimum_authorized_cases", 3))
    replay_count = len(replay.get("cases", []))
    l4_passed = replay.get("production_ready") is True and replay_count >= required_replays
    return {
        "independent_consumer_owner_acceptance": owner_acceptance,
        "qualified_professional_signoff": qualified_signoff,
        "authorized_real_replay_count": replay_count,
        "minimum_authorized_real_replays": required_replays,
        "l4_passed": l4_passed,
        "external_assurance_complete": owner_acceptance and qualified_signoff and l4_passed,
    }


def compute(
    policy: dict | None = None,
    runner: Callable[[str], tuple[bool, str]] = default_runner,
) -> dict:
    policy = policy or json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    errors = policy_errors(policy)
    checks: dict[str, dict[str, str | bool]] = {}
    if not errors:
        for path in MANDATORY_VALIDATORS:
            passed, detail = runner(path)
            checks[path] = {"passed": passed, "detail": detail}
            if not passed:
                errors.append(f"validator failed: {path}")
    assurance = external_assurance(policy) if "external assurance sources drifted" not in errors else {}
    return {
        "contract": policy.get("contract"),
        "engineering_ready": not errors,
        "engineering_label": "controlled_pilot_engineering_ready" if not errors else "engineering_not_ready",
        "engineering_errors": errors,
        "validator_checks": checks,
        "external_assurance": assurance,
        "production_ready": False,
        "l4_is_an_engineering_gate": False,
    }


if __name__ == "__main__":
    result = compute()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["engineering_ready"] else 2)
