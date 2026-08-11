#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("lifd_ecae_adapter_validator", HERE / "validate_adapter.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class LIFDECAEConsumerAdapterTests(unittest.TestCase):
    def test_consumer_owned_contract_and_pending_owner_boundary(self):
        self.assertEqual(MODULE.validate(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
