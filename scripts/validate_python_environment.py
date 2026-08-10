#!/usr/bin/env python3
"""Prove authoritative subprocesses inherit the current Python dependency set."""
from __future__ import annotations

import json
import subprocess
import sys


def validate() -> list[str]:
    errors: list[str] = []
    try:
        import jsonschema
    except ImportError as exc:
        return [f"current interpreter lacks jsonschema: {exc}"]
    probe = subprocess.run(
        [sys.executable, "-c", "import json, jsonschema, sys; print(json.dumps({'executable':sys.executable,'jsonschema':jsonschema.__version__}))"],
        capture_output=True, text=True,
    )
    if probe.returncode != 0:
        errors.append(f"subprocess dependency isolation failure: {(probe.stdout + probe.stderr).strip()}")
    else:
        payload = json.loads(probe.stdout)
        if payload.get("executable") != sys.executable:
            errors.append("subprocess interpreter differs from authoritative interpreter")
    return errors


if __name__ == "__main__":
    errors = validate()
    print("PYTHON_ENVIRONMENT=PASS" if not errors else "PYTHON_ENVIRONMENT=FAIL\n- " + "\n- ".join(errors))
    raise SystemExit(0 if not errors else 2)
