#!/usr/bin/env python3
"""Validate F01 L3 controlled-pilot method qualification without crossing L4."""

from __future__ import annotations

import json
from pathlib import Path

from run_native_method_parity import run as run_native_parity


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evaluations" / "method-evidence-registry.json"
SOURCES = ROOT / "evaluations" / "method-source-registry.json"
REVIEW = ROOT / "evaluations" / "controlled-pilot-method-review.json"
PARITY = ROOT / "evaluations" / "native-method-parity.json"
BACKENDS = ROOT / "backends" / "backend-registry.json"
EVIDENCE_CLASSES = {"analytical_or_design_truth", "simulation", "external_parity", "adversarial_negative", "mutation"}
FINAL_EVIDENCE = {"pass", "not_applicable_with_reason"}
ACTIVE_NATIVE = {
    "sample_size_fixed", "mde_precision_fixed", "randomized_itt", "cuped_linear",
    "srm_chi_square", "multiplicity_holm_bonferroni_bh", "guardrail_rules",
    "did_2x2_independent_cells",
}
PROTOCOL_ONLY = {"long_term_surrogate_contract", "transportability_contract"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def equivalent(left, right, tolerance=1e-10):
    if isinstance(left, float) or isinstance(right, float):
        return isinstance(left, (int, float)) and isinstance(right, (int, float)) and abs(left-right) <= tolerance * max(1.0, abs(left), abs(right))
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(equivalent(left[key], right[key], tolerance) for key in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(equivalent(a, b, tolerance) for a, b in zip(left, right))
    return left == right


def validate() -> dict:
    failures: list[str] = []
    evidence = load(EVIDENCE)
    sources = load(SOURCES)
    review = load(REVIEW)
    stored_parity = load(PARITY)
    current_parity = run_native_parity()
    backend_registry = load(BACKENDS)

    methods = evidence.get("methods", [])
    method_ids = [item.get("method_id") for item in methods]
    method_set = set(method_ids)
    if len(method_ids) != len(method_set) or len(method_ids) != 23:
        failures.append("method_inventory_not_23_unique")

    source_rows = sources.get("sources", [])
    source_ids = [item.get("source_id") for item in source_rows]
    if len(source_ids) != len(set(source_ids)):
        failures.append("duplicate_source_id")
    known_sources = set(source_ids)
    sources_by_id = {item.get("source_id"): item for item in source_rows}
    source_method_coverage: set[str] = set()
    for source in source_rows:
        if source.get("source_type") not in sources.get("source_policy", {}).get("allowed", []):
            failures.append(f"unapproved_source_type:{source.get('source_id')}")
        if not str(source.get("url", "")).startswith("https://"):
            failures.append(f"non_https_source:{source.get('source_id')}")
        unknown = set(source.get("method_ids", [])) - method_set
        if unknown:
            failures.append(f"source_unknown_methods:{source.get('source_id')}:{sorted(unknown)}")
        source_method_coverage.update(source.get("method_ids", []))
    if source_method_coverage != method_set:
        failures.append(f"source_coverage_mismatch:{sorted(method_set - source_method_coverage)}")

    active_native: set[str] = set()
    protocol_only: set[str] = set()
    for method in methods:
        method_id = method["method_id"]
        if set(method.get("evidence", {})) != EVIDENCE_CLASSES:
            failures.append(f"evidence_surface_mismatch:{method_id}")
        if any(status not in FINAL_EVIDENCE for status in method.get("evidence", {}).values()):
            failures.append(f"pending_evidence:{method_id}")
        if not set(method.get("source_ids", [])) or not set(method.get("source_ids", [])) <= known_sources:
            failures.append(f"source_binding_invalid:{method_id}")
        for source_id in method.get("source_ids", []):
            if method_id not in sources_by_id.get(source_id, {}).get("method_ids", []):
                failures.append(f"source_binding_not_bidirectional:{method_id}:{source_id}")
        if not (ROOT / method.get("script", "")).is_file():
            failures.append(f"script_missing:{method_id}")
        if not method.get("limitations"):
            failures.append(f"limitations_missing:{method_id}")
        disposition = method.get("release_disposition")
        if disposition == "controlled_pilot_active":
            active_native.add(method_id)
            if method.get("capability_tier") != "native_executable":
                failures.append(f"non_native_active:{method_id}")
            if method.get("independent_review") != "owner_authorized_primary_source_review_pass":
                failures.append(f"active_review_missing:{method_id}")
        elif disposition == "protocol_only_active":
            protocol_only.add(method_id)
            if method.get("capability_tier") != "protocol_only" or "awarded" not in method.get("claim_ceiling", ""):
                failures.append(f"unsafe_protocol_only:{method_id}")
        elif disposition in {
            "installed_withheld_l4_qualification", "candidate_rejected_fail_closed",
            "candidate_unavailable_fail_closed",
        }:
            if method.get("claim_ceiling") not in {"unavailable", "unavailable_until_l4_qualification"}:
                failures.append(f"withheld_claim_ceiling:{method_id}")
        else:
            failures.append(f"unknown_release_disposition:{method_id}")
    if active_native != ACTIVE_NATIVE:
        failures.append(f"active_native_mismatch:{sorted(active_native ^ ACTIVE_NATIVE)}")
    if protocol_only != PROTOCOL_ONLY:
        failures.append(f"protocol_only_mismatch:{sorted(protocol_only ^ PROTOCOL_ONLY)}")

    installed_unverified = {
        item["backend_id"] for item in backend_registry.get("backends", [])
        if item.get("status") == "installed_unverified"
    }
    if len(installed_unverified) != 11 or any(item.get("status") == "verified" for item in backend_registry.get("backends", [])):
        failures.append("advanced_backend_fail_closed_boundary_drift")

    if current_parity != stored_parity or not stored_parity.get("all_pass"):
        failures.append("native_parity_not_reproducible")
    if review.get("status") != "accepted" or review.get("l3_controlled_pilot_gate_closed") is not True:
        failures.append("controlled_pilot_review_open")
    if review.get("authorization", {}).get("external_independence_claimed") is not False:
        failures.append("false_external_independence_claim")
    if review.get("l4_external_review_gate_closed") is not False or review.get("production_ready") is not False:
        failures.append("l4_boundary_crossed")
    if evidence.get("registry_status") != "L3_controlled_pilot_complete" or evidence.get("l4_external_qualification_complete") is not False:
        failures.append("method_registry_release_state_invalid")
    for relative in evidence.get("shared_evidence_refs", []):
        if not (ROOT / relative).exists():
            failures.append(f"shared_evidence_missing:{relative}")

    return {
        "valid": not failures,
        "failures": sorted(set(failures)),
        "method_count": len(method_ids),
        "primary_source_count": len(source_ids),
        "active_native_method_count": len(active_native),
        "protocol_only_method_count": len(protocol_only),
        "advanced_backend_count_withheld": len(installed_unverified),
        "native_parity_pass": stored_parity.get("all_pass") is True and current_parity.get("all_pass") is True and equivalent(current_parity.get("checks"), stored_parity.get("checks")),
        "l3_controlled_pilot_gate_closed": review.get("l3_controlled_pilot_gate_closed") is True,
        "l4_external_review_gate_closed": False,
        "production_ready": False,
        "external_write": False,
    }


if __name__ == "__main__":
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if result["valid"] else 2)
