#!/usr/bin/env python3
"""Deterministically profile and aggregate a coded VOC dataset for investment research."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV, JSON array, or JSONL input")
    parser.add_argument("--output", type=Path, help="Write JSON here instead of stdout")
    parser.add_argument("--pretty", action="store_true", help="Indent JSON output")
    return parser.parse_args()


def load_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    if suffix == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, list) or not all(isinstance(x, dict) for x in value):
            raise ValueError("JSON input must be an array of objects")
        return value
    if suffix in {".jsonl", ".ndjson"}:
        records = []
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"JSONL line {line_number} must be an object")
            records.append(value)
        return records
    raise ValueError("Input must use .csv, .json, .jsonl, or .ndjson")


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


def parse_themes(value: Any) -> list[str]:
    if isinstance(value, list):
        raw = value
    elif value is None:
        raw = []
    else:
        raw = re.split(r"[|;,]", str(value))
    return sorted({str(item).strip() for item in raw if str(item).strip()})


def parse_rating(value: Any) -> str | None:
    if value in (None, ""):
        return None
    try:
        rating = float(value)
    except (TypeError, ValueError):
        return "invalid"
    if not 0 <= rating <= 5:
        return "invalid"
    return f"{rating:g}"


def analyze(records: list[dict[str, Any]]) -> dict[str, Any]:
    source_counts: Counter[str] = Counter()
    competitor_counts: Counter[str] = Counter()
    sentiment_counts: Counter[str] = Counter()
    rating_counts: Counter[str] = Counter()
    theme_counts: Counter[str] = Counter()
    theme_sources: dict[str, set[str]] = {}
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    missing_text = 0

    for record in records:
        text = normalize_text(record.get("text"))
        if not text:
            missing_text += 1
            continue
        if text in seen:
            continue
        seen.add(text)
        unique.append(record)

        source = str(record.get("source") or "unknown").strip()
        competitor = str(record.get("competitor") or "unknown").strip()
        sentiment = str(record.get("sentiment") or "uncoded").strip().lower()
        source_counts[source] += 1
        competitor_counts[competitor] += 1
        sentiment_counts[sentiment] += 1

        rating = parse_rating(record.get("rating"))
        if rating is not None:
            rating_counts[rating] += 1

        for theme in parse_themes(record.get("themes")):
            theme_counts[theme] += 1
            theme_sources.setdefault(theme, set()).add(source)

    unique_count = len(unique)
    coded_count = sum(1 for record in unique if parse_themes(record.get("themes")))
    source_diversity = len([key for key in source_counts if key != "unknown"])
    warnings = []
    if unique_count < 50:
        warnings.append("Fewer than 50 unique texts: treat findings as qualitative and do not generalize sample percentages.")
    if source_diversity < 2:
        warnings.append("Fewer than two named sources: cross-source validation is unavailable.")
    if unique_count and coded_count < unique_count:
        warnings.append("Some unique texts have no theme codes; theme counts cover only coded records.")
    if rating_counts.get("invalid"):
        warnings.append("Invalid ratings were retained as a separate count.")

    themes = [
        {"theme": theme, "records": count, "sources": sorted(theme_sources[theme])}
        for theme, count in sorted(theme_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    return {
        "records": {
            "raw": len(records),
            "unique_with_text": unique_count,
            "duplicates_or_reposts": len(records) - missing_text - unique_count,
            "missing_text": missing_text,
            "theme_coded": coded_count,
        },
        "distributions": {
            "sources": dict(source_counts.most_common()),
            "competitors": dict(competitor_counts.most_common()),
            "sentiment": dict(sentiment_counts.most_common()),
            "ratings": dict(sorted(rating_counts.items())),
        },
        "themes": themes,
        "warnings": warnings,
    }


def main() -> int:
    args = parse_args()
    try:
        result = analyze(load_records(args.input))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
