#!/usr/bin/env python3
"""Deterministic weighted video content scoring calculator.

Reads 7 dimension scores (1-10) and a video type, applies the weight table
from scoring-model.md, and outputs the weighted total score + confidence.

Usage:
    python3 score_video.py --type 带货 \
        --hook 8 --rhythm 7 --density 6 --persuasion 8 \
        --originality 7 --replication 9 --conversion 5

    python3 score_video.py --type 电商成交 \
        --hook 7 --rhythm 6 --density 5 --persuasion 8 \
        --originality 6 --replication 7 --conversion 8 \
        --product-match 9

    # JSON input
    python3 score_video.py --json scores.json

    # With confidence and batch break-even
    python3 score_video.py --type 带货 \
        --hook 8 --rhythm 7 --density 6 --persuasion 8 \
        --originality 7 --replication 9 --conversion 5 \
        --confidence high
"""

import argparse
import json
import sys

# Weight table from scoring-model.md
# Each column sums to 100.
WEIGHT_TABLE = {
    "带货": {
        "hook": 20,
        "rhythm": 15,
        "density": 10,
        "persuasion": 25,
        "originality": 10,
        "replication": 15,
        "conversion": 5,
    },
    "知识": {
        "hook": 15,
        "rhythm": 15,
        "density": 25,
        "persuasion": 20,
        "originality": 15,
        "replication": 5,
        "conversion": 5,
    },
    "情绪": {
        "hook": 20,
        "rhythm": 20,
        "density": 20,
        "persuasion": 15,
        "originality": 15,
        "replication": 5,
        "conversion": 5,
    },
    "娱乐": {
        "hook": 25,
        "rhythm": 20,
        "density": 15,
        "persuasion": 5,
        "originality": 20,
        "replication": 10,
        "conversion": 5,
    },
    "人设": {
        "hook": 15,
        "rhythm": 15,
        "density": 10,
        "persuasion": 15,
        "originality": 20,
        "replication": 15,
        "conversion": 10,
    },
    "电商成交": {
        "hook": 15,
        "rhythm": 10,
        "density": 10,
        "persuasion": 25,
        "originality": 5,
        "replication": 10,
        "conversion": 20,
        "product_match": 5,
    },
}

DIMENSION_NAMES = {
    "hook": "Hook",
    "rhythm": "节奏",
    "density": "信息/情绪密度",
    "persuasion": "说服力/可信度",
    "originality": "原创与差异",
    "replication": "复刻价值",
    "conversion": "转化/留存设计",
    "product_match": "产品-视频匹配",
}

VALID_TYPES = list(WEIGHT_TABLE.keys())
VALID_CONFIDENCE = ("high", "medium", "low")


def build_parser():
    p = argparse.ArgumentParser(
        description="Calculate weighted video content score from 7-dimension ratings."
    )
    p.add_argument(
        "--type",
        choices=VALID_TYPES,
        help="Video type (determines weight column). Required unless --json provides it.",
    )
    p.add_argument("--hook", type=float, help="Hook score (1-10)")
    p.add_argument("--rhythm", type=float, help="节奏 score (1-10)")
    p.add_argument("--density", type=float, help="信息/情绪密度 score (1-10)")
    p.add_argument("--persuasion", type=float, help="说服力/可信度 score (1-10)")
    p.add_argument("--originality", type=float, help="原创与差异 score (1-10)")
    p.add_argument("--replication", type=float, help="复刻价值 score (1-10)")
    p.add_argument("--conversion", type=float, help="转化/留存设计 score (1-10)")
    p.add_argument(
        "--product-match",
        dest="product_match",
        type=float,
        help="产品-视频匹配 score (1-10). Only used when --type 电商成交.",
    )
    p.add_argument(
        "--confidence",
        choices=VALID_CONFIDENCE,
        default=None,
        help="Evidence confidence: high (full video + backend data), "
        "medium (full video, no backend), low (partial/keyframes only).",
    )
    p.add_argument(
        "--json",
        type=argparse.FileType("r", encoding="utf-8"),
        help="JSON file with type, scores, and optional confidence.",
    )
    return p


