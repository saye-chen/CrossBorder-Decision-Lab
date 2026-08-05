#!/usr/bin/env python3
"""D04 consumer boundary for D05 market-access packets."""
OWNED={"supplier_selection","production_release","batch_quality_release"}
REQUIRED={"object_ref","object_version","product_facts","market_access_gate","blocked_actions","external_write"}
def validate(p):
 e=[]
 if not REQUIRED<=set(p):e.append("D04 missing required D05 fields")
 if p.get("external_write") is not False:e.append("D04 rejects external write")
 if OWNED & set(p.get("d05_owned_decisions",[])):e.append("D05 packet invades D04 sovereignty")
 if p.get("market_access_gate")=="passed" and p.get("quality_gate") in {None,"blocked","unknown"} and p.get("production_release_requested"):e.append("D05 gate cannot substitute D04 quality release")
 return e
