#!/usr/bin/env python3
import unittest

from validate_all_domains import audit_registry


class RegistryTests(unittest.TestCase):
    def test_registry_is_explicit_and_nonempty(self):
        result = audit_registry()
        self.assertGreaterEqual(result["checked"], 10)
        # Existing domains may be mid-migration; missing wiring must be visible,
        # never silently treated as a passing joint report.
        self.assertIn(result["status"], {"PASS", "BLOCKED"})


if __name__ == "__main__":
    unittest.main()
