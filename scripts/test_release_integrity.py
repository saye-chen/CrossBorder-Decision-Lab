#!/usr/bin/env python3
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("integrity", ROOT / "scripts/validate_release_integrity.py")
integrity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integrity)


class ReleaseIntegrityTests(unittest.TestCase):
    def test_static_release_contract_is_complete(self):
        self.assertEqual(integrity.validate(run_commands=False), [])
        self.assertGreaterEqual(len(integrity.command_paths()), 13)

    def test_exact_mutation_set_has_no_duplicate_escape_hatch(self):
        manifest = json.loads(integrity.MUTATIONS.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["mutations"]), len({x["id"] for x in manifest["mutations"]}))
        self.assertEqual({x["id"] for x in manifest["mutations"]}, integrity.EXPECTED_MUTATIONS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
