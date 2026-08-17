#!/usr/bin/env python3
from __future__ import annotations
import json
import argparse
from datetime import datetime
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[1]
PENDING={"PENDING","pending",""}
def dt(x):
 parsed=datetime.fromisoformat(x.replace("Z","+00:00"))
 if parsed.tzinfo is None: raise ValueError("timezone required")
 return parsed
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
 parser=argparse.ArgumentParser(description="Validate a qualified professional sign-off against a fixed as-of time.")
 parser.add_argument("input", type=Path)
 parser.add_argument("as_of", help="ISO-8601 validation cutoff")
 args=parser.parse_args()
 try:
  x=json.loads(args.input.read_text(encoding="utf-8")); e=validate(x,args.as_of)
 except (OSError,json.JSONDecodeError,KeyError,TypeError,ValueError) as exc:
  parser.error(f"invalid sign-off input: {exc}")
 print("SIGNOFF=PASS" if not e else "SIGNOFF=BLOCKED\n- "+"\n- ".join(e)); raise SystemExit(bool(e))
