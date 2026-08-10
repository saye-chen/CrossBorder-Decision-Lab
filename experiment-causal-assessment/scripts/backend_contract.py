#!/usr/bin/env python3
"""Fail-closed scientific-backend registry, proof, and runtime access."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ecae_common import ECAEError, backend_registry_path, load_json, parse_time
from probe_backend_environment import probe_candidate
from validate_backend_registry import validate_backend_registry

ROOT = Path(__file__).resolve().parents[1]


def require_verified_backend(backend_id: str, *, registry: dict | None = None, now: datetime | None = None, runtime_probe=probe_candidate) -> dict:
    registry = load_json(backend_registry_path()) if registry is None else registry
    validate_backend_registry(registry)
    matches = [item for item in registry.get("backends", []) if item.get("backend_id") == backend_id]
    if len(matches) != 1:
        raise ECAEError("BACKEND_NOT_REGISTERED", f"Backend is not uniquely registered: {backend_id}")
    backend = matches[0]
    if backend.get("status") != "verified":
        raise ECAEError("BACKEND_UNAVAILABLE", f"Backend is not verified: {backend_id}", {"status":backend.get("status"),"reason":backend.get("reason")})
    required = ["selected_candidate_id","package","version","ecosystem","runtime","adapter_ref","parity_evidence_ref","verified_at","expires_at"]
    missing = [field for field in required if not backend.get(field)]
    if missing:
        raise ECAEError("BACKEND_PROOF_INCOMPLETE", f"Backend proof is incomplete: {backend_id}", missing)
    expiry = parse_time(backend["expires_at"], "expires_at")
    if expiry <= (now or datetime.now(timezone.utc)):
        raise ECAEError("BACKEND_PROOF_EXPIRED", f"Backend proof expired: {backend_id}", {"expires_at":backend["expires_at"]})
    probe = runtime_probe(backend)
    if probe.get("status") in {"runtime_unavailable", "package_unavailable", "probe_failed", "unbound"}:
        raise ECAEError("BACKEND_RUNTIME_UNAVAILABLE", f"Backend runtime is unavailable: {backend_id}", probe)
    if probe.get("status") != "available" or probe.get("observed_version") != backend["version"]:
        raise ECAEError("BACKEND_VERSION_MISMATCH", f"Backend version does not match lock: {backend_id}", probe)
    adapter = ROOT / backend["adapter_ref"]
    if not adapter.is_file():
        raise ECAEError("BACKEND_ADAPTER_MISSING", f"Backend adapter is missing: {backend_id}", {"adapter_ref": backend["adapter_ref"]})
    result = dict(backend)
    result["runtime_probe"] = probe
    return result
