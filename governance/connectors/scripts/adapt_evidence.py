#!/usr/bin/env python3
"""Map raw authorized connector fields into a lineage-preserving evidence envelope."""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation


def _valid_value(value, field):
    if value is None: return False, None
    kind = field["type"]
    if kind == "decimal_string":
        if not isinstance(value, str): raise ValueError(f"{field['source_field']} must be decimal string")
        try: parsed = Decimal(value)
        except InvalidOperation as exc: raise ValueError(f"{field['source_field']} invalid decimal") from exc
        if not parsed.is_finite(): raise ValueError(f"{field['source_field']} non-finite")
    elif kind == "integer" and (isinstance(value, bool) or not isinstance(value, int)): raise ValueError(f"{field['source_field']} must be integer")
    elif kind == "datetime":
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None: raise ValueError(f"{field['source_field']} timezone required")
    return True, value


def adapt(raw: dict, manifest: dict, fields: dict, context: dict) -> dict:
    if manifest.get("status") not in {"controlled_pilot", "active", "contract_only"}: raise ValueError("connector is unavailable")
    values, missing = {}, []
    for field in fields["fields"]:
        present, value = _valid_value(raw.get(field["source_field"]), field)
        if present: values[field["canonical_field"]] = {"value": value, "unit": field["unit"], "allowed_uses": field["allowed_uses"]}
        else:
            missing.append({"field": field["canonical_field"], "state": "missing", "semantics": "unknown_not_zero", "required": field["required"]})
    raw_hash = hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"contract": "CBDS-CONNECTOR-EVIDENCE-2026.07", "connector_id": manifest["connector_id"], "tenant_id": context["tenant_id"], "authorization_ref": context["authorization_ref"], "source_class": "authorized_first_party", "raw_reference": context["raw_reference"], "payload_hash": raw_hash, "observed_at": context["observed_at"], "ingested_at": context["ingested_at"], "values": values, "missing": missing, "decision_authority": False, "external_write": False}


def main() -> int:
    if len(sys.argv) != 5:
        print("usage: adapt_evidence.py MANIFEST.json FIELD_CONTRACT.json RAW.json CONTEXT.json")
        return 2
    paths = [pathlib.Path(p) for p in sys.argv[1:]]
    result = adapt(*(json.loads(path.read_text()) for path in paths))
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
