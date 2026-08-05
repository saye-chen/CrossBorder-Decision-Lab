#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parent
EXPECTED={"D03":("product-innovation-product-management","PIPM-2026.07"),"D04":("supplier-procurement-production-quality-decision","SPPQ-2026.07"),"D08":("platform-store-listing-conversion","PLCO-2026.07")}
def load_validator(path,domain):
 spec=importlib.util.spec_from_file_location(f"d05_consumer_{domain}",path); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def validate(x):
 errors=[]; rows={r.get("consumer"):r for r in x.get("records",[])}; packets=json.loads((ROOT/"evaluations/d05-consumer-packets.json").read_text())["packets"]
 if set(rows)!=set(EXPECTED): errors.append("consumer coverage must be exactly D03 D04 D08")
 for domain,(skill,runtime) in EXPECTED.items():
  r=rows.get(domain,{})
  if r.get("runtime")!=runtime or runtime not in (REPO/skill/"SKILL.md").read_text(): errors.append(f"{domain} runtime mismatch")
  if not r.get("required_fields") or not r.get("preserved_sovereignty"): errors.append(f"{domain} contract lacks fields or sovereignty")
  validator=REPO/r.get("validator","")
  if r.get("automated_contract_status")!="verified_by_consumer_validator" or not validator.is_file(): errors.append(f"{domain} consumer validator not bound")
  elif load_validator(validator,domain).validate(packets[domain]): errors.append(f"{domain} consumer validator rejected canonical packet")
  if r.get("external_write") is not False: errors.append(f"{domain} external write forbidden")
 if any(r.get("independent_owner_status")!="accepted" for r in rows.values()):
  if x.get("next_stage_effect")!="blocked_until_independent_owner_acceptance": errors.append("pending owner acceptance must block next stage")
 return errors
if __name__=="__main__":
 x=json.loads((ROOT/"evaluations/consumer-contract-acceptance.json").read_text()); e=validate(x); print("CONSUMER_CONTRACTS=PASS_OWNER_PENDING" if not e else "CONSUMER_CONTRACTS=FAIL\n- "+"\n- ".join(e)); raise SystemExit(bool(e))
