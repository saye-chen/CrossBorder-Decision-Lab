#!/usr/bin/env python3
"""Detect fabricated evidence, sovereignty, version, numeric-lineage and partial-failure violations."""
from __future__ import annotations
import argparse,json,re
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
 participant={p.get("skill"):p.get("status") for p in d.get("participant_results",[])}
 for claim in d.get("claims",[]):
  if participant.get(claim.get("producer_skill")) in {"failed","timeout","partial"} and claim.get("state")=="validated":errors.append(f"failed_participant_validated_claim:{claim.get('id')}")
  if not set(claim.get("evidence_ids",[]))<=ids:errors.append(f"claim_missing_evidence:{claim.get('id')}")
 return {"valid":not errors,"errors":errors}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("input",type=Path);a=p.parse_args();r=validate(json.loads(a.input.read_text()));print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r["valid"] else 1
if __name__=="__main__":raise SystemExit(main())
