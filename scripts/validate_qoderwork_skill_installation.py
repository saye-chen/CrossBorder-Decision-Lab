#!/usr/bin/env python3
"""Install or validate repository skills in one or more QoderWork roots."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INSTALL_ROOTS = (
    Path.home() / ".qoderwork/skills",
    Path.home() / ".qoderworkcn/skills",
)


def discover_skills(repository_root: Path) -> list[str]:
    return sorted(path.parent.name for path in repository_root.glob("*/SKILL.md"))


def install(repository_root: Path, install_roots: Iterable[Path]) -> list[str]:
    """Create missing links without replacing conflicting filesystem objects."""
    errors: list[str] = []
    skills = discover_skills(repository_root)
    for install_root in install_roots:
        install_root.mkdir(parents=True, exist_ok=True)
        for skill in skills:
            link = install_root / skill
            expected = repository_root / skill
            if link.is_symlink():
                if link.resolve() != expected.resolve():
                    errors.append(f"{link}: wrong symlink target {link.resolve()}")
                continue
            if link.exists():
                errors.append(f"{link}: conflicting non-symlink object")
                continue
            link.symlink_to(expected, target_is_directory=True)
    return errors


def validate(repository_root: Path, install_roots: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    skills = discover_skills(repository_root)
    if not skills:
        return [f"{repository_root}: no discoverable skills"]
    for install_root in install_roots:
        for skill in skills:
            link = install_root / skill
            expected = repository_root / skill
            if not link.is_symlink():
                errors.append(f"{link}: missing symlink")
                continue
            if link.resolve() != expected.resolve():
                errors.append(f"{link}: points to {link.resolve()}, expected {expected.resolve()}")
                continue
            if not (link / "SKILL.md").is_file():
                errors.append(f"{link}: target has no SKILL.md")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--install-root", action="append", type=Path, dest="install_roots")
    parser.add_argument("--create-missing", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repository_root = args.repository_root.resolve()
    install_roots = tuple(args.install_roots or DEFAULT_INSTALL_ROOTS)
    errors = install(repository_root, install_roots) if args.create_missing else []
    errors.extend(validate(repository_root, install_roots))
    if errors:
        print("\n".join(f"ERROR: {item}" for item in dict.fromkeys(errors)))
        return 1
    print(
        f"QoderWork installation passed for {len(discover_skills(repository_root))} "
        f"skills across {len(install_roots)} roots."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
