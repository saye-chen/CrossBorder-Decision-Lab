#!/usr/bin/env python3
import importlib.util,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=importlib.util.spec_from_file_location("v",R/"scripts/validate_domain_professional_evaluations.py");v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
class T(unittest.TestCase):
 def test_legacy_domains_have_self_contained_professional_evaluations(self):
  for skill in v.b.P:self.assertEqual(v.validate(skill),[],skill)
if __name__=="__main__":unittest.main(verbosity=2)
