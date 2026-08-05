#!/usr/bin/env python3
"""Top-level professional engineering gate for all thirteen current domains."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "governance/professional-evaluation-registry.json"
MUTATIONS = ROOT / "governance/release-mutation-contract.json"
EXPECTED_MUTATIONS = {
    "remove_noncompensable_redline", "raise_action_ceiling", "expired_evidence_to_current",
    "synthetic_evidence_to_production", "delete_counterevidence", "generic_template_substitution",
    "auxiliary_domain_final_decision", "delete_consumer_rejection", "old_version_overwrite",
    "partial_failure_overall_pass", "manual_completion_tamper", "same_source_fake_independence",
}
CORE = {
    "scripts/validate_professional_evaluation_registry.py",
    "scripts/validate_domain_professional_evaluations.py",
    "scripts/test_release_anti_cheat.py",
    "legal-tax-intellectual-property-market-access-decision/scripts/validate_completion_readiness.py",
}


def command_paths() -> list[str]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    paths = set(CORE)
    for row in registry["domains"]:
        paths.add(row["semantic_validator"])
        paths.add(row["numeric_validator"])
    return sorted(paths)


def validate(run_commands: bool = True) -> list[str]:
    errors: list[str] = []
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if len(registry.get("domains", [])) != 13:
        errors.append("professional registry is not thirteen-domain complete")
    mutation_contract = json.loads(MUTATIONS.read_text(encoding="utf-8"))
    mutation_ids = {x.get("id") for x in mutation_contract.get("mutations", [])}
    if mutation_ids != EXPECTED_MUTATIONS or len(mutation_contract.get("mutations", [])) != 12:
        errors.append("release mutation contract drifted")
    if mutation_contract.get("test") != "scripts/test_release_anti_cheat.py":
        errors.append("release mutation test binding drifted")
    for relative in command_paths():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing release evidence executable: {relative}")
    if errors or not run_commands:
        return errors
    for relative in command_paths():
        result = subprocess.run([sys.executable, str(ROOT / relative)], cwd=ROOT, capture_output=True, text=True)
        if result.returncode != 0:
            detail = (result.stdout + result.stderr).strip()[-1200:]
            errors.append(f"{relative} failed: {detail}")
    return errors


if __name__ == "__main__":
    errors = validate()
    print("PROFESSIONAL_ENGINEERING_RELEASE=PASS" if not errors else "PROFESSIONAL_ENGINEERING_RELEASE=FAIL\n- " + "\n- ".join(errors))
    print("L4_EXTERNAL_ASSURANCE=SEPARATE_NOT_PASSED")
    raise SystemExit(0 if not errors else 2)
