#!/usr/bin/env python3
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parent


class MonitoringScripts(unittest.TestCase):
    def test_domain_pipeline_blocks_less_than_three_snapshots(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);source=tmp/"in.json";output=tmp/"out.json"
            source.write_text(json.dumps({"object_id":"A","snapshots":[{"object_id":"A","observed_at":"2026-01-01","display_condition":"public"}],"signals":[],"opportunity_window":{"deployment_days":5,"conservative_remaining_days":10}}),encoding="utf-8")
            subprocess.run(["python3",ROOT/"evaluate_competitive_decision.py","--input",source,"--output",output],check=True);d=json.loads(output.read_text());self.assertEqual(d["posture"],"Blocked");self.assertIn("trend_requires_three_snapshots",d["errors"])

    def test_domain_pipeline_keeps_proxy_warning_and_counterevidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);source=tmp/"in.json";output=tmp/"out.json";sn=[{"object_id":"A","observed_at":f"2026-01-0{i}","display_condition":"public"} for i in range(1,4)]
            source.write_text(json.dumps({"object_id":"A","snapshots":sn,"signals":[{"id":"ads","value":12,"baseline":2,"threshold":5,"consecutive_confirmations":2,"evidence_type":"public_proxy"}],"hypotheses":[{"id":"H1","supporting_signal_ids":["ads"],"counter_signal_ids":["stable-rank"],"independent_source_fingerprints":["f1"],"validation_due":"2026-02-01"}],"opportunity_window":{"deployment_days":5,"conservative_remaining_days":20}}),encoding="utf-8")
            subprocess.run(["python3",ROOT/"evaluate_competitive_decision.py","--input",source,"--output",output],check=True);d=json.loads(output.read_text());self.assertEqual(d["posture"],"Test");self.assertTrue(d["forbidden_claims"]);self.assertEqual(d["hypotheses"][0]["confidence"],"low")

    def test_single_snapshot_does_not_become_trend(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);source=tmp/"history.json";output=tmp/"alerts.json"
            source.write_text(json.dumps([{"product_id":"A","snapshot_at":"2026-01-01","price":100}]),encoding="utf-8")
            result=subprocess.run(["python3",ROOT/"detect_changes.py","--input",source,"--output",output],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)

    def test_snapshot_comparison_keeps_missing_and_zero_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);old=tmp/"old.json";new=tmp/"new.json";output=tmp/"out.json"
            old.write_text(json.dumps({"product_id":"A","price":10,"inventory":0}),encoding="utf-8")
            new.write_text(json.dumps({"product_id":"A","price":10}),encoding="utf-8")
            subprocess.run(["python3",ROOT/"compare_snapshots.py","--previous",old,"--current",new,"--output",output],check=True)
            self.assertIn("inventory",output.read_text(encoding="utf-8"))

    def test_metrics_reject_non_finite_proxy(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);source=tmp/"metrics.json";output=tmp/"out.json"
            source.write_text('{"model_version":"v","normalization_basis":"b","own":{"dimensions":{"product":NaN}}}',encoding="utf-8")
            result=subprocess.run(["python3",ROOT/"compute_competitive_metrics.py","--input",source,"--output",output],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)

    def test_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            rows = [{"product_id": "A", "snapshot_at": f"2026-01-{i:02d}", "price": 100, "rating": 4.5, "rank": 100} for i in range(1, 9)]
            rows.append({"product_id": "A", "snapshot_at": "2026-01-09", "price": 80, "rating": 4.0, "rank": 60})
            history, alerts, report = tmp / "history.json", tmp / "alerts.json", tmp / "report.md"
            history.write_text(json.dumps(rows), encoding="utf-8")
            subprocess.run(["python3", ROOT / "detect_changes.py", "--input", history, "--output", alerts], check=True)
            data = json.loads(alerts.read_text(encoding="utf-8"))
            self.assertEqual({x["field"] for x in data["alerts"]}, {"price", "rating", "rank"})
            subprocess.run(["python3", ROOT / "build_monitoring_report.py", "--alerts", alerts, "--output", report], check=True)
            self.assertIn("自动检测只证明", report.read_text(encoding="utf-8"))

    def test_competitive_metrics_and_proxy_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source, output = tmp / "metrics.json", tmp / "result.json"
            source.write_text(json.dumps({
                "model_version": "test-v1", "normalization_basis": "reviewed set",
                "own": {"dimensions": {"product": .5, "price": .5, "content": .5, "reputation": .5, "channel": .5}},
                "competitors": [{"id": "C1", "overlaps": {"market": 1, "category": 1, "customer": 1},
                    "dimensions": {"product": .8, "price": .6, "content": .7, "reputation": .8, "channel": .6}, "share_proxy": 70},
                    {"id": "C2", "overlaps": {"market": .5, "category": .5, "customer": .5},
                    "dimensions": {"product": .4, "price": .5, "content": .4, "reputation": .5, "channel": .4}, "share_proxy": 30}]}, ensure_ascii=False), encoding="utf-8")
            subprocess.run(["python3", ROOT / "compute_competitive_metrics.py", "--input", source, "--output", output], check=True)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["competitors"][0]["cri"], 1.0)
            self.assertIn("不等同真实市场份额", data["proxy_hhi_warning"])

    def test_learning_loop_keeps_denominators(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source, output = tmp / "learning.json", tmp / "result.json"
            source.write_text(json.dumps({"events": [{"review_result": "real"}, {"review_result": "noise"}],
                "hypotheses": [{"confidence": "high", "result": "validated"}],
                "actions": [{"result": "inconclusive"}]}), encoding="utf-8")
            subprocess.run(["python3", ROOT / "evaluate_learning_loop.py", "--input", source, "--output", output], check=True)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["event_validity"]["denominator"], 2)
            self.assertEqual(data["high_confidence_hit_rate"]["rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
