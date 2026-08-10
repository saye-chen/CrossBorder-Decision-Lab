#!/usr/bin/env python3
"""Capture an immutable-description baseline without claiming a clean main audit."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evaluations/audit-workspace-baseline-2026-08-10.json"


def run(*args: str) -> str:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    status = run("git", "status", "--porcelain=v1")
    lock_candidates = [ROOT / "requirements.txt", ROOT / "pyproject.toml", ROOT / "uv.lock"]
    lock_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in lock_candidates if p.is_file()}
    record = {
        "audit_id": "CBDS-WORKSPACE-2026-08-10-WP0",
        "audit_standard_version": "CBDS-AUDIT-2026.07-v1",
        "audited_commit": run("git", "rev-parse", "HEAD"),
        "branch": run("git", "branch", "--show-current"),
        "workspace_clean": not bool(status),
        "conclusion_status": "workspace_snapshot" if status else "verified_commit_candidate",
        "uncommitted_paths_at_capture": [line[3:] for line in status.splitlines()],
        "captured_at": datetime.now().astimezone().isoformat(),
        "timezone": str(datetime.now().astimezone().tzinfo),
        "os": platform.platform(),
        "python_version": sys.version.split()[0],
        "dependency_lock_hashes": lock_hashes,
        "scope_boundary": "L1-L3 engineering; L4 external assurance excluded and separately reported",
        "limitations": ["existing uncommitted user work is preserved", "snapshot does not represent remote main"],
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"AUDIT_BASELINE_CAPTURED clean={record['workspace_clean']} commit={record['audited_commit']}")


if __name__ == "__main__":
    main()
