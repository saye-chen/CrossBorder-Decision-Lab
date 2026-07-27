#!/usr/bin/env python3
"""Portable QoderWork installation tests for CI and local release gates."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate_qoderwork_skill_installation.py"
SPEC = importlib.util.spec_from_file_location("qoderwork_installation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class QoderWorkInstallation(unittest.TestCase):
    def test_install_is_complete_idempotent_and_space_safe(self):
        with tempfile.TemporaryDirectory(prefix="qoder install roots ") as temp:
            roots = (Path(temp) / "root one", Path(temp) / "root two")
            self.assertEqual(MODULE.install(ROOT, roots), [])
            self.assertEqual(MODULE.install(ROOT, roots), [])
            self.assertEqual(MODULE.validate(ROOT, roots), [])
            for install_root in roots:
                self.assertEqual(
                    {path.name for path in install_root.iterdir()},
                    set(MODULE.discover_skills(ROOT)),
                )

    def test_missing_wrong_and_broken_links_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            install_root = Path(temp) / "skills"
            self.assertEqual(MODULE.install(ROOT, (install_root,)), [])
            skill = MODULE.discover_skills(ROOT)[0]
            link = install_root / skill
            link.unlink()
            self.assertTrue(any("missing symlink" in item for item in MODULE.validate(ROOT, (install_root,))))
            link.symlink_to(Path(temp) / "missing-target", target_is_directory=True)
            self.assertTrue(any("points to" in item for item in MODULE.validate(ROOT, (install_root,))))

    def test_non_symlink_conflict_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            install_root = Path(temp) / "skills"
            install_root.mkdir()
            skill = MODULE.discover_skills(ROOT)[0]
            conflict = install_root / skill
            conflict.mkdir()
            errors = MODULE.install(ROOT, (install_root,))
            self.assertTrue(any("conflicting non-symlink object" in item for item in errors))
            self.assertTrue(conflict.is_dir())
            self.assertFalse(conflict.is_symlink())


if __name__ == "__main__":
    unittest.main(verbosity=2)
