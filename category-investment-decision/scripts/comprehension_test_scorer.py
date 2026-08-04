#!/usr/bin/env python3
"""Score formal non-implementer comprehension evidence without self-attestation."""
from __future__ import annotations
from collections import Counter, defaultdict
from decimal import Decimal
from typing import Any

CORE_ROLES = {"category_research", "operations", "supply_or_procurement", "capital_decision", "newcomer"}

class ComprehensionError(ValueError):
    pass

def score(payload: dict[str, Any]) -> dict[str, Any]:
    responses = payload.get("responses")
    if not isinstance(responses, list) or len(responses) < 20:
        raise ComprehensionError("formal gate requires at least 20 non-implementers")
    ids = [item.get("participant_id") for item in responses]
    if any(not value for value in ids) or len(set(ids)) != len(ids):
        raise ComprehensionError("participant IDs must be unique and nonempty")
    roles = Counter(item.get("role") for item in responses)
    if any(roles[role] < 4 for role in CORE_ROLES):
        raise ComprehensionError("each core role requires at least four participants")
    by_role: dict[str, list[Decimal]] = defaultdict(list)
    severe = 0; decision_misreads = 0; total = Decimal(0)
    required_scores = {"decision", "risk_confidence", "top3_actions", "do_not_do_yet", "missing_data", "go_stop", "sovereignty"}
    for item in responses:
        if item.get("participated_in_implementation"):
            raise ComprehensionError("implementers cannot enter formal comprehension evidence")
        components = item.get("scores", {})
        if set(components) != required_scores:
            raise ComprehensionError("comprehension score components incomplete")
        if components["decision"] not in {0, 1, 2} or any(components[key] not in {0, 1} for key in required_scores - {"decision"}):
            raise ComprehensionError("invalid component score")
        value = sum(Decimal(component) for component in components.values())
        total += value; by_role[item["role"]].append(value)
        decision_misreads += components["decision"] == 0
        severe += int(item.get("redline_misread", False) or item.get("do_not_do_yet_misread", False) or item.get("stop_misread", False))
        if not item.get("raw_response_id") or item.get("completion_seconds") is None:
            raise ComprehensionError("raw answer evidence and completion time are required")
    average = total / Decimal(len(responses)); decision_rate = Decimal(decision_misreads) / Decimal(len(responses))
    passed = average >= Decimal(7) and decision_rate < Decimal("0.05") and severe == 0
    return {"status": "passed" if passed else "failed", "participants": len(responses), "average_score": str(average), "decision_severe_misread_rate": str(decision_rate), "redline_do_not_stop_severe_misreads": severe, "role_average": {role: str(sum(values) / Decimal(len(values))) for role, values in sorted(by_role.items())}}
