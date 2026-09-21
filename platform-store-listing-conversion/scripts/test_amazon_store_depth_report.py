#!/usr/bin/env python3
"""Ensure the Amazon report golden remains operationally rich."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "evaluations/output-goldens/amazon-store-portfolio-architecture.md"


class AmazonStoreDepthReport(unittest.TestCase):
    def test_report_has_twenty_required_sections_and_operational_boundaries(self):
        text = REPORT.read_text(encoding="utf-8")
        for number in range(1, 21):
            self.assertIn(f"## {number}.", text)
        for marker in (
            "store_profile_id", "Seller ID", "法定主体", "Marketplace site", "FBA/MFN/Vendor",
            "Brand Store", "Offer", "Ads Profile", "Gates", "替代解释", "反事实", "计算",
            "Issue Cards", "实验", "停止/回滚", "跨域交接", "外部写入为 `false`",
            "每日", "运营板", "FBA/MFN/Vendor", "指标", "工作流",
        ):
            self.assertIn(marker, text, marker)


if __name__ == "__main__":
    unittest.main(verbosity=2)
