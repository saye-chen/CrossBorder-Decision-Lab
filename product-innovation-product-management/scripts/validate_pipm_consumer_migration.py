#!/usr/bin/env python3
"""Fail-closed validator for all D03 consumer migration evidence."""
from __future__ import annotations
import importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DIR=ROOT/"evaluations/migration"
REPO=ROOT.parent
spec=importlib.util.spec_from_file_location("consumer_side",ROOT/"scripts/validate_consumer_side_adapter.py");CS=importlib.util.module_from_spec(spec);spec.loader.exec_module(CS)
EXPECTED={"category-investment-decision","competitive-intelligence-monitoring","video-link-breakdown","consumer-insights-customer-growth","advertising-analysis-measurement-optimization","logistics-inventory-fulfillment-decision","platform-store-listing-conversion","creator-affiliate-partnership-management","marketing-brand-campaign-management","pricing-profit-finance-cashflow-decision","governance/erdg"}
def validate(values=None):
 v=values or {p.stem:json.loads(p.read_text()) for p in DIR.glob("*.json")};e=[]
 adapters=v["consumer-adapters"]["adapters"];names={x["consumer"] for x in adapters}
 if names!=EXPECTED:e.append("consumer_inventory")
 for a in adapters:
  d=a["consumer"]
  for f in ("required_fields","optional_fields","ignored_fields","forbidden_fields","field_mapping","mapping_classification","retained_sovereignty","forbidden_writeback","allowed_uses","forbidden_uses","blocked_actions","preserved_results","reaccept_triggers","legacy_reader"):
   if not a.get(f):e.append(f"{d}:missing:{f}")
  if set(a["required_fields"])!=set(a["field_mapping"]) or set(a["required_fields"])!=set(a["mapping_classification"]):e.append(f"{d}:mapping_incomplete")
  if any(a["mapping_classification"][x]!="lossless" for x in a["required_fields"]):e.append(f"{d}:required_not_lossless")
  if not set(a["retained_sovereignty"])<=set(a["forbidden_writeback"]):e.append(f"{d}:sovereignty_writeback")
  if a["status"]!="automated_contract_accepted" or a["independent_owner_accepted"] is not False:e.append(f"{d}:acceptance_state")
  if a["external_write"] is not False:e.append(f"{d}:external_write")
 inv=v["source-inventory"]
 if {x["consumer"] for x in inv["inventory"]}!=EXPECTED or not inv["all_legacy_readers_preserved"]:e.append("source_inventory")
 if any(x["retirement_allowed"] for x in inv["inventory"]):e.append("premature_retirement")
 results=v["dual-run-results"]["results"]
 for d in EXPECTED:
  rows=[x for x in results if x["consumer"]==d]
  if len(rows)!=2 or {x["difference_class"] for x in rows}!={"equivalent","incomparable"}:e.append(f"{d}:dual_run")
  if any(x["difference_class"]=="incomparable" and x["result"]!="blocked" for x in rows):e.append(f"{d}:incomparable_not_blocked")
 if v["dual-run-results"]["error_count"]!=0:e.append("dual_run_errors")
 ac=v["consumer-acceptance"]["acceptances"]
 if {x["consumer"] for x in ac}!=EXPECTED or not all(x["automated_contract_accepted"] and not x["independent_owner_accepted"] for x in ac):e.append("acceptance")
 for x in ac:
  ap=REPO/x.get("adapter_path","");ep=REPO/x.get("acceptance_path","")
  if not ap.is_file() or not ep.is_file():e.append(f"{x.get('consumer')}:consumer_side_evidence_missing")
  elif CS.validate_files(ap,ep):e.append(f"{x['consumer']}:consumer_side_validation")
  if not (ap.parent/"validate_adapter.py").is_file() or not (ap.parent/"test_adapter.py").is_file():e.append(f"{x.get('consumer')}:consumer_side_executable_missing")
 state=v["migration-state"]
 if state["stage"]!="automated_contract_accepted" or state["authoritative"] or not state["legacy_reader_active"] or state["unaccepted_consumers"]:e.append("migration_state")
 rb=v["rollback-manifest"]
 if rb["status"]!="passed" or not rb["legacy_reader_verified"] or not all(x["restored"] for x in rb["release_units"]):e.append("rollback")
 if any(x.get("external_write") is not False for x in (v["consumer-adapters"],state,rb)):e.append("external_write")
 return e
if __name__=="__main__":
 e=validate()
 if e:raise SystemExit("PIPM_WP9=BLOCKED\n-"+"\n-".join(e))
 print("PIPM_WP9=PASS consumers=11 dual_runs=22 rollback_units=6")
