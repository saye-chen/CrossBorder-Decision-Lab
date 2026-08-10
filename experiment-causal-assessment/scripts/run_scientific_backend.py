#!/usr/bin/env python3
"""Execute a verified scientific adapter through a bounded JSON-only subprocess."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from backend_contract import require_verified_backend
from ecae_common import ECAEError, canonical_json, cli_main, ensure_finite
from validate_schema import validate_object

ROOT = Path(__file__).resolve().parents[1]


def validate_backend_output(output: dict, backend: dict) -> dict:
    if not isinstance(output, dict):
        raise ECAEError("BACKEND_OUTPUT_INVALID", "Backend output must be a JSON object")
    ensure_finite(output)
    validate_object(output, "backend-execution-result.schema.json", verify_hash=False)
    expected = {
        "backend_id": backend["backend_id"],
        "candidate_id": backend["selected_candidate_id"],
        "package": backend["package"],
        "version": backend["version"],
    }
    mismatches = {field: {"expected": expected[field], "observed": output.get(field)} for field in expected if output.get(field) != expected[field]}
    if mismatches:
        raise ECAEError("BACKEND_OUTPUT_BINDING_MISMATCH", "Backend output does not bind the verified runtime", mismatches)
    if output["ok"] is not True:
        error = output.get("error") or {}
        raise ECAEError("BACKEND_EXECUTION_REPORTED_FAILURE", error.get("message", "Backend reported failure"), {"backend_error": error})
    return output


def _runtime_command(backend: dict, adapter: Path) -> list[str]:
    kind = backend["runtime"]["kind"]
    if kind == "python":
        executable = os.environ.get("ECAE_PYTHON_BACKEND") or sys.executable
        if adapter.suffix != ".py":
            raise ECAEError("BACKEND_ADAPTER_RUNTIME_MISMATCH", "Python backend requires a .py adapter")
    elif kind == "r":
        executable = os.environ.get("ECAE_RSCRIPT_BACKEND") or shutil.which("Rscript")
        if adapter.suffix.lower() != ".r":
            raise ECAEError("BACKEND_ADAPTER_RUNTIME_MISMATCH", "R backend requires a .R adapter")
    else:
        raise ECAEError("BACKEND_RUNTIME_UNAVAILABLE", "Unbound runtime cannot execute")
    if not executable or not Path(executable).is_file() or not os.access(executable, os.X_OK):
        raise ECAEError("BACKEND_RUNTIME_UNAVAILABLE", f"Executable runtime is unavailable for {kind}")
    return [str(executable), "--vanilla", str(adapter)] if kind == "r" else [str(executable), str(adapter)]


def execute_backend(value: dict) -> dict:
    backend_id = value.get("backend_id")
    payload = value.get("payload")
    timeout = value.get("timeout_seconds", 120)
    if not isinstance(backend_id, str) or not backend_id or not isinstance(payload, dict):
        raise ECAEError("BACKEND_REQUEST_INVALID", "backend_id and object payload are required")
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 300:
        raise ECAEError("BACKEND_TIMEOUT_INVALID", "timeout_seconds must be an integer from 1 through 300")
    ensure_finite(payload)
    backend = require_verified_backend(backend_id)
    adapter = (ROOT / backend["adapter_ref"]).resolve()
    if ROOT.resolve() not in adapter.parents:
        raise ECAEError("BACKEND_PATH_UNSAFE", "Adapter must remain inside the F01 package")
    command = _runtime_command(backend, adapter)
    try:
        completed = subprocess.run(
            command,
            input=canonical_json(payload),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ECAEError("BACKEND_EXECUTION_TIMEOUT", "Scientific backend exceeded its registered timeout", {"timeout_seconds": timeout}) from exc
    if completed.returncode != 0:
        raise ECAEError("BACKEND_EXECUTION_FAILED", "Scientific backend process failed", {"exit_status": completed.returncode, "stderr_tail": completed.stderr[-500:]})
    try:
        output = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ECAEError("BACKEND_OUTPUT_INVALID", "Scientific backend emitted invalid or mixed JSON", {"line": exc.lineno}) from exc
    validated = validate_backend_output(output, backend)
    return {
        "backend": {key: backend[key] for key in ("backend_id", "selected_candidate_id", "package", "version", "parity_evidence_ref", "verified_at", "expires_at")},
        "result": validated["result"],
        "warnings": validated["warnings"],
    }


if __name__ == "__main__":
    cli_main(execute_backend, __doc__ or "Run scientific backend")
