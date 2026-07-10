#!/usr/bin/env python3
"""Validate repository conventions that the generic Skill validator cannot enforce."""

from __future__ import annotations

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
    keys = {
        line.split(":", 1)[0].strip()
        for line in match.group(1).splitlines()
        if ":" in line and not line.startswith((" ", "\t"))
    }
    if keys != {"name", "description"}:
        errors.append(f"{skill_file}: frontmatter keys must be exactly name and description")
    if not VERSION_RE.search(text):
        errors.append(f"{skill_file}: missing runtime version declaration")

    for target in LINK_RE.findall(text):
        if "://" in target or target.startswith("#"):
            continue
        local_target = target.split("#", 1)[0]
        if local_target and not (skill_dir / local_target).exists():
            errors.append(f"{skill_file}: broken local link {target}")
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


def main() -> int:
    skill_dirs = sorted(path.parent for path in ROOT.glob("*/SKILL.md"))
    errors = [error for skill_dir in skill_dirs for error in validate_skill(skill_dir)]
    errors.extend(validate_video_weights())
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Repository validation passed for {len(skill_dirs)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
