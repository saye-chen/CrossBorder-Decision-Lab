#!/usr/bin/env python3
"""Compute traceable CRI, CPI, RCG and proxy HHI from reviewed inputs."""

import argparse
import json
from pathlib import Path


CRI_WEIGHTS = {"market": 0.3, "category": 0.4, "customer": 0.3}
DEFAULT_CPI_WEIGHTS = {"product": 0.2, "price": 0.2, "content": 0.2, "reputation": 0.2, "channel": 0.2}


def bounded(name, value):
    if not isinstance(value, (int, float)) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be numeric in [0, 1]")
    return float(value)


def weighted(values, weights, prefix):
    missing = [key for key in weights if key not in values]
    if missing:
        raise ValueError(f"{prefix} missing fields: {', '.join(missing)}")
    return sum(bounded(f"{prefix}.{key}", values[key]) * weight for key, weight in weights.items())


def validate_weights(weights, name):
    if abs(sum(weights.values()) - 1.0) > 1e-9 or any(value < 0 for value in weights.values()):
        raise ValueError(f"{name} weights must be non-negative and sum to 1")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    cpi_weights = data.get("cpi_weights", DEFAULT_CPI_WEIGHTS)
    validate_weights(CRI_WEIGHTS, "CRI")
    validate_weights(cpi_weights, "CPI")
    own_cpi = weighted(data["own"]["dimensions"], cpi_weights, "own.dimensions")
    rows = []
    proxies = []
    for competitor in data.get("competitors", []):
        cri = weighted(competitor["overlaps"], CRI_WEIGHTS, f"{competitor['id']}.overlaps")
        cpi = weighted(competitor["dimensions"], cpi_weights, f"{competitor['id']}.dimensions")
        proxy = competitor.get("share_proxy")
        if proxy is not None:
            if not isinstance(proxy, (int, float)) or proxy < 0:
                raise ValueError("share_proxy must be non-negative")
            proxies.append(float(proxy))
        rows.append({"id": competitor["id"], "cri": cri, "cpi": cpi, "rcg": cpi - own_cpi, "share_proxy": proxy})
    proxy_hhi = None
    total = sum(proxies)
    if proxies and total > 0:
        proxy_hhi = sum((value / total) ** 2 for value in proxies) * 10000
    result = {
        "model_version": data.get("model_version", "CIM-2026.10"),
        "normalization_basis": data.get("normalization_basis"),
        "cpi_weights": cpi_weights,
        "own_cpi": own_cpi,
        "competitors": rows,
        "proxy_hhi": proxy_hhi,
        "proxy_hhi_warning": "基于输入代理分布估算，不等同真实市场份额 HHI" if proxy_hhi is not None else None,
    }
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
