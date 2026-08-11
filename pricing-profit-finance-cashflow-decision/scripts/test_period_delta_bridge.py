#!/usr/bin/env python3
import copy, importlib.util, unittest
from pathlib import Path
P=Path(__file__).with_name("build_period_delta_bridge.py");S=importlib.util.spec_from_file_location("bridge",P);M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
def period(gross="100",op="20"):
    return {"gross_ordered_revenue":gross,"discounts":"5","pass_through_tax":"10","cancellations":"0","refunds":"5","other_reversals":"0","product_cogs":"30","fulfillment":"10","platform_payment_fees":"5","expected_returns":"2","variable_marketing":"8","variable_service":"2","avoidable_period_cost":"2","allocated_operating_expense":"1","recognized_net_revenue":str(int(gross)-20),"operating_profit":op}
def payload():
    evidence={"evidence_id":"E1","subject_id":"SKU1","subject_version":"v1","currency":"USD","tax_basis":"pass_through_excluded","quantity_unit":"piece","timezone":"America/Los_Angeles","status":"verified","observed_at":"2026-07-31T00:00:00Z","valid_until":"2026-08-28T00:00:00Z","fingerprint":"a"*64}
    return {"bridge_id":"B1","subject_id":"SKU1","subject_version":"v1","currency":"USD","tax_basis":"pass_through_excluded","quantity_unit":"piece","timezone":"America/Los_Angeles","baseline_window":{"start":"2026-06-01T00:00:00Z","end":"2026-07-01T00:00:00Z"},"comparison_window":{"start":"2026-07-01T00:00:00Z","end":"2026-07-31T00:00:00Z"},"baseline":period(),"comparison":period("120","40"),"evidence_refs":["E1"],"evidence_records":[evidence],"external_write":False}
class TestBridge(unittest.TestCase):
    def test_revenue_and_profit_delta_conserve(self):
        out=M.build(payload());self.assertEqual(out["status"],"validated");self.assertEqual(out["action_ceiling"],"reconciliation_only");self.assertEqual(out["recognized_net_revenue_delta"],"20");self.assertEqual(out["operating_profit_delta"],"20");self.assertEqual(out["owner"],"D06")
    def test_revenue_mismatch_blocks(self):
        x=payload();x["comparison"]["recognized_net_revenue"]="101";self.assertIn("REVENUE_NOT_CONSERVED:comparison",M.build(x)["blocking_errors"])
    def test_profit_mismatch_blocks(self):
        x=payload();x["comparison"]["operating_profit"]="41";self.assertIn("PROFIT_NOT_CONSERVED:comparison",M.build(x)["blocking_errors"])
    def test_float_is_rejected(self):
        x=payload();x["baseline"]["gross_ordered_revenue"]=100.0
        with self.assertRaises(M.BridgeError):M.build(x)
    def test_external_write_is_rejected(self):
        x=payload();x["external_write"]=True
        with self.assertRaisesRegex(M.BridgeError,"EXTERNAL_WRITE"):M.build(x)
    def test_negative_reversal_is_rejected(self):
        x=payload();x["baseline"]["discounts"]="-1"
        with self.assertRaises(M.BridgeError):M.build(x)
    def test_negative_cost_is_rejected(self):
        x=payload();x["baseline"]["product_cogs"]="-1"
        with self.assertRaises(M.BridgeError):M.build(x)
    def test_schema_rejects_illegal_metadata_and_extra_fields(self):
        for field,value in (("currency","NOT_A_CURRENCY"),("timezone","NOT_A_TIMEZONE")):
            x=payload();x[field]=value
            with self.subTest(field=field),self.assertRaises(M.BridgeError):M.build(x)
        x=payload();x["unknown"]="forbidden"
        with self.assertRaisesRegex(M.BridgeError,"schema"):M.build(x)
    def test_windows_must_be_ordered_nonoverlapping_and_equal_duration(self):
        x=payload();x["comparison_window"]["start"]="2026-06-15T00:00:00Z"
        with self.assertRaisesRegex(M.BridgeError,"overlapping"):M.build(x)
        x=payload();x["comparison_window"]["end"]="2026-08-01T00:00:00Z"
        with self.assertRaisesRegex(M.BridgeError,"NOT_COMPARABLE"):M.build(x)
    def test_evidence_must_be_current_complete_and_scope_bound(self):
        x=payload();x["evidence_records"][0]["status"]="expired"
        with self.assertRaisesRegex(M.BridgeError,"NOT_CURRENT"):M.build(x)
        x=payload();x["evidence_records"][0]["currency"]="EUR"
        with self.assertRaisesRegex(M.BridgeError,"SCOPE_MISMATCH"):M.build(x)
        x=payload();x["evidence_refs"]=[]
        with self.assertRaisesRegex(M.BridgeError,"schema"):M.build(x)
    def test_deterministic_hash(self):self.assertEqual(M.build(payload())["result_hash"],M.build(payload())["result_hash"])
if __name__=="__main__":unittest.main(verbosity=2)
