#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("local_validator",HERE/"validate_adapter.py")
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)
class ConsumerOwnedAdapterTest(unittest.TestCase):
 def test_acceptance_and_negative_paths(self):self.assertEqual(MODULE.validate(),[])
if __name__=="__main__":unittest.main(verbosity=2)
