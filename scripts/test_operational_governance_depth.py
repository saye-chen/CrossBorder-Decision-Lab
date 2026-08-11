#!/usr/bin/env python3
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("depth", ROOT / "scripts/validate_operational_governance_depth.py")
depth = importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(depth)


class OperationalGovernanceDepthTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connector = json.loads(depth.CONNECTOR.read_text())
        cls.knowledge = json.loads(depth.KNOWLEDGE.read_text())

    def test_contracts_pass(self):
        self.assertEqual(depth.validate(copy.deepcopy(self.connector), copy.deepcopy(self.knowledge)), [])

    def test_connector_activation_without_independent_review_fails(self):
        connector = copy.deepcopy(self.connector)
        row = next(x for x in connector["transitions"] if x["from"] == "controlled_pilot" and x["to"] == "active")
        row["requires"].remove("independent_review")
        self.assertIn("connector activation lacks independent review", depth.validate(connector, copy.deepcopy(self.knowledge)))

    def test_platform_manual_expiry_override_fails(self):
        knowledge = copy.deepcopy(self.knowledge)
        knowledge["prohibited"].remove("manual_expiry_override")
        self.assertIn("knowledge prohibited uses incomplete", depth.validate(copy.deepcopy(self.connector), knowledge))

    def test_reactivation_without_reconciliation_fails(self):
        connector = copy.deepcopy(self.connector)
        row = next(x for x in connector["transitions"] if x["from"] == "suspended" and x["to"] == "controlled_pilot")
        row["requires"].remove("reconciliation_pass")
        self.assertIn("connector recovery lacks reconciliation", depth.validate(connector, copy.deepcopy(self.knowledge)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
