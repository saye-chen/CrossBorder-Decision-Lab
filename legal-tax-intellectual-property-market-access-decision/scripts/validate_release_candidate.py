#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]

def validate():
    errors=[]
    for rel in ["references/professional-depth-governance.md","references/skill-integration-protocol.md","references/data-contract-and-automation.md","references/confidential-material-governance.md","references/output-protocols/professional-report-delivery.md","evaluations/completion-readiness.json","evaluations/consumer-contract-acceptance.json","agents/openai.yaml"]:
        if not (ROOT/rel).is_file(): errors.append(f"missing {rel}")
    for path in (ROOT/"schemas").glob("*.json"):
        try: jsonschema.Draft202012Validator.check_schema(json.loads(path.read_text()))
        except Exception as exc: errors.append(f"invalid schema {path.name}: {exc}")
    try:
        report=json.loads((ROOT/"evaluations/golden/blocked-safety-report.json").read_text()); schema=json.loads((ROOT/"schemas/professional-report.schema.json").read_text()); jsonschema.validate(report,schema,format_checker=jsonschema.FormatChecker())
        if report["gate_status"]!="blocked" or report["external_write"] is not False: errors.append("golden does not fail closed")
    except Exception as exc: errors.append(f"invalid golden: {exc}")
    catalog=json.loads((ROOT/"evaluations/evaluation-catalog.json").read_text()); ids=[x["id"] for x in catalog.get("cases",[])]
    if len(ids)<12 or len(ids)!=len(set(ids)): errors.append("evaluation catalog lacks unique breadth")
    replay=json.loads((ROOT/"evaluations/historical-replay-template.json").read_text())
    if replay.get("production_ready") is not False or replay.get("cases")!=[]: errors.append("L4 template must remain empty and closed")
    confidential=(ROOT/"references/confidential-material-governance.md").read_text()
    for marker in ("最少字段","脱敏引用","授权用途","访问角色","保留期限","删除责任人","停止处理","适格律师"):
        if marker not in confidential: errors.append(f"confidential-material governance missing {marker}")
    return errors

if __name__=="__main__":
    found=validate()
    if found: raise SystemExit("D05 release candidate failed:\n- "+"\n- ".join(found))
    print("D05 release candidate internal gates passed; L4 remains closed.")
