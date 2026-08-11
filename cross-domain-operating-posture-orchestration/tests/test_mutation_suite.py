#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from run_mutation_suite import run
class TestMutations(unittest.TestCase):
 def test_all_sixteen_mutations_are_executed_and_killed(self):
  result=run();self.assertEqual(len(result),16);self.assertTrue(all(result.values()),result)
if __name__=="__main__":unittest.main(verbosity=2)
