#!/usr/bin/env python3
import importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; spec=importlib.util.spec_from_file_location("release",ROOT/"scripts/validate_release_candidate.py"); release=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(release)
class ReleaseCandidateTest(unittest.TestCase):
    def test_internal_release_candidate(self): self.assertEqual(release.validate(),[])
if __name__=="__main__": unittest.main(verbosity=2)
