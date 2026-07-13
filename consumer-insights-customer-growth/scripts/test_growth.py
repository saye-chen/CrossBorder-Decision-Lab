#!/usr/bin/env python3
import csv,json,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).parent

def run(script,*args): subprocess.run(["python3",ROOT/script,*map(str,args)],check=True)

class GrowthScripts(unittest.TestCase):
    def test_event_validation_and_rfm(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); events=td/"events.csv"; out=td/"out.json"
            fields=["event_id","event_time","ingest_time","customer_key","market","channel","event_type","consent_state","source"]
            with events.open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerow(dict(zip(fields,["e1","2026-01-01T00:00:00","2026-01-01T01:00:00","c1","US","web","purchase","granted","shop"])))
            run("validate_customer_events.py","--input",events,"--output",out); self.assertTrue(json.loads(out.read_text())["valid"])
            orders=td/"orders.csv"
            with orders.open("w",newline="",encoding="utf-8") as f:
                fields=["customer_key","order_id","order_time","contribution_margin","status"]; w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerow({"customer_key":"c1","order_id":"o1","order_time":"2026-01-01T00:00:00","contribution_margin":"20","status":"completed"})
            run("build_rfm_segments.py","--input",orders,"--as-of","2026-01-20","--output",out); self.assertEqual(json.loads(out.read_text())[0]["segment"],"new")

    def test_cohort_clv_experiment_and_actions(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); orders=td/"orders.csv"; out=td/"out.json"
            with orders.open("w",newline="",encoding="utf-8") as f:
                fields=["customer_key","order_time"]; w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows([{"customer_key":"c1","order_time":"2026-01-01T00:00:00"},{"customer_key":"c1","order_time":"2026-02-01T00:00:00"}])
            run("analyze_cohort_retention.py","--input",orders,"--as-of","2026-02-28","--output",out); self.assertEqual(json.loads(out.read_text())[0]["cells"][1]["retention"],1)
            inp=td/"in.json"; inp.write_text(json.dumps({"expected_contribution_margins":[60,60],"survival":[1,.5],"cac":50}),encoding="utf-8")
            run("calculate_clv.py","--input",inp,"--output",out); self.assertEqual(json.loads(out.read_text())["payback_period"],1)
            inp.write_text(json.dumps({"treatment":{"successes":150,"n":1000},"control":{"successes":100,"n":1000},"contribution_margin_per_incremental_success":20}),encoding="utf-8")
            run("evaluate_growth_experiment.py","--input",inp,"--output",out); self.assertEqual(json.loads(out.read_text())["decision"],"Go")
            inp.write_text(json.dumps([{"customer_key":"c1","action":"email","uplift":.1,"contribution_margin":100,"contact_cost":1,"consent":True,"not_unsubscribed":True,"frequency_ok":True,"inventory_ok":True,"market_allowed":True},{"customer_key":"c2","action":"coupon","uplift":.01,"contribution_margin":10,"incentive_cost":5,"consent":True,"not_unsubscribed":True,"frequency_ok":True,"inventory_ok":True,"market_allowed":True}]),encoding="utf-8")
            run("rank_next_best_actions.py","--input",inp,"--output",out); d=json.loads(out.read_text()); self.assertEqual(d["selected"][0]["customer_key"],"c1"); self.assertIn("non_positive_niv",d["not_selected"][0]["rejection_reasons"])

if __name__=="__main__": unittest.main()
