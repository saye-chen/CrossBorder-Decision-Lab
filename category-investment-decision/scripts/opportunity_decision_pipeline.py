#!/usr/bin/env python3
"""Controlled OSL pipeline: evidence -> model/oracle -> score -> playbook -> decision card."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from evidence_adapter import normalize
from independent_opportunity_oracles import evaluate as oracle_evaluate
from opportunity_models import evaluate as model_evaluate
from opportunity_signals import compose_playbook, validate_rapid_decision_card, validate_signal_card
from score_engine import evaluate_score

ROOT=Path(__file__).resolve().parents[1]
PLAYBOOKS=json.loads((ROOT/"references/opportunity-combination-playbooks.json").read_text())["playbooks"]

def run(payload):
    adapted=normalize(payload["raw_evidence"],payload["adapter_contract"])
    spec=payload["model"]
    model=model_evaluate(spec["signal_type"],spec["data"],spec["calibration"])
    oracle=oracle_evaluate(spec["signal_type"],spec["data"],spec["calibration"])
    if model["status"]!=oracle["status"] or model["metrics"]!=oracle["metrics"]: raise ValueError("independent oracle mismatch")
    card=dict(payload["signal_card"]); card["status"]=model["status"]; card["derived_metrics"]=model["metrics"]
    validated=validate_signal_card(card)
    score=evaluate_score(payload["score"])
    playbook=next((p for p in PLAYBOOKS if p["playbook_id"]==payload["playbook_id"]),None)
    if playbook is None: raise ValueError("unknown playbook")
    signal_for_composition={**validated,"source_family_id":adapted["source_family_id"]}
    composition=compose_playbook(playbook,[signal_for_composition],payload.get("active_vetoes",[]))
    blocked=score["decision_status"]=="Blocked" or composition["composition_status"] in {"blocked","inconclusive"}
    decision={"decision":"不建议进入" if blocked else score["decision_band"],"confidence":payload.get("confidence","low"),"lifecycle":payload["lifecycle"],"supporting_evidence":card["source_evidence_ids"],"counter_evidence":card["counter_evidence"] or card["alternative_explanations"],"weakest_assumption":payload["weakest_assumption"],"priority_actions":payload["priority_actions"],"do_not_do_yet":payload["do_not_do_yet"],"missing_data":payload.get("missing_data",[]),"minimum_credible_validation":payload["minimum_credible_validation"],"go":payload["go"],"stop":payload["stop"]}
    validate_rapid_decision_card(decision)
    return {"execution_completion":"complete","maturity":"controlled pilot","adapter":adapted,"model":model,"oracle":oracle,"signal":validated,"score":score,"composition":composition,"decision_card":decision}

def main():
    p=argparse.ArgumentParser(); p.add_argument("input",type=Path); a=p.parse_args()
    try: result=run(json.loads(a.input.read_text()))
    except (KeyError,ValueError,OSError,json.JSONDecodeError) as exc: raise SystemExit(f"pipeline blocked: {exc}") from exc
    print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))
if __name__=="__main__": main()
