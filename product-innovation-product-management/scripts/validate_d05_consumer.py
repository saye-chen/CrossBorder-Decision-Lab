#!/usr/bin/env python3
"""D03 consumer boundary for D05 market-access packets."""
OWNED={"product_definition","specification","product_lifecycle"}
REQUIRED={"object_ref","object_version","scope_ref","use_ref","blocked_actions","market_access_gate","external_write"}
def validate(p):
 e=[]
 if not REQUIRED<=set(p): e.append("D03 missing required D05 fields")
 if p.get("external_write") is not False:e.append("D03 rejects external write")
 if OWNED & set(p.get("d05_owned_decisions",[])):e.append("D05 packet invades D03 sovereignty")
 if p.get("market_access_gate") in {"blocked","evidence_required","professional_review"} and "product_release" not in p.get("blocked_actions",[]):e.append("D03 release must reflect D05 gate ceiling")
 return e


if __name__ == "__main__":
 import argparse, json
 from pathlib import Path
 parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("input", type=Path); args=parser.parse_args()
 try: payload=json.loads(args.input.read_text(encoding="utf-8")); errors=validate(payload)
 except (OSError,json.JSONDecodeError,TypeError,ValueError) as exc:
  print(json.dumps({"status":"error","errors":[str(exc)]},ensure_ascii=False)); raise SystemExit(2)
 print(json.dumps({"status":"pass" if not errors else "blocked","errors":errors},ensure_ascii=False,indent=2))
 raise SystemExit(0 if not errors else 1)
