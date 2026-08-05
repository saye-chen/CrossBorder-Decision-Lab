#!/usr/bin/env python3
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validator", ROOT / "scripts/validate_professional_evaluation_registry.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ProfessionalEvaluationRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(validator.REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.index = json.loads(validator.INDEX_PATH.read_text(encoding="utf-8"))

    def test_current_evidence_passes(self):
        self.assertEqual(validator.validate(self.registry, self.index), [])

    def test_missing_domain_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["domains"].pop()
        self.assertTrue(validator.validate(registry, self.index))

    def test_source_fingerprint_tamper_is_rejected(self):
        index = copy.deepcopy(self.index)
        index["cases"][0]["source_hash"] = "0" * 64
        self.assertTrue(any("fingerprint" in x for x in validator.validate(self.registry, index)))

    def test_manual_l4_escalation_is_rejected(self):
        index = copy.deepcopy(self.index)
        index["cases"][0]["sovereignty"]["forbidden_uses"].remove("l4_claim")
        self.assertTrue(any("L4" in x for x in validator.validate(self.registry, index)))

    def test_removed_counterevidence_is_rejected(self):
        index = copy.deepcopy(self.index)
        index["cases"][0]["counterevidence"] = []
        self.assertTrue(any("counterevidence" in x for x in validator.validate(self.registry, index)))

    def test_action_detached_from_root_cause_is_rejected(self):
        index = copy.deepcopy(self.index)
        index["cases"][0]["actions"][0]["root_cause_ref"] = "RC-UNRELATED"
        self.assertTrue(any("linked to root cause" in x for x in validator.validate(self.registry, index)))

    def test_claim_with_unknown_evidence_is_rejected(self):
        index = copy.deepcopy(self.index)
        index["cases"][0]["claims"][0]["evidence_refs"] = ["E-FABRICATED"]
        self.assertTrue(any("claim references unknown evidence" in x for x in validator.validate(self.registry, index)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
