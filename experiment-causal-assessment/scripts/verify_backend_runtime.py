#!/usr/bin/env python3
"""Verify exact ECAE runtimes, backend packages, source pins, and adapter hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(command: list[str], timeout: int = 45) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)


def _python_probe(executable: str, expected_runtime: str, requirements: Path) -> dict:
    locked = {}
    for line in requirements.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            package, version = line.split("==", 1)
            locked[package] = version
    expression = (
        "import importlib.metadata,json,platform,sys;"
        "names=json.loads(sys.argv[1]);"
        "print(json.dumps({'runtime':platform.python_version(),"
        "'packages':{name:importlib.metadata.version(name) for name in names}}))"
    )
    result = _run([executable, "-c", expression, json.dumps(sorted(locked))])
    if result.returncode:
        return {"status": "probe_failed", "stderr": result.stderr[-1000:]}
    observed = json.loads(result.stdout)
    mismatches = {
        name: {"expected": version, "observed": observed["packages"].get(name)}
        for name, version in locked.items()
        if observed["packages"].get(name) != version
    }
    if observed["runtime"] != expected_runtime:
        mismatches["python_runtime"] = {"expected": expected_runtime, "observed": observed["runtime"]}
    return {"status": "pass" if not mismatches else "version_mismatch", "observed": observed, "mismatches": mismatches}


def _r_probe(executable: str, expected_runtime: str, package_lock: Path) -> dict:
    lock = json.loads(package_lock.read_text(encoding="utf-8"))
    expected = {item["package"]: item["version"] for item in lock["packages"]}
    expression = (
        "args<-commandArgs(trailingOnly=TRUE);"
        "packages<-strsplit(args[[1]],',',fixed=TRUE)[[1]];"
        "versions<-vapply(packages,function(p) utils::packageDescription(p,fields='Version'),character(1));"
        "revision<-utils::packageDescription('synthdid',fields='RemoteSha');"
        "cat(jsonlite::toJSON(list(runtime=as.character(getRversion()),packages=as.list(versions),synthdid_revision=revision),auto_unbox=TRUE))"
    )
    result = _run([executable, "--vanilla", "-e", expression, ",".join(expected)], timeout=90)
    if result.returncode:
        return {"status": "probe_failed", "stderr": (result.stderr or result.stdout)[-1000:]}
    observed = json.loads(result.stdout)
    mismatches = {
        name: {"expected": version, "observed": observed["packages"].get(name)}
        for name, version in expected.items()
        if observed["packages"].get(name) != version
    }
    if observed["runtime"] != expected_runtime:
        mismatches["r_runtime"] = {"expected": expected_runtime, "observed": observed["runtime"]}
    synthdid = next(item for item in lock["packages"] if item["package"] == "synthdid")
    if observed.get("synthdid_revision") != synthdid["revision"]:
        mismatches["synthdid_revision"] = {"expected": synthdid["revision"], "observed": observed.get("synthdid_revision")}
    return {"status": "pass" if not mismatches else "version_mismatch", "observed": observed, "mismatches": mismatches}


def _integrity_probe(lock: dict) -> dict:
    mismatches = {}
    observed = {}
    for relative, expected in lock["adapter_integrity"]["adapters"].items():
        digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        observed[relative] = digest
        if digest != expected:
            mismatches[relative] = {"expected": expected, "observed": digest}
    return {"status": "pass" if not mismatches else "hash_mismatch", "observed": observed, "mismatches": mismatches}


def verify(python_executable: str | None = None, rscript_executable: str | None = None) -> dict:
    lock = json.loads((ROOT / "backends/runtime-lock.json").read_text(encoding="utf-8"))
    python_executable = python_executable or os.environ.get(lock["python"]["executable_env"])
    rscript_executable = rscript_executable or os.environ.get(lock["r"]["executable_env"])
    checks = {"adapter_integrity": _integrity_probe(lock)}
    checks["python"] = (
        {"status": "runtime_not_bound"}
        if not python_executable
        else _python_probe(python_executable, lock["python"]["version"], ROOT / lock["python"]["requirements_ref"])
    )
    checks["r"] = (
        {"status": "runtime_not_bound"}
        if not rscript_executable
        else _r_probe(rscript_executable, lock["r"]["version"], ROOT / lock["r"]["packages_ref"])
    )
    return {
        "schema_version": "1.0.0",
        "qualification": "persistent_runtime_and_integrity_only_not_external_backend_verification",
        "checks": checks,
        "all_bound_checks_pass": all(item["status"] == "pass" for item in checks.values()),
        "registry_promotion_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python")
    parser.add_argument("--rscript")
    parser.add_argument("--require-runtimes", action="store_true")
    args = parser.parse_args()
    report = verify(args.python, args.rscript)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    statuses = {item["status"] for item in report["checks"].values()}
    if args.require_runtimes and "runtime_not_bound" in statuses:
        return 2
    return 0 if all(status in {"pass", "runtime_not_bound"} for status in statuses) else 2


if __name__ == "__main__":
    raise SystemExit(main())
