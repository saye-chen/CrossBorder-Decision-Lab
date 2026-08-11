#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from run_behavior_mutations import run
class TestBehaviorMutations(unittest.TestCase):
 def test_all_sixteen_behavior_replacements_make_bound_tests_fail(self):
  result=run();self.assertEqual(len(result),16);self.assertTrue(all(result.values()),result)
if __name__=="__main__":unittest.main(verbosity=2)
