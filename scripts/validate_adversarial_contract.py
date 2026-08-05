#!/usr/bin/env python3
"""Detect fabricated evidence, sovereignty, version, numeric-lineage and partial-failure violations."""
from __future__ import annotations
import argparse,json,re
from datetime import datetime
from pathlib import Path

OWNERS={"investment":"category-investment-decision","competition":"competitive-intelligence-monitoring","content":"video-link-breakdown","customer_growth":"consumer-insights-customer-growth","advertising":"advertising-analysis-measurement-optimization","logistics":"logistics-inventory-fulfillment-decision","listing_conversion":"platform-store-listing-conversion"}

def validate(d):
 errors=[];evidence=d.get("evidence",[]);fingerprints=set();ids=set()
 for i,e in enumerate(evidence):
  if not e.get("source_ref") or not e.get("observed_at") or not e.get("fingerprint"):errors.append(f"fabricated_or_untraceable_evidence:{i}")
  if e.get("fingerprint") in fingerprints:errors.append(f"duplicate_evidence_fingerprint:{e.get('fingerprint')}")
  fingerprints.add(e.get("fingerprint"));ids.add(e.get("id"))
 for a in d.get("actions",[]):
  expected=OWNERS.get(a.get("domain"))
  if expected and a.get("owner")!=expected:errors.append(f"sovereignty_overreach:{a.get('id')}")
 current=[v for v in d.get("versions",[]) if v.get("current")]
 by_object={}
 for v in current:by_object.setdefault(v.get("object_id"),[]).append(v)
 for obj,rows in by_object.items():
  if len(rows)>1:errors.append(f"multiple_current_versions:{obj}")
 for c in d.get("numeric_claims",[]):
  raw=str(c.get("value"))
  if re.search(r"\d",raw) and (not c.get("calculation_id") or not c.get("input_hash") or not c.get("output_hash")):errors.append(f"hallucinated_numeric_lineage:{c.get('id')}")
 source_families={}
 for e in evidence:
  if e.get("source_family"): source_families.setdefault(e["source_family"],[]).append(e.get("id"))
 for family,rows in source_families.items():
  if len(rows)>1 and d.get("independent_source_count",0)>=len(rows): errors.append(f"colluding_source_independence:{family}")
 for window in d.get("analysis_windows",[]):
  if window.get("selected_after_outcome") or not window.get("pre_registered"): errors.append(f"cherry_picked_window:{window.get('id')}")
 for item in d.get("untrusted_inputs",[]):
  if re.search(r"ignore (previous|system)|override (rules|owner)|忽略(以上|系统)|绕过",item.get("content",""),re.I) and not item.get("treated_as_data_only"):
   errors.append(f"embedded_instruction_not_isolated:{item.get('id')}")
 drift=d.get("cumulative_drift",{})
 if drift.get("current_version",0)-drift.get("baseline_version",0)>=drift.get("review_interval",10) and not drift.get("revalidated"):
  errors.append("gradual_drift_requires_revalidation")
 cutoff=d.get("evidence_cutoff")
 for e in evidence:
  if cutoff and e.get("submitted_at") and datetime.fromisoformat(e["submitted_at"].replace("Z","+00:00"))>datetime.fromisoformat(cutoff.replace("Z","+00:00")) and e.get("accepted_for_decision"):
   errors.append(f"post_cutoff_evidence_accepted:{e.get('id')}")
 participant={p.get("skill"):p.get("status") for p in d.get("participant_results",[])}
 for claim in d.get("claims",[]):
  if participant.get(claim.get("producer_skill")) in {"failed","timeout","partial"} and claim.get("state")=="validated":errors.append(f"failed_participant_validated_claim:{claim.get('id')}")
  if not set(claim.get("evidence_ids",[]))<=ids:errors.append(f"claim_missing_evidence:{claim.get('id')}")
 return {"valid":not errors,"errors":errors}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("input",type=Path);a=p.parse_args();r=validate(json.loads(a.input.read_text()));print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r["valid"] else 1
if __name__=="__main__":raise SystemExit(main())
