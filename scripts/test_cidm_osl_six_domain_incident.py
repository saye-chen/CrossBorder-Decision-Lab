#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MODDIR = ROOT / "category-investment-decision/scripts"; sys.path.insert(0, str(MODDIR))
spec = importlib.util.spec_from_file_location("incident", MODDIR / "validate_osl_six_domain_incident.py")
incident = importlib.util.module_from_spec(spec); spec.loader.exec_module(incident)
FIXTURE = ROOT / "category-investment-decision/evaluations/osl-six-domain-incident.json"

class TestSixDomainIncident(unittest.TestCase):
    def setUp(self): self.data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    def test_full_chain_passes(self): self.assertEqual(incident.validate(self.data), [])
    def test_every_domain_is_required(self):
        for name in incident.EXPECTED:
            case = copy.deepcopy(self.data); case["domains"] = [d for d in case["domains"] if d["domain"] != name]
            with self.subTest(name=name): self.assertIn("six_domain_set_invalid", incident.validate(case))
    def test_every_depth_field_is_required(self):
        for field in incident.DEPTH:
            case = copy.deepcopy(self.data); case["domains"][0][field] = ""
            with self.subTest(field=field): self.assertIn("shallow_domain_contract:CIM", incident.validate(case))
    def test_root_lineage_and_supersession_are_required(self):
        case = copy.deepcopy(self.data); case["lineage_edges"] = []
        self.assertIn("root_lineage_incomplete", incident.validate(case))
        case = copy.deepcopy(self.data); case["recovery"]["new_effective_decision_id"] = "CIDM-D1"
        self.assertIn("decision_supersession_invalid", incident.validate(case))
    def test_auxiliary_domain_cannot_take_investment_authority(self):
        case = copy.deepcopy(self.data); case["domains"][0]["allowed_use"] = "investment authorization"
        self.assertIn("authority_violation:CIM", incident.validate(case))

if __name__ == "__main__": unittest.main()
