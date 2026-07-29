#!/usr/bin/env python3
"""Generate a reproducible repository audit evidence package without external writes."""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".toml", ".txt"}
SECRET_PATTERNS = {
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
}
ABSOLUTE_USER_PATH = re.compile(r"/" + r"Users/[^/\s]+/")


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tracked_files() -> list[Path]:
    result = run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"])
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return [ROOT / item for item in result.stdout.split("\0") if item]


def discover_tests(files: list[Path]) -> dict:
    rows = []
    total_cases = 0
    total_assertions = 0
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix != ".py" or not path.name.startswith("test_"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as exc:
            rows.append({"path": rel, "parse_error": str(exc), "cases": 0, "assertion_calls": 0})
            continue
        cases = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
            for node in ast.walk(tree)
        )
        assertions = sum(
            isinstance(node, ast.Assert)
            or (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr.startswith("assert")
            )
            for node in ast.walk(tree)
        )
        rows.append({"path": rel, "cases": cases, "assertion_calls": assertions})
        total_cases += cases
        total_assertions += assertions
    return {
        "test_files": len(rows),
        "static_test_cases": total_cases,
        "static_assertion_calls": total_assertions,
        "note": "Static inventory; parameterized and subprocess assertions may differ from runtime counts.",
        "files": rows,
    }


def security_scan(files: list[Path]) -> dict:
    findings = []
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(ROOT).as_posix()
        for pattern_id, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append({"severity": "P0", "pattern": pattern_id, "path": rel})
        if ABSOLUTE_USER_PATH.search(text):
            findings.append({"severity": "P1", "pattern": "absolute_user_path", "path": rel})
    tracked_cache = [
        path.relative_to(ROOT).as_posix()
        for path in files
        if "__pycache__" in path.parts or path.suffix == ".pyc"
    ]
    executable_non_scripts = []
    for path in files:
        if path.is_file() and os.access(path, os.X_OK) and path.suffix not in {".py", ".sh"}:
            executable_non_scripts.append(path.relative_to(ROOT).as_posix())
    return {
        "status": "PASS" if not findings and not tracked_cache and not executable_non_scripts else "FAIL",
        "findings": findings,
        "tracked_cache": tracked_cache,
        "executable_non_scripts": executable_non_scripts,
        "limitations": [
            "Pattern scan is a release guard, not a substitute for a dedicated secret scanner.",
            "License compatibility and external privacy authorization still require owner review.",
        ],
    }


def git_snapshot() -> dict:
    head = run(["git", "rev-parse", "HEAD"])
    branch = run(["git", "branch", "--show-current"])
    status = run(["git", "status", "--porcelain=v1"])
    return {
        "audited_commit": head.stdout.strip(),
        "branch": branch.stdout.strip(),
        "workspace_clean": not bool(status.stdout.strip()),
        "uncommitted_paths": [line[3:] for line in status.stdout.splitlines() if len(line) > 3],
    }


