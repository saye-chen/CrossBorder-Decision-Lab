#!/usr/bin/env python3
"""D08 consumer boundary for D05 claim-use packets."""
OWNED={"listing_content","store_structure","conversion_optimization"}
REQUIRED={"object_ref","object_version","claims","claim_use_boundary","blocked_actions","external_write"}
def validate(p):
 e=[]
 if not REQUIRED<=set(p):e.append("D08 missing required D05 fields")
 if p.get("external_write") is not False:e.append("D08 rejects external write")
 if OWNED & set(p.get("d05_owned_decisions",[])):e.append("D05 packet invades D08 sovereignty")
 allowed=set(p.get("claim_use_boundary",{}).get("allowed_claim_ids",[])); claims={x.get("claim_id") for x in p.get("claims",[])}
 if not allowed<=claims:e.append("D08 claim boundary references unknown claim")
 if any(x.get("claim_id") not in allowed and x.get("publish") for x in p.get("claims",[])):e.append("D08 cannot publish claim outside D05 boundary")
 return e
