#!/usr/bin/env python3
"""Validate backend registry, lock bindings, proof records, and fail-closed states."""

from __future__ import annotations

from pathlib import Path

from ecae_common import ECAEError, cli_main, load_json, parse_time
from validate_schema import validate_object

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_DISPOSITIONS = {
    "selected_pending_runtime_and_parity",
    "component_probe_incomplete",
    "component_only_pending_parity",
    "selected_as_parity_oracle_pending_runtime",
    "selected_component_pending_sequence_contract_and_parity",
    "selected_development_adapter_pending_deploy_runtime_and_external_verification",
    "development_parity_oracle_pending_qualification_and_external_verification",
    "selected_component_development_adapter_pending_external_verification",
    "rejected_for_binding",
}


def _safe_relative_file(relative: str, label: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ECAEError("BACKEND_PATH_UNSAFE", f"{label} must be a safe F01-relative path", {"path": relative})
    resolved = ROOT / path
    if not resolved.is_file():
        raise ECAEError("BACKEND_EVIDENCE_MISSING", f"{label} does not exist", {"path": relative})
    return resolved


def validate_backend_registry(value: dict) -> dict:
    validate_object(value, "backend-registry.schema.json", verify_hash=False)
    lock_path = _safe_relative_file(value["lock_ref"], "lock_ref")
    lock = load_json(lock_path)
    candidates = lock.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ECAEError("BACKEND_LOCK_EMPTY", "Backend lock requires candidates")
    candidate_ids = [item.get("candidate_id") for item in candidates]
    if len(candidate_ids) != len(set(candidate_ids)) or any(not item for item in candidate_ids):
        raise ECAEError("BACKEND_CANDIDATE_DUPLICATE", "Backend candidate ids must be unique and non-empty")
    by_id = {item["candidate_id"]: item for item in candidates}
    for candidate in candidates:
        if candidate.get("disposition") not in ALLOWED_DISPOSITIONS:
            raise ECAEError("BACKEND_DISPOSITION_INVALID", "Unknown candidate disposition", {"candidate_id": candidate["candidate_id"]})
        sources = candidate.get("official_sources")
        if not isinstance(sources, list) or not sources or any(not source.startswith("https://") for source in sources):
            raise ECAEError("BACKEND_SOURCE_INVALID", "Every candidate requires HTTPS official sources", {"candidate_id": candidate["candidate_id"]})
        if candidate.get("ecosystem") == "github":
            revision = candidate.get("source_revision")
            if not isinstance(revision, str) or len(revision) != 40 or any(char not in "0123456789abcdef" for char in revision):
                raise ECAEError("BACKEND_SOURCE_REVISION_INVALID", "GitHub candidates require a pinned lowercase 40-character source revision", {"candidate_id": candidate["candidate_id"]})

    backend_ids = [item.get("backend_id") for item in value["backends"]]
    if len(backend_ids) != len(set(backend_ids)):
        raise ECAEError("BACKEND_DUPLICATE", "Backend ids must be unique")
    verified_count = 0
    for backend in value["backends"]:
        selected = backend.get("selected_candidate_id")
        if selected is not None:
            candidate = by_id.get(selected)
            if candidate is None:
                raise ECAEError("BACKEND_CANDIDATE_NOT_LOCKED", "Selected candidate is absent from the lock", {"backend_id": backend["backend_id"]})
            for field in ("backend_id", "package", "version", "ecosystem"):
                if candidate.get(field) != backend.get(field):
                    raise ECAEError("BACKEND_LOCK_MISMATCH", "Registry binding differs from backend lock", {"backend_id": backend["backend_id"], "field": field})
        if backend["status"] != "verified":
            if any(backend.get(field) is not None for field in ("parity_evidence_ref", "verified_at", "expires_at")):
                raise ECAEError("BACKEND_FALSE_PROOF", "Unverified backend cannot carry verification timestamps or evidence", {"backend_id": backend["backend_id"]})
            continue
        verified_count += 1
        proof_path = _safe_relative_file(backend["parity_evidence_ref"], "parity_evidence_ref")
        proof = load_json(proof_path)
        validate_object(proof, "backend-proof.schema.json", verify_hash=False)
        for field, proof_field in (("backend_id", "backend_id"), ("selected_candidate_id", "candidate_id"), ("package", "package"), ("version", "version")):
            if backend[field] != proof[proof_field]:
                raise ECAEError("BACKEND_PROOF_BINDING_MISMATCH", "Proof does not bind the registered backend", {"backend_id": backend["backend_id"], "field": field})
        if backend["verified_at"] != proof["verified_at"] or backend["expires_at"] != proof["expires_at"]:
            raise ECAEError("BACKEND_PROOF_TIME_MISMATCH", "Registry and proof verification windows differ", {"backend_id": backend["backend_id"]})
        if parse_time(proof["expires_at"], "expires_at") <= parse_time(proof["verified_at"], "verified_at"):
            raise ECAEError("BACKEND_PROOF_TIME_ORDER", "Backend proof expiry must follow verification")
    return {"valid": True, "backend_count": len(backend_ids), "candidate_count": len(candidate_ids), "verified_count": verified_count, "policy": "fail_closed"}


if __name__ == "__main__":
    cli_main(validate_backend_registry, __doc__ or "Validate backend registry")
