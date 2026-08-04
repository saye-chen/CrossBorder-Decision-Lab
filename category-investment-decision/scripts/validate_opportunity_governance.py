#!/usr/bin/env python3
"""Validate versioned CIDM opportunity-governance registries."""
from __future__ import annotations
import json
from pathlib import Path
from opportunity_signals import ContractError, validate_field_trap_registry, validate_playbook_registry

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    path = ROOT / "references/external-data-field-trap-registry.json"
    try:
        result = validate_field_trap_registry(json.loads(path.read_text(encoding="utf-8")))
        playbooks = validate_playbook_registry(json.loads((ROOT / "references/opportunity-combination-playbooks.json").read_text(encoding="utf-8")))
        runtime = json.loads((ROOT / "references/external-research-runtime-mode.json").read_text(encoding="utf-8"))
        if runtime.get("default_research_mode") != "online_realtime" or runtime.get("external_connector_mode") != "reserved_interface" or runtime.get("mcp_required") is not False:
            raise ContractError("runtime mode must default to online realtime with optional reserved connector")
        if runtime.get("installed_provider_clients") != []:
            raise ContractError("current stage cannot install provider clients")
        fallbacks = runtime.get("fallbacks", {})
        if fallbacks.get("connector_unavailable") != "continue_online_research" or fallbacks.get("connector_empty_response") != "unknown_not_zero":
            raise ContractError("connector fallback must continue online research and preserve unknown")
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        raise SystemExit(f"opportunity governance rejected: {exc}") from exc
    print(json.dumps({"field_traps": result, "playbooks": playbooks, "runtime_mode": "online_realtime_with_reserved_connector"}, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
