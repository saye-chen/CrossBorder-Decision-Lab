#!/usr/bin/env python3
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parent


class MonitoringScripts(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
