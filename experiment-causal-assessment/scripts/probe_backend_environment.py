#!/usr/bin/env python3
"""Probe locked scientific backend runtimes without installing or mutating them."""

from __future__ import annotations

import importlib.metadata
import os
import re
import shutil
import subprocess
from typing import Callable

from ecae_common import ECAEError, cli_main

PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")


def _python_version(package: str) -> str:
    return importlib.metadata.version(package)


def _r_version(package: str) -> str:
    executable = os.environ.get("ECAE_RSCRIPT_BACKEND") or shutil.which("Rscript")
    if executable is None:
        raise FileNotFoundError("Rscript")
    expression = "args<-commandArgs(trailingOnly=TRUE);cat(utils::packageDescription(args[[1]],fields='Version'))"
    result = subprocess.run(
        [executable, "--vanilla", "-e", expression, package],
        text=True,
        capture_output=True,
        timeout=15,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip()[-500:])
    return result.stdout.strip()


def _r_source_revision(package: str) -> str:
    executable = os.environ.get("ECAE_RSCRIPT_BACKEND") or shutil.which("Rscript")
    if executable is None:
        raise FileNotFoundError("Rscript")
    expression = "args<-commandArgs(trailingOnly=TRUE);value<-utils::packageDescription(args[[1]],fields='RemoteSha');if(is.na(value)||!nzchar(value))quit(status=3);cat(value)"
    result = subprocess.run([executable,"--vanilla","-e",expression,package],text=True,capture_output=True,timeout=15,check=False)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "installed package lacks RemoteSha").strip()[-500:])
    return result.stdout.strip()


def probe_candidate(
    candidate: dict,
    *,
    python_version: Callable[[str], str] = _python_version,
    r_version: Callable[[str], str] = _r_version,
) -> dict:
    package = candidate.get("package")
    expected = candidate.get("version")
    ecosystem = candidate.get("ecosystem")
    if not isinstance(package, str) or not PACKAGE_RE.fullmatch(package):
        raise ECAEError("BACKEND_PACKAGE_INVALID", "Backend package name is unsafe", {"package": package})
    if not isinstance(expected, str) or not expected:
        raise ECAEError("BACKEND_VERSION_INVALID", "Backend version lock is missing")
    if ecosystem not in {"pypi", "cran", "github"}:
        return {"status": "unbound", "package": package, "expected_version": expected, "observed_version": None}
    getter = python_version if ecosystem == "pypi" else r_version
    try:
        observed = getter(package)
    except importlib.metadata.PackageNotFoundError:
        return {"status": "package_unavailable", "package": package, "expected_version": expected, "observed_version": None}
    except FileNotFoundError:
        return {"status": "runtime_unavailable", "package": package, "expected_version": expected, "observed_version": None}
    except (RuntimeError, subprocess.SubprocessError) as exc:
        return {"status": "probe_failed", "package": package, "expected_version": expected, "observed_version": None, "reason": str(exc)}
    status = "available" if observed == expected else "version_mismatch"
    result = {"status": status, "package": package, "expected_version": expected, "observed_version": observed}
    if status == "available" and ecosystem == "github":
        expected_revision = candidate.get("source_revision")
        result["expected_source_revision"] = expected_revision
        try:
            observed_revision = _r_source_revision(package)
        except (FileNotFoundError, RuntimeError, subprocess.SubprocessError) as exc:
            result.update(status="source_revision_unavailable", observed_source_revision=None, reason=str(exc))
        else:
            result["observed_source_revision"] = observed_revision
            if observed_revision != expected_revision:
                result["status"] = "source_revision_mismatch"
    return result


def probe_environment(value: dict) -> dict:
    candidates = value.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ECAEError("BACKEND_CANDIDATES_MISSING", "Probe input requires a non-empty candidates array")
    probes = []
    for candidate in candidates:
        result = probe_candidate(candidate)
        result["candidate_id"] = candidate.get("candidate_id")
        result["backend_id"] = candidate.get("backend_id")
        probes.append(result)
    return {
        "mutation_performed": False,
        "all_exact_versions_available": all(item["status"] == "available" for item in probes),
        "probes": probes,
    }


if __name__ == "__main__":
    cli_main(probe_environment, __doc__ or "Probe backend environment")
