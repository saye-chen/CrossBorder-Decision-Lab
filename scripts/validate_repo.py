#!/usr/bin/env python3
"""Validate repository conventions that the generic Skill validator cannot enforce.

Covers RULES.md section 7 checks:
- Frontmatter keys = {name, description}, with a directory-matching name
- Runtime version declaration present
- Broken local links in SKILL.md and reference files
- Every nested reference is reachable from SKILL.md
- Temporary workspace and cleanup policy is declared
- VLB e-commerce weights sum to 100
- agents/openai.yaml has required fields
- Active tests and Golden reports use the registered current runtimes
- GitHub release workflow covers every Skill and the full audit
- README file inventory matches repo
- No __pycache__ or .pyc artifacts
- Cross-skill version consistency
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^运行时版本：`([A-Z][A-Z0-9-]*-\d{4}\.\d{2})`。$", re.MULTILINE)
LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")

    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return [f"{skill_file}: invalid frontmatter"]
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    keys = set(fields)
    if keys != {"name", "description"}:
        errors.append(f"{skill_file}: frontmatter keys must be exactly name and description")
    name = fields.get("name", "")
    if name != skill_dir.name:
        errors.append(f"{skill_file}: name must match directory {skill_dir.name!r}")
    if name and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append(f"{skill_file}: name must use lowercase hyphen-case")
    description = fields.get("description", "")
    if not description or len(description) > 1024:
        errors.append(f"{skill_file}: description must contain 1-1024 characters")
    if not VERSION_RE.search(text):
        errors.append(f"{skill_file}: missing runtime version declaration")
    if "${TMPDIR:-/tmp}" not in text and "mktemp -d" not in text:
        errors.append(f"{skill_file}: missing managed or ephemeral temporary-workspace policy")
    if not any(marker in text for marker in (".task-owner.json", "mktemp -d")):
        errors.append(f"{skill_file}: temporary workspace must have an ownership boundary")
    if not any(marker in text for marker in ("只删除", "仅删除", "只清理", "删除整个任务临时目录", "清理失败", "verify the task directory no longer exists")):
        errors.append(f"{skill_file}: temporary workspace must define bounded cleanup and verification")

    # Check links in SKILL.md
    for target in LINK_RE.findall(text):
        if "://" in target or target.startswith("#"):
            continue
        local_target = target.split("#", 1)[0]
        if local_target and not (skill_dir / local_target).exists():
            errors.append(f"{skill_file}: broken local link {target}")

    # Check links in all reference files
    for ref_file in (skill_dir / "references").rglob("*.md"):
        ref_text = ref_file.read_text(encoding="utf-8")
        for target in LINK_RE.findall(ref_text):
            if "://" in target or target.startswith("#"):
                continue
            local_target = target.split("#", 1)[0]
            if local_target and not (ref_file.parent / local_target).exists():
                errors.append(f"{ref_file.relative_to(ROOT)}: broken local link {target}")

    return errors


def validate_video_weights() -> list[str]:
    skill_file = ROOT / "video-link-breakdown" / "references" / "scoring-model.md"
    text = skill_file.read_text(encoding="utf-8")
    table_rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in text.splitlines()
        if line.startswith("|")
    ]
    header = next((row for row in table_rows if "电商成交" in row), None)
    if header is None:
        return [f"{skill_file}: could not locate e-commerce weight column"]
    column = header.index("电商成交")
    rows = [row for row in table_rows if len(row) > column and re.fullmatch(r"\d+", row[column])]
    total = sum(int(row[column]) for row in rows)
    return [] if total == 100 else [f"{skill_file}: e-commerce weights total {total}%, expected 100%"]


def validate_agents_yaml() -> list[str]:
    """Check agents/openai.yaml follows the official UI metadata contract."""
    errors: list[str] = []
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        yaml_file = skill_dir / "agents" / "openai.yaml"
        if not yaml_file.exists():
            continue
        text = yaml_file.read_text(encoding="utf-8")
        skill_name = skill_dir.name
        required_fields = ["display_name", "short_description", "default_prompt"]
        allowed_fields = {"display_name", "short_description", "default_prompt", "icon_small", "icon_large", "brand_color"}
        content_lines = [
            (number, line)
            for number, line in enumerate(text.splitlines(), 1)
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if not content_lines or content_lines[0][1] != "interface:":
            errors.append(f"{yaml_file.relative_to(ROOT)}: top level must be exactly 'interface:'")
            continue
        fields: dict[str, str] = {}
        for number, line in content_lines[1:]:
            match = re.fullmatch(r'  ([a-z_]+):\s*("(?:[^"\\]|\\.)*")\s*', line)
            if not match:
                errors.append(
                    f"{yaml_file.relative_to(ROOT)}:{number}: interface values must be double-quoted strings"
                )
                continue
            field, encoded = match.groups()
            if field in fields:
                errors.append(f"{yaml_file.relative_to(ROOT)}:{number}: duplicate field '{field}'")
                continue
            try:
                fields[field] = json.loads(encoded)
            except json.JSONDecodeError:
                errors.append(f"{yaml_file.relative_to(ROOT)}:{number}: invalid quoted string")
        for field in required_fields:
            if not fields.get(field):
                errors.append(f"{yaml_file.relative_to(ROOT)}: missing required field '{field}'")
        unknown_fields = sorted(set(fields) - allowed_fields)
        if unknown_fields:
            errors.append(f"{yaml_file.relative_to(ROOT)}: unsupported interface fields {unknown_fields}")
        short_description = fields.get("short_description", "")
        if short_description and not 25 <= len(short_description) <= 64:
            errors.append(f"{yaml_file.relative_to(ROOT)}: short_description must be 25-64 characters")
        default_prompt = fields.get("default_prompt", "")
        if default_prompt and f"${skill_name}" not in default_prompt:
            errors.append(f"{yaml_file.relative_to(ROOT)}: default_prompt must mention ${skill_name}")
        # runtime is not an official agents/openai.yaml interface field; the
        # canonical runtime lives in SKILL.md and executable decision contracts.
        if "runtime" in fields:
            errors.append(f"{yaml_file.relative_to(ROOT)}: runtime is not an official interface field; keep it in SKILL.md")
    return errors


def validate_readme_inventory() -> list[str]:
    """Check README mentions all skill directories and key files."""
    errors: list[str] = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    # Check all skill directories are mentioned
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        if skill_dir.name not in readme:
            errors.append(f"README.md: missing skill directory '{skill_dir.name}'")

    # Check repository-level governance and dependency files are mentioned
    for required_file in ["RULES.md", "LICENSE", "requirements-dev.txt"]:
        if required_file not in readme:
            errors.append(f"README.md: missing reference to '{required_file}'")

    # Check model versions in README match SKILL.md
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        version_match = re.search(r"`([A-Z][A-Z0-9-]*-\d{4}\.\d{2})`", skill_text)
        if version_match and version_match.group(1) not in readme:
            errors.append(
                f"README.md: model version {version_match.group(1)} from "
                f"{skill_dir.name}/SKILL.md not found"
            )

    return errors


def validate_no_artifacts() -> list[str]:
    """Check no __pycache__, .pyc, or other artifacts remain."""
    errors: list[str] = []
    for pycache in ROOT.rglob("__pycache__"):
        if ".git" not in pycache.parts:
            errors.append(f"artifact: {pycache.relative_to(ROOT)} directory exists")
    for pyc in ROOT.rglob("*.pyc"):
        if ".git" not in pyc.parts:
            errors.append(f"artifact: {pyc.relative_to(ROOT)} exists")
    return errors


def validate_cross_skill_versions() -> list[str]:
    """Check model versions are consistent between SKILL.md and RULES.md."""
    errors: list[str] = []
    rules_text = (ROOT / "RULES.md").read_text(encoding="utf-8")

    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        version_match = re.search(r"`([A-Z][A-Z0-9-]*-\d{4}\.\d{2})`", skill_text)
        if version_match:
            version = version_match.group(1)
            # Version should appear in at least one of README or RULES
            readme = (ROOT / "README.md").read_text(encoding="utf-8")
            if version not in readme and version not in rules_text:
                errors.append(
                    f"{skill_dir.name}: version {version} not found in README.md or RULES.md"
                )
            release_audit = (ROOT / "scripts/test_full_repository_audit.py").read_text(encoding="utf-8")
            if version not in release_audit:
                errors.append(
                    f"scripts/test_full_repository_audit.py: current runtime {version} "
                    f"for {skill_dir.name} is not exercised"
                )
    return errors


def validate_reference_routing() -> list[str]:
    """Check every nested reference is reachable from SKILL.md."""
    errors: list[str] = []
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        skill_file = skill_dir / "SKILL.md"
        ref_dir = skill_dir / "references"
        if not ref_dir.exists():
            continue
        all_refs = {path.resolve() for path in ref_dir.rglob("*.md")}
        names: dict[str, list[Path]] = {}
        for ref_file in all_refs:
            names.setdefault(ref_file.name, []).append(ref_file)
        reachable: set[Path] = set()
        queue = [skill_file.resolve()]
        visited: set[Path] = set()
        while queue:
            source = queue.pop()
            if source in visited:
                continue
            visited.add(source)
            source_text = source.read_text(encoding="utf-8")
            candidates: set[Path] = set()
            for target in LINK_RE.findall(source_text):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (source.parent / target.split("#", 1)[0]).resolve()
                if resolved in all_refs:
                    candidates.add(resolved)
            for ref_file in all_refs:
                relative = ref_file.relative_to(skill_dir.resolve()).as_posix()
                if relative in source_text or (
                    len(names[ref_file.name]) == 1 and ref_file.name in source_text
                ):
                    candidates.add(ref_file)
            for candidate in candidates - reachable:
                reachable.add(candidate)
                queue.append(candidate)
        for ref_file in sorted(all_refs - reachable):
            errors.append(
                f"{skill_dir.name}: reference file "
                f"'{ref_file.relative_to(skill_dir.resolve()).as_posix()}' is unreachable from SKILL.md"
            )
    return errors


def current_runtime_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        match = VERSION_RE.search((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
        if match:
            versions[skill_dir.name] = match.group(1)
    return versions


def validate_current_runtime_lineage() -> list[str]:
    """Reject stale runtime IDs in active code, fixtures, and Golden reports."""
    errors: list[str] = []
    expected_by_prefix = {
        version.split("-", 1)[0]: version for version in current_runtime_versions().values()
    }
    active_paths = set((ROOT / "scripts").rglob("*.py"))
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        active_paths.update((skill_dir / "scripts").rglob("*.py"))
        evaluation_dir = skill_dir / "evaluations"
        if evaluation_dir.exists():
            active_paths.update(evaluation_dir.rglob("*.md"))
            active_paths.update(evaluation_dir.rglob("*.json"))
    for directory in ("golden", "golden-reports", "extreme-reports", "lineage", "d07", "d08"):
        root = ROOT / "evaluations" / directory
        if root.exists():
            active_paths.update(root.rglob("*.md"))
            active_paths.update(root.rglob("*.json"))
    runtime_re = re.compile(r"\b([A-Z][A-Z0-9]*)-20\d{2}\.\d{2}\b")
    for path in sorted(active_paths):
        text = path.read_text(encoding="utf-8")
        for match in runtime_re.finditer(text):
            expected = expected_by_prefix.get(match.group(1))
            if expected and match.group(0) != expected:
                errors.append(
                    f"{path.relative_to(ROOT)}: active runtime {match.group(0)} must be {expected}"
                )
    return errors


def validate_ci_release_gate() -> list[str]:
    errors: list[str] = []
    workflow = ROOT / ".github/workflows/expert-release.yml"
    if not workflow.is_file():
        return [".github/workflows/expert-release.yml is required"]
    text = workflow.read_text(encoding="utf-8")
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        if skill_dir.name not in text:
            errors.append(f"expert-release.yml: missing Skill coverage for {skill_dir.name}")
    for command in (
        "python3 -m pip install -r requirements-dev.txt",
        "python3 scripts/test_full_repository_audit.py",
    ):
        if command not in text:
            errors.append(f"expert-release.yml: missing release command '{command}'")
    return errors

def validate_change_impact_manifest() -> list[str]:
    errors: list[str] = []
    path = ROOT / "governance/change-impact-manifest.json"
    if not path.exists():
        return ["governance/change-impact-manifest.json is required"]
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {"owner", "authoritative_sources", "consumers", "validators", "tests", "evaluations"}
    for cid, spec in data.get("contracts", {}).items():
        missing = required - set(spec)
        if missing:
            errors.append(f"impact contract {cid}: missing {sorted(missing)}")
        for key in required - {"owner"}:
            for target in spec.get(key, []):
                if not (ROOT / target).exists():
                    errors.append(f"impact contract {cid}: missing target {target}")
    return errors

def validate_domain_contract_entrypoints() -> list[str]:
    errors = []
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        entry = skill_dir / "scripts/validate_decision_contract.py"
        if not entry.exists():
            errors.append(f"{skill_dir.name}: missing decision contract validator")
        elif "validate_decision_contract.py" not in (skill_dir / "SKILL.md").read_text(encoding="utf-8"):
            errors.append(f"{skill_dir.name}: decision contract validator is not routed")
    return errors


def validate_vlb_handoff_entrypoints() -> list[str]:
    errors: list[str] = []
    skill = ROOT / "video-link-breakdown"
    skill_text = (skill / "SKILL.md").read_text(encoding="utf-8")
    for name in ("validate_selection_handoff.py", "validate_brief_seed.py", "test_handoff_contracts.py"):
        path = skill / "scripts" / name
        if not path.is_file():
            errors.append(f"video-link-breakdown: missing {name}")
        if name.startswith("validate_") and name not in skill_text:
            errors.append(f"video-link-breakdown: {name} is not routed from SKILL.md")
    return errors


def main() -> int:
    skill_dirs = sorted(path.parent for path in ROOT.glob("*/SKILL.md"))
    errors: list[str] = []

    # Core skill validation
    for skill_dir in skill_dirs:
        errors.extend(validate_skill(skill_dir))

    # Weight validation
    errors.extend(validate_video_weights())

    # agents/openai.yaml validation
    errors.extend(validate_agents_yaml())

    # README inventory sync
    errors.extend(validate_readme_inventory())

    # Artifact detection
    errors.extend(validate_no_artifacts())

    # Cross-skill version consistency
    errors.extend(validate_cross_skill_versions())

    # Reference routing completeness
    errors.extend(validate_reference_routing())
    errors.extend(validate_current_runtime_lineage())
    errors.extend(validate_ci_release_gate())
    errors.extend(validate_change_impact_manifest())
    errors.extend(validate_domain_contract_entrypoints())
    errors.extend(validate_vlb_handoff_entrypoints())

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Repository validation passed for {len(skill_dirs)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
