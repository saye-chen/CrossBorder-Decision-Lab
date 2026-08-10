#!/usr/bin/env python3
"""Audit F01 L1-L4 gates and keep production evidence separate from L1-L3."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
F01 = ROOT / "experiment-causal-assessment"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run(command: list[str]) -> tuple[bool, str]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False, env=environment)
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def audit(run_tests: bool = True) -> dict:
    required = [
        F01 / "SKILL.md",
        F01 / "agents/openai.yaml",
        F01 / "backends/backend-registry.json",
        F01 / "backends/runtime-lock.json",
        F01 / "integrations/consumer-migration.json",
        F01 / "evaluations/persistent-backend-development-qualification.json",
        F01 / "evaluations/development-closure.json",
        F01 / "evaluations/method-evidence-registry.json",
        F01 / "evaluations/method-source-registry.json",
        F01 / "evaluations/native-method-parity.json",
        F01 / "evaluations/controlled-pilot-method-review.json",
        F01 / "evaluations/independent-review-template.json",
        F01 / "evaluations/real-replay-template.json",
        F01 / "evaluations/consumer-controlled-pilot-acceptance",
    ]
    required.extend(F01 / "schemas" / name for name in [
        "causal-question.schema.json", "causal-graph.schema.json", "estimand.schema.json",
        "experiment-protocol.schema.json", "metric-contract.schema.json", "population-snapshot.schema.json",
        "assignment-record.schema.json", "exposure-record.schema.json", "analysis-plan.schema.json",
        "hypothesis-family.schema.json", "analysis-dataset-manifest.schema.json", "diagnostic-result.schema.json",
        "causal-analysis-result.schema.json", "sensitivity-result.schema.json", "economic-interpretation.schema.json",
        "deviation-record.schema.json", "causal-handoff.schema.json", "reproducibility-bundle.schema.json",
        "consumer-migration.schema.json", "consumer-acceptance.schema.json", "consumer-difference.schema.json",
    ])
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.exists()]
    skill_ok, skill_output = run([sys.executable, "scripts/validate_f01_structure.py"])
    governance_ok, governance_output = run([sys.executable, "scripts/validate_f01_governance.py"])
    repo_ok, repo_output = run([sys.executable, "scripts/validate_repo.py"])
    migration_ok, migration_output = run([
        sys.executable, "experiment-causal-assessment/scripts/validate_consumer_migration.py",
        "experiment-causal-assessment/integrations/consumer-migration.json",
    ])
    acceptance_build_ok, acceptance_build_output = run([
        sys.executable, "experiment-causal-assessment/scripts/build_controlled_pilot_acceptance.py",
    ])
    method_ok, method_output = run([
        sys.executable, "experiment-causal-assessment/scripts/validate_method_qualification.py",
    ])
    development_ok, development_output = run([
        sys.executable, "experiment-causal-assessment/scripts/validate_development_closure.py",
    ])
    tests_ok, tests_output = (True, "not_run") if not run_tests else run([
        sys.executable, "-m", "unittest", "discover", "-s", "experiment-causal-assessment/tests", "-p", "test_*.py",
    ])

    migration = load(F01 / "integrations/consumer-migration.json")
    controlled_review = load(F01 / "evaluations/controlled-pilot-method-review.json")
    external_review = load(F01 / "evaluations/independent-review-template.json")
    replay = load(F01 / "evaluations/real-replay-template.json")
    method_result = load(F01 / "evaluations/method-evidence-registry.json")
    backend_registry = load(F01 / "backends/backend-registry.json")

    l1 = not missing and skill_ok and governance_ok and repo_ok and development_ok
    l2 = l1 and tests_ok and migration_ok and acceptance_build_ok and migration["completion_gate"]["wp11_controlled_pilot_complete"] is True
    l3_review = controlled_review.get("l3_controlled_pilot_gate_closed") is True and controlled_review.get("status") == "accepted"
    l3 = l2 and method_ok and l3_review and method_result.get("registry_status") == "L3_controlled_pilot_complete"

    external_review_passed = external_review.get("l4_external_review_gate_closed") is True and external_review.get("status") == "accepted"
    production_consumers_passed = migration["completion_gate"]["l4_production_acceptance_complete"] is True
    real_replay_passed = replay.get("l4_gate_closed") is True and replay.get("status") == "externally_assured"
    advanced_backends_passed = all(item.get("status") in {"verified", "rejected", "unavailable"} for item in backend_registry["backends"])
    l4 = l3 and external_review_passed and production_consumers_passed and real_replay_passed and advanced_backends_passed

    manifest = load(ROOT / "governance/f01-implementation-manifest.json")
    boundaries = manifest["release_boundaries"]
    manifest_consistent = all((
        boundaries.get("l1_structure") is l1,
        boundaries.get("l2_contract") is l2,
        boundaries.get("l3_expert") is l3,
        boundaries.get("l4_external_assurance") is l4,
        boundaries.get("implementation_complete") is l3,
        boundaries.get("independent_review") is external_review_passed,
        boundaries.get("production_ready") is False,
        boundaries.get("external_write_authority") is False,
    ))
    registry = load(ROOT / "governance/foundation-capability-registry.json")
    f01 = next(item for item in registry["foundations"] if item["foundation_id"] == "F01")
    expected_release_state = f01["availability"] == "current" and f01["maturity"] == "controlled_pilot"
    premature = not expected_release_state or not manifest_consistent or not l3

    non_l4_blockers = {
        "missing_artifacts": missing,
        "development_pending": not development_ok,
        "controlled_pilot_consumer_acceptance_pending": not migration["completion_gate"]["wp11_controlled_pilot_complete"],
        "method_qualification_pending": not method_ok,
        "controlled_pilot_review_pending": not l3_review,
    }
    l4_blockers = {
        "production_consumer_dual_run_and_acceptance_pending": not production_consumers_passed,
        "advanced_backend_external_qualification_pending": not advanced_backends_passed,
        "independent_nonimplementer_review_pending": not external_review_passed,
        "authorized_real_replay_and_calibration_pending": not real_replay_passed,
    }
    checks = {
        "skill": {"pass": skill_ok, "output": skill_output},
        "governance": {"pass": governance_ok, "output": governance_output},
        "repository": {"pass": repo_ok, "output": repo_output},
        "development_closure": {"pass": development_ok, "output": development_output[-2000:]},
        "consumer_migration": {"pass": migration_ok, "output": migration_output[-2000:]},
        "controlled_pilot_acceptance_build": {"pass": acceptance_build_ok, "output": acceptance_build_output[-2000:]},
        "method_qualification": {"pass": method_ok, "output": method_output[-2000:]},
        "tests": {"pass": tests_ok, "output": tests_output[-2000:]},
    }
    return {
        "schema_version": "1.1.0",
        "f01_release_audit": {
            "l1_structure": l1,
            "l2_contract": l2,
            "l3_expert": l3,
            "l4_external_assurance": l4,
            "availability": f01["availability"],
            "maturity": f01["maturity"],
            "manifest_consistent": manifest_consistent,
            "premature_promotion": premature,
            "controlled_pilot_released": l3 and not premature,
            "remaining_gate_class": "L4_EXTERNAL_ONLY" if l3 and not l4 else ("NONE" if l4 else "L1_L3_REMAINS"),
        },
        "non_l4_blockers": non_l4_blockers,
        "l4_blockers": l4_blockers,
        "checks": checks,
        "policy": {"external_write": False, "production_ready": False, "public_method_sources_do_not_equal_real_replay": True},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-tests", action="store_true")
    parser.add_argument("--require-l3", action="store_true")
    parser.add_argument(
        "--write-audit",
        action="store_true",
        help="Write the exact audited result to the governed F01 release-audit artifact.",
    )
    args = parser.parse_args()
    result = audit(not args.no_tests)
    if args.write_audit:
        audit_path = F01 / "evaluations" / "release-audit.json"
        audit_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if result["f01_release_audit"]["premature_promotion"]:
        return 2
    if args.require_l3 and not result["f01_release_audit"]["l3_expert"]:
        return 2
    if any(result["non_l4_blockers"].values()):
        return 2
    return 0 if all(item["pass"] for item in result["checks"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
