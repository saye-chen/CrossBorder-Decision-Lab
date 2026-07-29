#!/usr/bin/env python3
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "product-innovation-product-management/SKILL.md"


class EntryRoutingTest(unittest.TestCase):
    def test_routes_product_work_and_escalates_other_sovereignties(self):
        text = SKILL.read_text(encoding="utf-8")
        for owned in ("MVP范围", "规格、容差", "变体架构", "产品根因假设", "路线图"):
            self.assertIn(owned, text)
        for owner in ("CIDM", "PPFC", "D04", "D05", "LIFD", "PLCO"):
            self.assertIn(owner, text)

    def test_unavailable_d04_d05_fail_closed(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("D04未建成时`blocked`", text)
        self.assertIn("D05未建成时`blocked`", text)
        self.assertIn("不以SKILL.md行数作为成熟度证据", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
