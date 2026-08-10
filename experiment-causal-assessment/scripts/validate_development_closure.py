#!/usr/bin/env python3
"""Separate completed F01 software work from evidence that only external actors can close."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
EXECUTABLE_BACKENDS = {
    "cluster_inference",
    "group_sequential",
    "switchback_inference",
    "staggered_did",
    "synthetic_control",
    "synthetic_did",
    "rdd_local",
    "weak_iv",
    "observational_aipw",
    "observational_dml",
    "hte_uplift",
}
EVIDENCE_CLASSES = {"analytical_or_design_truth", "simulation", "external_parity", "adversarial_negative", "mutation"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def audit() -> dict:
    failures: list[str] = []
    manifest = load(REPO / "governance/f01-implementation-manifest.json")
    qualification = load(ROOT / "evaluations/persistent-backend-development-qualification.json")
    registry = load(ROOT / "backends/backend-registry.json")
    migration = load(ROOT / "integrations/consumer-migration.json")
    methods = load(ROOT / "evaluations/method-evidence-registry.json")
    controlled_review = load(ROOT / "evaluations/controlled-pilot-method-review.json")
    review = load(ROOT / "evaluations/independent-review-template.json")
    replay = load(ROOT / "evaluations/real-replay-template.json")

    packages = {item["id"]: item for item in manifest["work_packages"]}
    if set(packages) != {f"WP-{index:02d}" for index in range(14)}:
        failures.append("work_package_inventory_incomplete")
    for package in packages.values():
        for relative in package.get("evidence", []):
            if not (REPO / relative).exists():
                failures.append(f"missing_evidence:{package['id']}:{relative}")

    if not qualification.get("all_adapters_pass") or len(qualification.get("adapter_results", {})) != 12:
        failures.append("persistent_backend_qualification_incomplete")
    if not all(value == "pass" for value in qualification.get("runtime_checks", {}).values()):
        failures.append("runtime_or_adapter_integrity_incomplete")
    backend_states = {item["backend_id"]: item["status"] for item in registry["backends"]}
    if {key for key, value in backend_states.items() if value == "installed_unverified"} != EXECUTABLE_BACKENDS:
        failures.append("installed_unverified_backend_set_mismatch")
    if any(value == "verified" for value in backend_states.values()):
        failures.append("unearned_backend_verification")
    if backend_states.get("anytime_valid") != "rejected" or backend_states.get("observational_tmle") != "unavailable":
        failures.append("rejected_candidate_boundary_drift")

    completion = migration["completion_gate"]
    if completion.get("local_contract_implementation_complete") is not True or completion.get("wp11_controlled_pilot_complete") is not True or len(migration.get("consumers", [])) != 13:
        failures.append("consumer_local_implementation_incomplete")
    for method in methods["methods"]:
        if set(method.get("evidence", {})) != EVIDENCE_CLASSES:
            failures.append(f"method_evidence_surface_incomplete:{method.get('method_id')}")
        if not (ROOT / method["script"]).is_file():
            failures.append(f"method_script_missing:{method.get('method_id')}")
        if any(value not in {"pass", "not_applicable_with_reason"} for value in method.get("evidence", {}).values()):
            failures.append(f"method_evidence_pending:{method.get('method_id')}")
    if methods.get("registry_status") != "L3_controlled_pilot_complete" or controlled_review.get("l3_controlled_pilot_gate_closed") is not True:
        failures.append("controlled_pilot_method_review_incomplete")

    boundaries = manifest["release_boundaries"]
    if boundaries.get("production_ready") or boundaries.get("external_write_authority"):
        failures.append("unsafe_release_boundary")
    if review.get("l4_external_review_gate_closed") is not False or replay.get("l4_gate_closed") is not False:
        failures.append("unearned_external_gate")

    external_or_qualification_only = [
        "L4 external qualification for advanced backends withheld from the controlled-pilot executable surface",
        "L4 independent non-implementer causal-method and production-evidence review",
        "L4 production dual-runs, difference dispositions, owner signatures, and production rollback evidence for D01-D13",
        "L4 authorized real-data decision replay, mature outcomes, calibration, drift review, and external assurance",
    ]
    return {
        "schema_version": "1.0.0",
        "audit_id": "ECAE-DEVELOPMENT-CLOSURE-2026-08-10",
        "development_complete": not failures,
        "development_failures": sorted(set(failures)),
        "checks": {
            "work_package_artifacts_exist": not any(item.startswith("missing_evidence:") for item in failures),
            "persistent_runtime_and_12_adapters_pass": "persistent_backend_qualification_incomplete" not in failures and "runtime_or_adapter_integrity_incomplete" not in failures,
            "backend_registry_fail_closed": "installed_unverified_backend_set_mismatch" not in failures and "unearned_backend_verification" not in failures,
            "consumer_local_implementation_13_of_13": "consumer_local_implementation_incomplete" not in failures,
            "method_evidence_and_script_surfaces_complete": not any(item.startswith("method_") for item in failures),
            "release_and_external_gates_fail_closed": "unsafe_release_boundary" not in failures and "unearned_external_gate" not in failures,
        },
        "remaining_work_class": "l4_external_only" if not failures else "development_remains",
        "remaining_work": external_or_qualification_only,
        "production_ready": False,
        "external_write_authorized": False,
    }


def main() -> int:
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["development_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
