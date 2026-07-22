#!/usr/bin/env python3
from plco_common import GATES, fail, run_cli

VALID = {"pass", "conditional", "fail", "unknown"}
ORDER = {"pass": 0, "conditional": 1, "unknown": 2, "fail": 3}

def evaluate(data):
    gates = data.get("gates", {})
    missing = [g for g in GATES if g not in gates]
    if missing: fail("missing gates: " + ", ".join(missing))
    normalized = {}
    for gate in GATES:
        item = gates[gate]
        status = item if isinstance(item, str) else item.get("status")
        if status not in VALID: fail(f"{gate} invalid status")
        normalized[gate] = status
    worst = max(normalized.values(), key=ORDER.get)
    limit = {"pass":"test_or_execute","conditional":"conditional_test","unknown":"diagnose_only","fail":"blocked"}[worst]
    return {"status":"ok", "gates":normalized, "overall":worst, "action_limit":limit,
            "blocking_gates":[g for g,s in normalized.items() if s in {"fail","unknown"}]}

if __name__ == "__main__": run_cli(evaluate, "PLCO-gates-1")