def changed_paths() -> list[str]:
    commands = (
        ["git", "diff", "--name-only", "--diff-filter=ACDMRTUXB", "HEAD"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    paths: set[str] = set()
    for command in commands:
        result = run(command)
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or f"{' '.join(command)} failed")
        paths.update(line for line in result.stdout.splitlines() if line)
    return sorted(paths)


def change_impact(paths: list[str]) -> dict:
    manifest = json.loads(
        (ROOT / "governance/change-impact-manifest.json").read_text(encoding="utf-8")
    )
    affected: dict[str, dict] = {}
    mapped: set[str] = set()
    for contract_id, spec in manifest["contracts"].items():
        watched: set[str] = set()
        for key in ("authoritative_sources", "retired_sources", "consumers", "validators", "tests", "evaluations"):
            watched.update(spec.get(key, []))
        matches = sorted(
            path
            for path in paths
            if any(path == watch or path.startswith(watch.rstrip("/") + "/") for watch in watched)
        )
        if matches:
            affected[contract_id] = {"changed": matches, "owner": spec["owner"]}
            mapped.update(matches)
    unmapped = sorted(set(paths) - mapped)
    return {
        "status": "PASS" if not unmapped else "FAIL",
        "changed_paths": paths,
        "affected_contracts": affected,
        "unmapped_paths": unmapped,
    }


def execute_check(check_id: str, command: list[str], log_dir: Path) -> dict:
    started = dt.datetime.now(dt.timezone.utc)
    before = time.monotonic()
    result = run(command)
    duration = round(time.monotonic() - before, 3)
    log_path = log_dir / f"{check_id}.log"
    log_path.write_text(
        f"$ {' '.join(command)}\n\n[stdout]\n{result.stdout}\n[stderr]\n{result.stderr}",
        encoding="utf-8",
    )
    return {
        "id": check_id,
        "command": command,
        "started_at": started.isoformat(),
        "duration_seconds": duration,
        "exit_code": result.returncode,
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "log": log_path.relative_to(log_dir.parent).as_posix(),
        "log_sha256": sha256(log_path),
    }


def audit_verdict(checks: list[dict], security_status: str, impact_status: str, clean: bool) -> str:
    if (
        not all(item["status"] == "PASS" for item in checks)
        or security_status != "PASS"
        or impact_status != "PASS"
    ):
        return "FAIL"
    return "PASS_CLEAN_CANDIDATE" if clean else "PASS_WORKTREE_DIAGNOSTIC"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="New evidence directory. Defaults to Downloads/CrossBorder_Decision_Lab_Audit_Evidence/<UTC timestamp>.",
    )
    args = parser.parse_args()
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = (
        args.output_dir
        or Path.home() / "Downloads/CrossBorder_Decision_Lab_Audit_Evidence" / timestamp
    ).resolve()
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing evidence directory: {output}")
    output.mkdir(parents=True)
    logs = output / "logs"
    logs.mkdir()

    started = dt.datetime.now(dt.timezone.utc)
    snapshot = git_snapshot()
    files = tracked_files()
    dependency = ROOT / "requirements-dev.txt"
    inventory = discover_tests(files)
    security = security_scan(files)
    impact = change_impact(changed_paths())
    checks = [
        execute_check("diff-check", ["git", "diff", "--check"], logs),
        execute_check(
            "release-compliance",
            [sys.executable, "scripts/validate_release_compliance.py"],
            logs,
        ),
        execute_check(
            "erdg-capacity",
            [sys.executable, "governance/erdg/scripts/validate_erdg_capacity.py"],
            logs,
        ),
        execute_check(
            "full-repository-audit",
            [sys.executable, "scripts/test_full_repository_audit.py"],
            logs,
        ),
    ]
    evidence = {
        "audit_id": f"CBDS-AUDIT-{timestamp}",
        "audit_standard_version": "CBDS-AUDIT-2026.07-v1",
        **snapshot,
        "audit_started_at": started.isoformat(),
        "audit_finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "timezone": "UTC",
        "os": platform.platform(),
        "python_version": platform.python_version(),
        "dependency_lock": "requirements-dev.txt" if dependency.is_file() else None,
        "dependency_lock_sha256": sha256(dependency) if dependency.is_file() else None,
        "test_inventory": inventory,
        "security_release_scan": security,
        "change_impact": impact,
        "checks": checks,
        "maturity_boundary": "controlled pilot until authorized real L4 replay and independent review",
        "verdict": audit_verdict(
            checks, security["status"], impact["status"], snapshot["workspace_clean"]
        ),
        "reproducibility_gate": "PASS" if snapshot["workspace_clean"] else "FAIL_DIRTY_WORKTREE",
    }
    json_path = output / "audit-evidence.json"
    json_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    score_path = output / "audit-score.json"
    score_result = run(
        [
            sys.executable,
            "scripts/score_system_audit.py",
            str(json_path),
            "--output",
            str(score_path),
        ]
    )
    if score_result.returncode:
        raise SystemExit(score_result.stderr or score_result.stdout)
    score = json.loads(score_path.read_text(encoding="utf-8"))
    report_path = output / "README.md"
    report_path.write_text(
        "\n".join(
            [
                f"# {evidence['audit_id']}",
                "",
                f"- Commit: `{snapshot['audited_commit']}`",
                f"- Branch: `{snapshot['branch']}`",
                f"- Workspace clean: `{str(snapshot['workspace_clean']).lower()}`",
                f"- Reproducibility gate: `{evidence['reproducibility_gate']}`",
                f"- Security/release scan: `{security['status']}`",
                f"- Change-impact closure: `{impact['status']}`",
                f"- Full verdict: `{evidence['verdict']}`",
                f"- Audit score: `{score['score']}/{score['maximum']} ({score['grade']})`",
                f"- Test files: `{inventory['test_files']}`",
                f"- Static test cases: `{inventory['static_test_cases']}`",
                f"- Static assertion calls: `{inventory['static_assertion_calls']}`",
                "",
                (
                    "This package records a clean local candidate, not proof that the same commit "
                    "is published on GitHub `main`."
                    if snapshot["workspace_clean"]
                    else "This package records a working-tree diagnostic. It must not be represented "
                    "as a clean `main` release audit."
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )
    manifest = {
        "artifacts": [
            {
                "path": path.relative_to(output).as_posix(),
                "sha256": sha256(path),
            }
            for path in sorted(output.rglob("*"))
            if path.is_file() and path.name != "artifact-manifest.json"
        ]
    }
    (output / "artifact-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(output)
    return 0 if evidence["verdict"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