def validate_score(name, value):
    if value is None:
        return None
    if not (1 <= value <= 10):
        raise SystemExit(f"{name} score must be between 1 and 10, got {value}")
    return round(value, 1)


def compute_score(video_type, scores, confidence=None):
    """Compute weighted total score.

    Args:
        video_type: One of the 6 video types.
        scores: Dict mapping dimension key -> score (1-10).
        confidence: Optional confidence level (high/medium/low).

    Returns:
        Dict with weighted_total, raw_average, dimension breakdown, confidence.
    """
    weights = WEIGHT_TABLE[video_type]
    breakdown = []
    weighted_sum = 0.0
    scored_count = 0

    for dim_key, weight in weights.items():
        score = scores.get(dim_key)
        if score is None:
            continue
        # Weighted score = raw_score / 10 * weight
        weighted = score / 10.0 * weight
        weighted_sum += weighted
        scored_count += 1
        breakdown.append(
            {
                "dimension": DIMENSION_NAMES.get(dim_key, dim_key),
                "score": score,
                "weight": weight,
                "weighted": round(weighted, 2),
            }
        )

    # Raw average of scored dimensions
    raw_scores = [s for s in scores.values() if s is not None]
    raw_average = sum(raw_scores) / len(raw_scores) if raw_scores else 0

    # Auto-detect confidence if not provided
    if confidence is None:
        required_dims = list(weights.keys())
        missing = [d for d in required_dims if scores.get(d) is None]
        if not missing:
            confidence = "medium"  # default when all dimensions scored but no backend data
        elif len(missing) <= 2:
            confidence = "low"
        else:
            confidence = "low"

    result = {
        "video_type": video_type,
        "weighted_total": round(weighted_sum, 2),
        "raw_average": round(raw_average, 2),
        "dimensions_scored": scored_count,
        "dimensions_total": len(weights),
        "breakdown": breakdown,
        "confidence": confidence,
    }

    # Flag missing dimensions
    missing_dims = [
        DIMENSION_NAMES.get(d, d) for d in weights if scores.get(d) is None
    ]
    if missing_dims:
        result["missing_dimensions"] = missing_dims

    return result


def main():
    args = build_parser().parse_args()

    # Load from JSON or CLI args
    if args.json:
        try:
            data = json.load(args.json)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSON: {exc}")
        video_type = data.get("type")
        if not video_type:
            raise SystemExit("JSON must contain 'type' field")
        if video_type not in VALID_TYPES:
            raise SystemExit(
                f"invalid video type '{video_type}', must be one of: {VALID_TYPES}"
            )
        scores = {}
        for dim_key in ("hook", "rhythm", "density", "persuasion",
                        "originality", "replication", "conversion", "product_match"):
            if dim_key in data:
                scores[dim_key] = validate_score(dim_key, float(data[dim_key]))
        confidence = data.get("confidence")
        if confidence and confidence not in VALID_CONFIDENCE:
            raise SystemExit(
                f"invalid confidence '{confidence}', must be one of: {VALID_CONFIDENCE}"
            )
    else:
        if not args.type:
            raise SystemExit("--type is required when not using --json")
        video_type = args.type
        scores = {
            "hook": validate_score("hook", args.hook),
            "rhythm": validate_score("rhythm", args.rhythm),
            "density": validate_score("density", args.density),
            "persuasion": validate_score("persuasion", args.persuasion),
            "originality": validate_score("originality", args.originality),
            "replication": validate_score("replication", args.replication),
            "conversion": validate_score("conversion", args.conversion),
        }
        if video_type == "电商成交" and args.product_match is not None:
            scores["product_match"] = validate_score("product_match", args.product_match)
        confidence = args.confidence

    # Require at least some scores
    if all(v is None for v in scores.values()):
        raise SystemExit("at least one dimension score is required")

    result = compute_score(video_type, {k: v for k, v in scores.items() if v is not None}, confidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
