#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
PENDING={"PENDING","pending",""}
def dt(x): return datetime.fromisoformat(x.replace("Z","+00:00"))
def validate(x,as_of):
 errors=[]
 try: jsonschema.validate(x,json.loads((ROOT/"schemas/qualified-professional-signoff.schema.json").read_text()),format_checker=jsonschema.FormatChecker())
 except jsonschema.ValidationError as e: return [e.message]
 for key in ("reviewer_identity_ref","professional_role","credential_authority","credential_identifier_ref","signature_ref"):
  if x[key] in PENDING: errors.append(f"{key} is pending")
 if any(j in PENDING for j in x["jurisdictions"]): errors.append("jurisdiction is pending")
 if any(j in PENDING for j in x["object_refs"]+x["intended_uses"]+x["credential_scope"]): errors.append("object use or credential scope is pending")
 if x["topic"] not in x["credential_scope"]: errors.append("credential scope does not cover review topic")
 if x["decision"]!="approved": errors.append("professional review is not approved")
 if x["evidence_index_hash"]=="0"*64: errors.append("evidence index is not bound")
 if dt(x["credential_verified_at"])>dt(as_of): errors.append("credential verification is future dated")
 if dt(x["signed_at"])<dt(x["credential_verified_at"]): errors.append("signature predates credential verification")
 if x["credential_expires_at"] and dt(x["credential_expires_at"])<=dt(as_of): errors.append("credential is expired")
 if dt(x["signed_at"])>dt(as_of): errors.append("signature is future dated")
 return errors
if __name__=="__main__":
 x=json.loads(Path(__import__('sys').argv[1]).read_text()); e=validate(x,__import__('sys').argv[2]); print("SIGNOFF=PASS" if not e else "SIGNOFF=BLOCKED\n- "+"\n- ".join(e)); raise SystemExit(bool(e))
