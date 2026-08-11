#!/usr/bin/env python3
"""Adjust registered hypothesis families with Holm, Bonferroni, or BH."""

from __future__ import annotations

from collections import defaultdict

from ecae_common import ECAEError, cli_main, require_probability


def _adjust(pairs: list[tuple[str, float]], method: str) -> dict[str, float]:
    count = len(pairs)
    if method == "bonferroni":
        return {key:min(1.0, p * count) for key, p in pairs}
    ordered = sorted(pairs, key=lambda item: (item[1], item[0]))
    adjusted: dict[str, float] = {}
    if method == "holm":
        running = 0.0
        for index, (key, p_value) in enumerate(ordered):
            running = max(running, min(1.0, (count - index) * p_value))
            adjusted[key] = running
        return adjusted
    if method == "benjamini_hochberg":
        running = 1.0
        for reverse_index in range(count - 1, -1, -1):
            key, p_value = ordered[reverse_index]
            rank = reverse_index + 1
            running = min(running, min(1.0, p_value * count / rank))
            adjusted[key] = running
        return adjusted
    if method == "none_single_primary" and count == 1:
        return {pairs[0][0]:pairs[0][1]}
    raise ECAEError("UNSUPPORTED_ADJUSTMENT", f"Unsupported or invalid adjustment: {method}")


def adjust_multiplicity(value: dict) -> dict:
    hypotheses = value.get("hypotheses")
    method = value.get("method")
    alpha = require_probability(value.get("alpha", 0.05), "alpha")
    if not isinstance(hypotheses, list) or not hypotheses:
        raise ECAEError("EMPTY_HYPOTHESIS_FAMILY", "At least one registered hypothesis is required")
    families: dict[str, list[dict]] = defaultdict(list)
    seen = set()
    for item in hypotheses:
        key = item.get("hypothesis_id")
        family = item.get("family_id")
        if not key or not family or key in seen:
            raise ECAEError("INVALID_HYPOTHESIS_LEDGER", "Each hypothesis needs unique hypothesis_id and family_id")
        seen.add(key)
        raw_p = item.get("p_value")
        if not isinstance(raw_p, (int, float)) or isinstance(raw_p, bool) or not 0 <= raw_p <= 1:
            raise ECAEError("INVALID_P_VALUE", f"p_value[{key}] must be in [0,1]")
        p_value = float(raw_p)
        families[family].append({"hypothesis_id":key,"p_value":p_value})
    output = []
    for family_id in sorted(families):
        pairs = [(item["hypothesis_id"],item["p_value"]) for item in families[family_id]]
        adjusted = _adjust(pairs, method)
        output.append({
            "family_id":family_id,
            "method":method,
            "alpha":alpha,
            "hypotheses":[{"hypothesis_id":key,"p_value":p,"adjusted_p_value":adjusted[key],"reject":adjusted[key] <= alpha} for key,p in pairs]
        })
    return {"families":output,"forks_reruns_windows_share_original_family":True,"exploratory_only":method == "benjamini_hochberg"}


if __name__ == "__main__":
    cli_main(adjust_multiplicity, __doc__ or "Adjust multiplicity")
