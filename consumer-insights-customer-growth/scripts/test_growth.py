#!/usr/bin/env python3
import csv,json,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).parent

def run(script,*args): subprocess.run(["python3",ROOT/script,*map(str,args)],check=True)

class GrowthScripts(unittest.TestCase):
    def test_domain_decision_blocks_identity_and_consent(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);inp=td/"in.json";out=td/"out.json"
            inp.write_text(json.dumps({"object_id":"c1","as_of_time":"2026-01-01","purpose":"retention","identity":{"grain":"person","confidence":.4},"consent":{"purpose_allowed":False,"not_withdrawn":True,"not_unsubscribed":True,"retention_valid":True},"data_quality":{"events_reconciled":True,"revenue_reconciled":True,"no_future_leakage":True},"analysis_level":"descriptive","action":{"frequency_ok":True,"inventory_ok":True,"market_allowed":True,"fairness_ok":True,"sensitive_event_clear":True}}),encoding="utf-8")
            run("evaluate_growth_decision.py","--input",inp,"--output",out);d=json.loads(out.read_text());self.assertEqual(d["decision"],"Blocked");self.assertIn("consent_gate:purpose_allowed",d["errors"])

    def test_domain_decision_requires_causal_maturity(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);inp=td/"in.json";out=td/"out.json"
            inp.write_text(json.dumps({"object_id":"c1","as_of_time":"2026-01-01","purpose":"retention","identity":{"grain":"person","confidence":1},"consent":{"purpose_allowed":True,"not_withdrawn":True,"not_unsubscribed":True,"retention_valid":True},"data_quality":{"events_reconciled":True,"revenue_reconciled":True,"no_future_leakage":True},"analysis_level":"causal","experiment":{"randomization_valid":True,"exposure_reconciled":True,"outcome_mature":False,"interference_addressed":True,"treatment_n":100,"control_n":100,"treatment_outcome":20,"control_outcome":10},"action":{"frequency_ok":True,"inventory_ok":True,"market_allowed":True,"fairness_ok":True,"sensitive_event_clear":True}}),encoding="utf-8")
            run("evaluate_growth_decision.py","--input",inp,"--output",out);self.assertIn("experiment_gate:outcome_mature",json.loads(out.read_text())["errors"])

    def test_report_builder_is_explicit_about_no_contact(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); inp=td/"input.json"; out=td/"report.md"
            inp.write_text(json.dumps({"decision":"No contact","evidence_level":"descriptive","limitations":["no experiment"],"actions":[]}),encoding="utf-8")
            run("build_growth_report.py","--input",inp,"--output",out)
            text=out.read_text(encoding="utf-8")
            self.assertIn("不触达",text)
            self.assertNotIn("causal uplift validated",text.lower())

    def test_event_validator_rejects_missing_consent(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); source=td/"events.csv"; out=td/"out.json"
            fields=["event_id","event_time","ingest_time","customer_key","market","channel","event_type","consent_state","source"]
            with source.open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow({"event_id":"e1","event_time":"2026-01-01","ingest_time":"2026-01-01","customer_key":"c1","market":"US","channel":"email","event_type":"send","consent_state":"","source":"crm"})
            run("validate_customer_events.py","--input",source,"--output",out)
            self.assertFalse(json.loads(out.read_text())["valid"])

    def test_action_ranking_preserves_not_selected_reasons(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);inp=td/"in.json";out=td/"out.json"
            inp.write_text(json.dumps([{"customer_key":"c1","action":"email","uplift":.2,"contribution_margin":10,"contact_cost":0,"consent":False,"not_unsubscribed":True,"frequency_ok":True,"inventory_ok":True,"market_allowed":True}]),encoding="utf-8")
            run("rank_next_best_actions.py","--input",inp,"--output",out)
            data=json.loads(out.read_text());self.assertEqual(data["selected"],[]);self.assertIn("consent",data["not_selected"][0]["rejection_reasons"])

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

    def test_reconciliation_voc_lifecycle_uplift_and_governance(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); out=td/"out.json"
            ledger=td/"ledger.csv"
            with ledger.open("w",newline="",encoding="utf-8") as f:
                fields=["order_id","market","currency","captured_payment","recognized_discount","completed_refund","tax_excluded","cogs","reported_net_revenue"];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow({"order_id":"o1","market":"US","currency":"USD","captured_payment":100,"recognized_discount":10,"completed_refund":5,"tax_excluded":5,"cogs":30,"reported_net_revenue":80})
            run("reconcile_customer_revenue.py","--input",ledger,"--output",out);self.assertTrue(json.loads(out.read_text())["reconciled"])
            voc=td/"voc.csv"
            with voc.open("w",newline="",encoding="utf-8") as f:
                fields=["language","market","label_a","label_b","confidence"];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{"language":"en","market":"US","label_a":"fit","label_b":"fit","confidence":"high"},{"language":"en","market":"US","label_a":"size","label_b":"size","confidence":"high"}])
            run("audit_voc_labels.py","--input",voc,"--output",out);self.assertEqual(json.loads(out.read_text())["groups"][0]["agreement"],1)
            states=td/"states.csv"
            with states.open("w",newline="",encoding="utf-8") as f:
                fields=["customer_key","snapshot_at","state"];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{"customer_key":"c1","snapshot_at":"2026-01-01","state":"new"},{"customer_key":"c1","snapshot_at":"2026-02-01","state":"active"}])
            run("analyze_lifecycle_transitions.py","--input",states,"--output",out);self.assertEqual(json.loads(out.read_text())["transitions"][0]["probability"],1)
            uplift=td/"uplift.csv"
            with uplift.open("w",newline="",encoding="utf-8") as f:
                fields=["uplift_score","treatment","outcome"];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{"uplift_score":.9,"treatment":1,"outcome":1},{"uplift_score":.8,"treatment":0,"outcome":0},{"uplift_score":.2,"treatment":1,"outcome":0},{"uplift_score":.1,"treatment":0,"outcome":1}])
            run("evaluate_uplift_ranking.py","--input",uplift,"--output",out,"--bins",2);self.assertGreater(json.loads(out.read_text())["top_minus_bottom"],0)
            gov=td/"gov.csv"
            with gov.open("w",newline="",encoding="utf-8") as f:
                fields=["prediction","outcome","group","selected","period"];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{"prediction":.2,"outcome":0,"group":"A","selected":0,"period":"baseline"},{"prediction":.4,"outcome":1,"group":"A","selected":1,"period":"current"}])
            run("evaluate_growth_governance.py","--input",gov,"--output",out);self.assertEqual(json.loads(out.read_text())["n"],2)

if __name__=="__main__": unittest.main()
