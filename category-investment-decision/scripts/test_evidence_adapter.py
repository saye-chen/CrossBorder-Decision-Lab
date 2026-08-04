#!/usr/bin/env python3
import unittest
from datetime import date
from evidence_adapter import AdapterError, normalize

class AdapterTests(unittest.TestCase):
    def contract(self): return {"source":"fixture","source_family_id":"F1","raw_evidence_id":"E1","observed_at":"2026-08-01","max_age_days":10,"fields":{"growth":{"source_field":"growth_pct","kind":"ratio","scale":"0-100","required":True}}}
    def test_ratio_lineage_and_hashes(self):
        out=normalize({"growth_pct":25},self.contract(),as_of=date(2026,8,4)); self.assertEqual(out["normalized_fields"]["growth"],"0.25"); self.assertEqual(out["source_family_id"],"F1"); self.assertTrue(out["output_hash"].startswith("sha256:"))
    def test_missing_error_stale_and_bad_scale_fail_closed(self):
        for raw,contract,day in [({},self.contract(),date(2026,8,4)),({"error":"timeout"},self.contract(),date(2026,8,4)),({"growth_pct":25},self.contract(),date(2026,9,1))]:
            with self.assertRaises(AdapterError): normalize(raw,contract,as_of=day)
        c=self.contract(); c["fields"]["growth"]["scale"]="ambiguous"
        with self.assertRaises(AdapterError): normalize({"growth_pct":25},c,as_of=date(2026,8,4))
if __name__=="__main__": unittest.main(verbosity=2)
