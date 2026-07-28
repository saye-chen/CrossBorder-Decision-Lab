#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("wp2",ROOT/"scripts/validate_wp2_contracts.py")
WP2=importlib.util.module_from_spec(SPEC);assert SPEC and SPEC.loader;SPEC.loader.exec_module(WP2)

class WP2Contracts(unittest.TestCase):
    def test_canonical_object_and_version(self):
        payload={"object_id":"prod-1","object_type":"product","object_version":"v1","country":"US","platform":"Amazon","valid_from":"2026-07-28T00:00:00Z","as_of_time":"2026-07-28T00:00:00Z","recorded_at":"2026-07-28T00:01:00Z","attributes_hash":"a"*64}
        self.assertEqual(WP2.validate_file("canonical-product-object.schema.json",payload),[])
        payload["country"]="USA"
        self.assertTrue(WP2.validate_file("canonical-product-object.schema.json",payload))

    def test_plc_namespace_is_not_maturity(self):
        payload={"object_id":"prod-1","object_version":"v1","product_lifecycle_stage":"PLC4","decision_state":"proposed","maturity_l1":"passed","maturity_l2":"passed","maturity_l3":"not_passed","maturity_l4":"not_passed","external_write":False}
        self.assertEqual(WP2.validate_file("product-lifecycle-state.schema.json",payload),[])
        payload["product_lifecycle_stage"]="L4"
        self.assertTrue(WP2.validate_file("product-lifecycle-state.schema.json",payload))

    def test_external_write_fails(self):
        payload={"object_id":"prod-1","object_version":"v1","product_lifecycle_stage":"PLC3","decision_state":"validated","maturity_l1":"passed","maturity_l2":"passed","maturity_l3":"not_passed","maturity_l4":"not_passed","external_write":True}
        self.assertTrue(WP2.validate_file("product-lifecycle-state.schema.json",payload))

if __name__=="__main__": unittest.main(verbosity=2)
