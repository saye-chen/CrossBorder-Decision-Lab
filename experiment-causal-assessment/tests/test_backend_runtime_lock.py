import hashlib
import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_backend_runtime import verify


class BackendRuntimeLockTests(unittest.TestCase):
    def test_runtime_lock_is_complete_and_integrity_bound(self):
        lock = json.loads((ROOT / "backends/runtime-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["python"]["version"], "3.12.13")
        self.assertEqual(lock["r"]["version"], "4.5.3")
        self.assertEqual(len(lock["adapter_integrity"]["adapters"]), 12)
        for relative, expected in lock["adapter_integrity"]["adapters"].items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected)

    def test_unbound_probe_is_non_mutating_and_non_promotional(self):
        report = verify()
        self.assertEqual(report["checks"]["adapter_integrity"]["status"], "pass")
        self.assertIn(report["checks"]["python"]["status"], {"pass", "runtime_not_bound"})
        self.assertIn(report["checks"]["r"]["status"], {"pass", "runtime_not_bound"})
        self.assertFalse(report["registry_promotion_authorized"])


if __name__ == "__main__":
    unittest.main()
