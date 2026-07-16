#!/usr/bin/env python3
import csv,json,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).parent
def run(name,input_data,suffix="json"):
    with tempfile.TemporaryDirectory() as td:
        td=Path(td);inp=td/f"in.{suffix}";out=td/"out.json"
        if suffix=="json":inp.write_text(json.dumps(input_data),encoding="utf-8")
        else:
            with inp.open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=input_data[0]);w.writeheader();w.writerows(input_data)
        r=subprocess.run(["python3",str(ROOT/name),"--input",str(inp),"--output",str(out)],capture_output=True,text=True)
        if r.returncode: raise AssertionError(r.stderr)
        return json.loads(out.read_text())
class Models(unittest.TestCase):
    def test_cpc_and_break_even(self):
        d=run("ad_economics.py",{"mode":"cpc","revenue":1000,"pre_ad_cm_rate":.3,"clicks":100,"cpc":2,"cvr":.1,"aov":50,"ctr":.02})
        self.assertEqual(d["ad_contribution_profit"],100);self.assertEqual(d["break_even_platform_roas"],3.333333);self.assertEqual(d["break_even_cpc"],1.5)
    def test_all_cost_modes(self):
        cases=[{"mode":"cpm","impressions":10000,"cpm":10},{"mode":"cpv","views":1000,"cpv":.1},{"mode":"cpa","actions":10,"cpa":10},{"mode":"cps","cps_rate":.1},{"mode":"fixed","fixed_cost":100},{"mode":"mixed","fixed_cost":20,"variable_spend":30,"cps_rate":.05}]
        for c in cases:
            with self.subTest(c["mode"]):self.assertIn("status",run("ad_economics.py",{"revenue":1000,"pre_ad_cm_rate":.3,**c}))
    def test_mature_profit(self):
        rows=[{"gross_revenue":100,"discount":5,"refund":10,"chargeback":0,"tax":5,"cogs":30,"fulfillment":10,"platform_fee":5,"service_cost":2,"ad_spend":20}]
        d=run("mature_profit.py",rows,"csv");self.assertEqual(d["mature_net_revenue"],80);self.assertEqual(d["ad_contribution_profit"],13)
    def test_marginal_negative(self):
        d=run("marginal_analysis.py",[{"spend":100,"mature_revenue":400,"contribution_profit":50},{"spend":200,"mature_revenue":500,"contribution_profit":40}]);self.assertLess(d[1]["marginal_contribution"],0)
    def test_incrementality(self):
        d=run("evaluate_incrementality.py",{"treatment":{"n":100,"value":1200,"variance":4},"control":{"n":100,"value":1000,"variance":4},"incremental_spend":50,"contribution_margin_rate":.5});self.assertEqual(d["decision"],"Go")
    def test_budget_rejects_negative_margin(self):
        d=run("allocate_budget.py",{"budget":300,"candidates":[{"id":"a","step":100,"max_budget":200,"marginal_contribution_per_currency":.2},{"id":"b","step":100,"max_budget":200,"marginal_contribution_per_currency":-.1}]});self.assertEqual(d["allocations"][0]["allocated"],200);self.assertEqual(d["allocations"][1]["allocated"],0)
if __name__=="__main__":unittest.main(verbosity=2)
