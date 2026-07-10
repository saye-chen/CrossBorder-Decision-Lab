#!/usr/bin/env python3
"""Regression tests for video-link-breakdown preparation invariants."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("prepare_video_link.py")
SPEC = importlib.util.spec_from_file_location("prepare_video_link", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PreparationTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_slugify_is_bounded_and_safe(self) -> None:
        slug = MODULE.slugify("https://example.com/a video?x=1")
        self.assertEqual(slug, "example-com-a-video-x-1")
        self.assertLessEqual(len(slug), 60)

    def test_rejects_non_http_url(self) -> None:
        result = self.run_script("not-a-url", "--skip-download")
        self.assertEqual(result.returncode, 2)
        self.assertIn("url must start", result.stderr)

    def test_rejects_invalid_sample_count(self) -> None:
        result = self.run_script("https://example.com/video", "--samples", "1", "--skip-download")
        self.assertEqual(result.returncode, 2)
        self.assertIn("between 2 and 120", result.stderr)

    def test_missing_package_does_not_install_by_default(self) -> None:
        self.assertFalse(MODULE.ensure_package("package_that_does_not_exist_12345"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
