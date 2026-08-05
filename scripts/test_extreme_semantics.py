#!/usr/bin/env python3
import importlib.util,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]; s=importlib.util.spec_from_file_location("v",R/"scripts/validate_extreme_semantics.py"); v=importlib.util.module_from_spec(s); s.loader.exec_module(v)
class T(unittest.TestCase):
 def test_reports_are_semantically_distinct(self): self.assertEqual(v.validate(),[])
 def test_catalog_has_twelve_profiles(self): self.assertEqual(set(v.REQUIRED),{f"EC-{i:02d}" for i in range(1,13)})
if __name__=="__main__": unittest.main(verbosity=2)
