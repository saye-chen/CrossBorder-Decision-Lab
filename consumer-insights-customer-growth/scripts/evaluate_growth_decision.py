#!/usr/bin/env python3
"""Compose CIG identity, evidence, experiment, economics and contact gates."""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def finite(v,name):
 try:x=float(v)
 except (TypeError,ValueError) as e:raise ValueError(f"{name} must be numeric") from e
 if not math.isfinite(x):raise ValueError(f"{name} must be finite")
 return x

def evaluate(d):
 required=["object_id","as_of_time","purpose","identity","consent","data_quality","analysis_level"]
 missing=[k for k in required if d.get(k) in (None,"")]
 errors=[f"missing:{k}" for k in missing]
 identity=d.get("identity",{});consent=d.get("consent",{});quality=d.get("data_quality",{})
 if identity.get("grain") not in {"account","person","household"}:errors.append("invalid_identity_grain")
 if finite(identity.get("confidence",0),"identity.confidence")<finite(d.get("minimum_identity_confidence",.8),"minimum_identity_confidence"):errors.append("identity_below_threshold")
 for gate in ("purpose_allowed","not_withdrawn","not_unsubscribed","retention_valid"):
  if consent.get(gate) is not True:errors.append(f"consent_gate:{gate}")
 for gate in ("events_reconciled","revenue_reconciled","no_future_leakage"):
  if quality.get(gate) is not True:errors.append(f"data_gate:{gate}")
 level=d.get("analysis_level");allowed=["fact","descriptive","predictive","causal","decision"]
 if level not in allowed:errors.append("invalid_analysis_level")
 experiment=d.get("experiment")
 effect=None;ci=None
 if level in {"causal","decision"}:
  if not isinstance(experiment,dict):errors.append("causal_level_requires_experiment")
  else:
   for gate in ("randomization_valid","exposure_reconciled","outcome_mature","interference_addressed"):
    if experiment.get(gate) is not True:errors.append(f"experiment_gate:{gate}")
   nt=finite(experiment.get("treatment_n",0),"treatment_n");nc=finite(experiment.get("control_n",0),"control_n")
   if nt<=1 or nc<=1:errors.append("experiment_sample_too_small")
   else:
    pt=finite(experiment.get("treatment_outcome",0),"treatment_outcome")/nt;pc=finite(experiment.get("control_outcome",0),"control_outcome")/nc
    if not 0<=pt<=1 or not 0<=pc<=1:errors.append("invalid_outcome_rate")
    else:
     effect=pt-pc;se=math.sqrt(pt*(1-pt)/nt+pc*(1-pc)/nc);ci=[effect-1.96*se,effect+1.96*se]
 action=d.get("action",{});eligible=[]
 for gate in ("frequency_ok","inventory_ok","market_allowed","fairness_ok","sensitive_event_clear"):
  if action.get(gate) is not True:errors.append(f"action_gate:{gate}")
 margin=finite(action.get("incremental_contribution_margin",0),"incremental_contribution_margin")
 costs=sum(finite(action.get(k,0),k) for k in ("incentive_cost","contact_cost","fatigue_cost","risk_cost"))
 niv=(effect if effect is not None else 0)*margin-costs
 if not errors and effect is not None and ci[0]>0 and niv>0:eligible=[action.get("name","contact")]
 decision="Contact" if eligible else "No contact" if not any(x.startswith(("missing","invalid","data_gate","consent_gate","identity","experiment")) for x in errors) else "Blocked"
 return {"object_id":d.get("object_id"),"analysis_level":level,"effect":effect,"ci":ci,"net_incremental_value":niv,"eligible_actions":eligible,"decision":decision,"errors":errors,"stop_conditions":d.get("stop_conditions",[]),"result_feedback_required":["actual_exposure","cost","short_outcome","long_outcome","complaint","withdrawal"]}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 try:r=evaluate(json.loads(a.input.read_text()))
 except (ValueError,OSError,json.JSONDecodeError) as e:p.error(str(e))
 a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__":main()
