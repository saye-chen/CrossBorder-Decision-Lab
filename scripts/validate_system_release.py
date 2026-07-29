#!/usr/bin/env python3
"""Fail closed on system release-version drift across active repository artifacts."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate() -> list[str]:
    errors: list[str] = []
    release = json.loads((ROOT / "governance/system-release.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "governance/domain-architecture-registry.json").read_text(encoding="utf-8"))
    maturity = json.loads((ROOT / "governance/domain-maturity-status.json").read_text(encoding="utf-8"))
    erdg = json.loads((ROOT / "governance/erdg/contract-version.json").read_text(encoding="utf-8"))

    if registry["architecture_version"] != release["architecture_version"]:
        errors.append("architecture version differs from system release")
    if registry["governance_plane"]["contract"] != release["erdg_contract"]:
        errors.append("registry ERDG contract differs from system release")
    if erdg["runtime"] != release["erdg_runtime"] or erdg["contract"] != release["erdg_contract"]:
        errors.append("ERDG runtime or contract differs from system release")
    if erdg["schema_version"] != release["schema_semver"]:
        errors.append("ERDG schema semver differs from system release")

    domains = {item["domain_id"]: item for item in registry["domains"]}
    current_by_skill = {
        item["skill"]: release["domain_runtimes"][domain_id]
        for domain_id, item in domains.items()
        if item["availability"] == "current"
    }
    maturity_by_skill = {item["skill"]: item["runtime"] for item in maturity["domains"]}
    if maturity_by_skill != current_by_skill:
        errors.append("domain maturity runtimes differ from system release")

    for skill, runtime in current_by_skill.items():
        skill_text = (ROOT / skill / "SKILL.md").read_text(encoding="utf-8")
        if runtime not in skill_text:
            errors.append(f"{skill}: SKILL runtime differs from system release")
        if release["erdg_contract"] not in skill_text:
            errors.append(f"{skill}: ERDG contract differs from system release")
        adapter = json.loads(
            (ROOT / "governance/erdg/adapters" / skill / "adapter.json").read_text(encoding="utf-8")
        )
        if adapter.get("version") != release["adapter_semver"]:
            errors.append(f"{skill}: adapter semver differs from system release")
        if adapter.get("contract") != release["erdg_contract"]:
            errors.append(f"{skill}: adapter contract differs from system release")

    for homepage in ("README.md", "README.en.md"):
        text = (ROOT / homepage).read_text(encoding="utf-8")
        for required in (release["architecture_version"], release["erdg_contract"], *current_by_skill.values()):
            if required not in text:
                errors.append(f"{homepage}: missing current release marker {required}")

    exceptions = set(release["historical_snapshot_exceptions"])
    version_pattern = re.compile(r"\b[A-Z][A-Z0-9-]*-2026\.(\d+)\b")
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in exceptions:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        stale = sorted({match.group(0) for match in version_pattern.finditer(text) if match.group(1) != "07"})
        if stale:
            errors.append(f"{relative}: stale active release markers {stale}")
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        raise SystemExit("System release validation failed:\n- " + "\n- ".join(failures))
    print("System release validation passed: all active domains and ERDG aligned to 2026.07.")
