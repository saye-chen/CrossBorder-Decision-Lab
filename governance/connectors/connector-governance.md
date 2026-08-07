# Controlled Connector Governance

Contract: `CBDS-CONNECTOR-2026.07`

Connectors transport authorized evidence; they do not become decision owners.
Every connector declares identity, permissions, credential isolation, data
classes, field contracts, pagination/deduplication, rate/cost limits, failure
semantics, lineage, retention, and rollback. An empty response is never zero.

Default mode is read-only. Evidence adapters preserve raw source references,
observation time, ingestion time, authorization scope, field quality, and
missing/conflicting/stale states. They may not upgrade evidence or fabricate a
field.

External writes require a separate Action Gateway request bound to an approved
owner decision, exact target, idempotency key, least-privilege permission,
human approval, expiry, dry-run result, rollback plan, and audit destination.
The repository's current connectors are `contract_only`; therefore the gateway
must deny writes. No credential, token, cookie, or secret belongs in this repo.

Run `scripts/validate_connector_contract.py` for manifests and field contracts,
`scripts/adapt_evidence.py` for deterministic evidence envelopes, and
`scripts/authorize_action.py` for fail-closed gateway evaluation.
