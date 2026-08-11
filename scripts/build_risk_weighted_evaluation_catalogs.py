#!/usr/bin/env python3
"""Build risk-weighted professional evaluation catalogs without claiming L4.

The generated cases are engineering fixtures.  Each case binds a domain-native
failure mechanism to evidence, counterevidence, a flip condition, mutation and
rollback.  They are not real customer replays or professional opinions.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODES = ("standard", "conflict", "extreme", "multi_turn", "adversarial", "recovery")

DOMAIN_PLANS = {
    "D01": {
        "path": "category-investment-decision/evaluations/evaluation-catalog.json",
        "prefix": "CIDM-RW", "target": 24,
        "mechanisms": ["资本组合约束", "非补偿准入门", "牛基熊利润情景", "小测资本上限"],
        "states": ["inconclusive", "blocked", "test", "reallocate", "stop", "controlled_reentry"],
    },
    "D02": {
        "path": "competitive-intelligence-monitoring/evaluations/evaluation-catalog.json",
        "prefix": "CIM-RW", "target": 24,
        "mechanisms": ["竞品身份去重", "变化双源确认", "代理信号边界", "事件归因窗口"],
        "states": ["monitor", "inconclusive", "blocked", "recompute", "rejected", "controlled_recovery"],
    },
    "D05": {
        "path": "legal-tax-intellectual-property-market-access-decision/evaluations/evaluation-catalog.json",
        "prefix": "D05-RW", "target": 48,
        "mechanisms": ["多辖区适用规则冲突", "证书对象工厂版本错配", "认证测试标签路由", "商标专利版权并行冲突",
                       "税务海关交易链冲突", "高风险营销Claim", "平台下架与法律准入分离", "证书吊销召回恢复"],
        "states": ["evidence_required", "professional_review", "blocked", "restricted_continue", "recovery_pending", "exited"],
    },
    "D07": {
        "path": "logistics-inventory-fulfillment-decision/evaluations/evaluation-catalog.json",
        "prefix": "LIFD-RW", "target": 42,
        "mechanisms": ["ATP_CTP多平台争用", "多仓库存保护分配", "海空陆路线容量切换", "旺季补货与需求漂移",
                       "仓容订单容量守恒", "逆向退货退供召回", "海外库存清算退出"],
        "states": ["allocate", "constrain", "blocked", "recompute", "rollback", "controlled_recovery"],
    },
    "D08": {
        "path": "platform-store-listing-conversion/evaluations/evaluation-catalog.json",
        "prefix": "PLCO-RW", "target": 24,
        "mechanisms": ["索引可见性诊断", "Offer库存承诺", "变体合并拆分治理", "移动桌面漏斗守恒"],
        "states": ["repair", "blocked", "test", "recompute", "rejected", "controlled_recovery"],
    },
    "D09": {
        "path": "advertising-analysis-measurement-optimization/evaluations/evaluation-catalog.json",
        "prefix": "AAMO-RW", "target": 24,
        "mechanisms": ["三本账一致性", "平均边际效率分离", "归因增量分离", "放量库存利润红线"],
        "states": ["hold", "reduce", "blocked", "test", "stop", "controlled_recovery"],
    },
    "D11": {
        "path": "video-link-breakdown/evaluations/evaluation-catalog.json",
        "prefix": "VLB-RW", "target": 24,
        "mechanisms": ["钩子与证明机制", "素材权利与Claim", "疲劳刷新", "跨平台国家迁移"],
        "states": ["proposed", "blocked", "test", "recompute", "rejected", "controlled_recovery"],
    },
    "D13": {
        "path": "consumer-insights-customer-growth/evaluations/evaluation-catalog.json",
        "prefix": "CIG-RW", "target": 24,
        "mechanisms": ["身份授权与撤回", "收入订单守恒", "Cohort_CLV成熟度", "增量触达与疲劳"],
        "states": ["no_contact", "blocked", "test", "recompute", "stop", "controlled_recovery"],
    },
}


def fingerprint(domain: str, mechanism: str, mode: str) -> str:
    return hashlib.sha256(f"{domain}|{mechanism}|{mode}|2026.07".encode()).hexdigest()


def make_case(domain: str, plan: dict, ordinal: int, mechanism: str, mode: str) -> dict:
    state = plan["states"][MODES.index(mode)]
    token = fingerprint(domain, mechanism, mode)
    risk = "redline" if domain == "D05" else "continuity" if domain == "D07" else "domain_specific"
    return {
        "id": f"{plan['prefix']}-{ordinal:02d}",
        "name": f"{mechanism}-{mode}",
        "mode": mode,
        "object_ref": f"{domain}-{mechanism}@v{ordinal}",
        "object_version": f"v{ordinal}",
        "evidence": [f"E-SUPPORT-{token[:12]}", f"E-LINEAGE-{token[12:24]}"],
        "counterevidence": [f"E-COUNTER-{token[24:36]}"],
        "expected_status": state,
        "must": [mechanism, "对象版本", "证据与反证", "停止条件", "恢复或回滚", "主权边界"],
        "forbidden": ["external_write", "redline_compensation", "synthetic_l4", "unknown_as_zero"],
        "rationale": f"以{mechanism}为主机制处理{mode}场景；支持证据与反证冲突时保持最窄动作上限，"
                     f"不得由其他域评分覆盖{risk}门，预期状态为{state}。",
        "flip_condition": f"仅当反证关闭、对象版本一致、责任人复核且{mechanism}守卫重新通过时重算。",
        "evidence_binding": {
            "source": "synthetic_engineering_fixture",
            "fingerprint": f"sha256:{token}",
            "biz_time": "2026-08-10",
            "valid_until": "2026-09-10",
            "l4_eligible": False,
        },
        "mutation": {
            "field": "object_version",
            "value": "stale_or_mismatched",
            "expected": "blocked",
            "guard": f"{mechanism}:version_lineage",
        },
        "rollback": "restore_last_validated_version_and_recompute_impacted_consumers",
    }


def build_catalog(domain: str, plan: dict) -> dict:
    path = ROOT / plan["path"]
    original = json.loads(path.read_text(encoding="utf-8"))
    retained = [x for x in original.get("cases", []) if not str(x.get("id", "")).startswith(plan["prefix"])]
    generated = []
    ordinal = 1
    for mechanism in plan["mechanisms"]:
        for mode in MODES:
            generated.append(make_case(domain, plan, ordinal, mechanism, mode))
            ordinal += 1
    needed = max(0, plan["target"] - len(retained))
    cases = retained + generated[:needed]
    original["catalog"] = original.get("catalog", f"{domain}-EVAL") .replace("DRAFT", "RISK-WEIGHTED")
    original["cases"] = cases
    original["coverage_contract"] = {
        "method": "risk_weighted_mechanism_x_failure_mode",
        "target": plan["target"],
        "mechanisms": plan["mechanisms"],
        "modes": list(MODES),
        "synthetic_engineering_only": True,
        "l4_inference_forbidden": True,
    }
    return original


def main() -> None:
    ledger = {"contract": "CBDS-RISK-WEIGHTED-COVERAGE-2026.07", "generated_at": "2026-08-10", "domains": []}
    for domain, plan in DOMAIN_PLANS.items():
        catalog = build_catalog(domain, plan)
        path = ROOT / plan["path"]
        path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        ledger["domains"].append({
            "domain_id": domain, "catalog": plan["path"], "case_count": len(catalog["cases"]),
            "mechanisms": plan["mechanisms"], "modes": list(MODES),
            "evidence_types": ["source_catalog", "semantic_validator", "numeric_validator", "mutation", "golden_root"],
            "l4_status": "separate_not_passed",
        })
    out = ROOT / "evaluations/risk-weighted-coverage-ledger.json"
    out.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"RISK_WEIGHTED_CATALOGS_BUILT domains={len(DOMAIN_PLANS)} cases={sum(x['case_count'] for x in ledger['domains'])}")


if __name__ == "__main__":
    main()
