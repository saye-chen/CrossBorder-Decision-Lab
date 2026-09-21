#!/usr/bin/env python3
"""Validate every registered report asset through one shared quality boundary."""

from __future__ import annotations

import fnmatch
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "governance/report-contract-registry.json"
DELIVERABLES_PATH = ROOT / "governance/interaction/operator-deliverables.json"


def _load_quality():
    spec = importlib.util.spec_from_file_location("report_quality", ROOT / "scripts/evaluate_report_quality.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


QUALITY = _load_quality()


def _paths(patterns: Iterable[str]) -> list[Path]:
    found: set[Path] = set()
    for pattern in patterns:
        if any(token in pattern for token in ("*", "?", "[")):
            found.update(ROOT.glob(pattern))
        else:
            found.add(ROOT / pattern)
    return sorted(found)


def _walk(value: Any, prefix: str = "") -> Iterable[tuple[str, Any]]:
    yield prefix, value
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield from _walk(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{prefix}[{index}]")


def _has_key(value: Any, names: set[str]) -> bool:
    return any(path.rsplit(".", 1)[-1].split("[")[0] in names for path, _ in _walk(value))


def _nonempty(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, (str, list, dict, tuple, set)):
        return bool(value)
    return True


def _has_nonempty_key(value: Any, names: set[str]) -> bool:
    return any(
        path.rsplit(".", 1)[-1].split("[")[0] in names and _nonempty(child)
        for path, child in _walk(value)
    )


def _validate_card(text: str) -> list[str]:
    required = {
        "对象": "object boundary",
        "运行时": "runtime version",
        "结论": "decision conclusion",
        "证据": "evidence boundary",
        "反证": "counterevidence",
        "责任人": "action owner",
        "观察窗": "observation window",
        "成功条件": "success condition",
        "停止条件": "stop condition",
        "回滚": "rollback",
        "主权": "decision sovereignty",
        "翻转条件": "flip condition",
    }
    return [f"missing_card_field:{label}" for marker, label in required.items() if marker not in text]


def _validate_structured_row(row: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    groups = {
        "identity": ({"report_id", "decision_id", "evaluation_id", "case_id"}, "report identity"),
        "scope": ({"object_ref", "scope", "scope_ref", "object_scope", "object"}, "object and scope"),
        "conclusion": ({"current_conclusion", "decision_state", "decision", "executive_summary", "gate_status", "status"}, "conclusion/state"),
        "evidence": ({"evidence", "claims", "checks", "results", "ledgers"}, "evidence or result ledger"),
        "counterevidence": ({"counterevidence", "conflicts", "limitations", "gaps", "missing_data", "missing_and_expired"}, "counterevidence/limitations"),
        "action": ({"actions", "allowed_actions", "blocked_actions", "action_ceiling", "candidates", "alternatives"}, "action boundary"),
        "success": ({"success_conditions", "success", "exit_conditions"}, "success conditions"),
        "stop": ({"stop_conditions", "stop", "redlines", "blocked_actions"}, "stop controls"),
        "rollback": ({"rollback", "rollback_conditions", "recovery"}, "rollback/recovery"),
        "lineage": ({"lineage", "chain_id", "generated_by", "source_ref", "runtime_version", "ledgers", "professional_analysis"}, "lineage"),
    }
    for name, (keys, label) in groups.items():
        if not _has_nonempty_key(row, keys):
            errors.append(f"{path}:missing_{name}:{label}")
    if "external_write" in row and row.get("external_write") is not False:
        errors.append(f"{path}:external_write_must_be_false")
    has_usage_boundary = _has_nonempty_key(row, {"allowed_uses"}) and _has_nonempty_key(row, {"forbidden_uses"})
    has_action_boundary = _has_nonempty_key(row, {"allowed_actions"}) and _has_nonempty_key(row, {"blocked_actions"})
    has_governance_boundary = _has_nonempty_key(row, {"sovereignty"}) and _has_nonempty_key(row, {"execution_controls"})
    if not (has_usage_boundary or has_action_boundary or has_governance_boundary):
        errors.append(f"{path}:missing_usage_or_action_boundary")
    return errors


def _validate_structured(data: Any, path: str) -> list[str]:
    rows: list[dict[str, Any]]
    if isinstance(data, dict) and isinstance(data.get("reports"), list):
        rows = [row for row in data["reports"] if isinstance(row, dict)]
        if not rows:
            return [f"{path}:reports_empty"]
    elif isinstance(data, dict):
        rows = [data]
    else:
        return [f"{path}:report_root_must_be_object"]
    errors: list[str] = []
    for index, row in enumerate(rows):
        errors.extend(_validate_structured_row(row, f"{path}[{index}]"))
    return errors


def _validate_foundation(data: dict[str, Any], path: str) -> list[str]:
    if path.endswith("simulation-report.json"):
        required = {"schema_version", "evaluation_id", "generated_by", "checks", "limitations", "simulation_policy", "status"}
    else:
        required = {"schema_version", "report_id", "status", "environment", "mutation_scope", "results", "release_effect"}
    return [f"{path}:missing_foundation_field:{key}" for key in sorted(required - set(data))]


def _validate_deliverables() -> list[str]:
    errors: list[str] = []
    architecture = json.loads((ROOT / "governance/domain-architecture-registry.json").read_text(encoding="utf-8"))
    foundations = json.loads((ROOT / "governance/foundation-capability-registry.json").read_text(encoding="utf-8"))
    expected = {row["skill"] for row in architecture["domains"] if row.get("availability") == "current"}
    expected |= {row["name"] for row in foundations["foundations"] if row.get("availability") == "current"}
    deliverables = json.loads(DELIVERABLES_PATH.read_text(encoding="utf-8"))
    rows = deliverables.get("domains", [])
    actual = {row.get("skill") for row in rows}
    if actual != expected or len(rows) != len(expected):
        errors.append(f"operator-deliverables coverage drift missing={sorted(expected - actual)} extra={sorted(actual - expected)}")
    for row in rows:
        sections = row.get("required_sections", [])
        if len(sections) != 6 or len(set(sections)) != 6:
            errors.append(f"{row.get('skill')}: deliverable must contain six distinct sections")
        if not row.get("stop"):
            errors.append(f"{row.get('skill')}: deliverable stop policy missing")
    return errors


def _candidate_report_paths() -> set[Path]:
    candidates = set(ROOT.glob("*/evaluations/golden/*.md"))
    candidates.update(ROOT.glob("evaluations/golden/*.md"))
    candidates.update(ROOT.glob("evaluations/golden-reports/*.md"))
    candidates.update(ROOT.glob("evaluations/extreme-reports/*.md"))
    candidates.update(ROOT.glob("*/evaluations/golden/*-report.json"))
    candidates.add(ROOT / "supplier-procurement-production-quality-decision/evaluations/golden-professional-reports.json")
    candidates.update(ROOT.glob("experiment-causal-assessment/evaluations/*-report.json"))
    return {path for path in candidates if path.is_file()}


def validate() -> list[str]:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []
    seen: set[Path] = set()
    for asset in registry.get("assets", []):
        paths = _paths(asset.get("paths", []))
        if not paths:
            errors.append(f"{asset.get('id')}: no report assets resolved")
            continue
        for path in paths:
            if not path.is_file():
                errors.append(f"{asset.get('id')}: missing report asset {path.relative_to(ROOT)}")
                continue
            seen.add(path)
            relative = str(path.relative_to(ROOT))
            if asset["format"] == "markdown":
                text = path.read_text(encoding="utf-8")
                if asset["profile"] == "full":
                    result = QUALITY.score_report(text, "full")
                    if result["result"] != "PASS" or result["score"] != 100.0:
                        errors.append(f"{relative}: full_report_gate:{result}")
                elif asset["profile"] == "contract":
                    result = QUALITY.score_report(text, "contract")
                    if result["result"] != "PASS" or result["score"] != 100.0:
                        errors.append(f"{relative}: report_contract_gate:{result}")
                elif asset["profile"] == "card":
                    errors.extend(f"{relative}:{error}" for error in _validate_card(text))
            elif asset["profile"] == "structured":
                try:
                    errors.extend(_validate_structured(json.loads(path.read_text(encoding="utf-8")), relative))
                except (OSError, json.JSONDecodeError) as exc:
                    errors.append(f"{relative}:invalid_json:{exc}")
            elif asset["profile"] == "foundation":
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    errors.extend(_validate_foundation(data, relative))
                except (OSError, json.JSONDecodeError) as exc:
                    errors.append(f"{relative}:invalid_json:{exc}")
            else:
                errors.append(f"{relative}:unknown_profile:{asset['profile']}")
    errors.extend(_validate_deliverables())
    unregistered = sorted(_candidate_report_paths() - seen)
    errors.extend(f"unregistered_report_asset:{path.relative_to(ROOT)}" for path in unregistered)
    if len(seen) < 1:
        errors.append("report registry resolved no assets")
    return errors


if __name__ == "__main__":
    failures = validate()
    print("REPORT_CONTRACTS=PASS" if not failures else "REPORT_CONTRACTS=FAIL\n- " + "\n- ".join(failures))
    raise SystemExit(0 if not failures else 2)
