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

## Lifecycle and responsibility

The normative lifecycle is `draft -> contract_only -> controlled_pilot -> active
-> suspended -> retired`. The current repository ceiling is `contract_only`.
Every transition requires the owner, approver, reason, effective time, manifest
hash, affected consumers, rollback target and audit destination defined in
`connector-lifecycle-contract.json`. A connector cannot self-approve, skip a
state, or restore itself after authentication, integrity or authorization
failure.

The connector owner is responsible for transport behavior, credentials,
quotas, source-field mapping and connector incidents. Domain owners remain
responsible for interpretation and decisions. ERDG owns evidence acceptance;
the Action Gateway owns write authorization. A successful transport response
is therefore neither accepted evidence nor an approved business action.

## Read path controls

Each observation preserves tenant, marketplace, object key, source field,
canonical field, unit/currency, business time, observation time, ingestion
time, page/cursor lineage and deduplication key. Pagination terminates only on a
source-declared end condition. Retries are bounded and jittered; exhaustion is
`inconclusive`, never an empty business result. Partial failures quarantine the
affected fields and preserve independently valid fields.

Freshness and retention are field-class policies. Stale, conflicting,
unauthorized or out-of-scope data cannot be upgraded by aggregation. Raw
evidence is immutable; normalized corrections create a new version linked to
the original observation.

## Credential and incident controls

Secrets use an external secret manager, least privilege, tenant isolation,
rotation and revocation. Authentication failure, unexpected privilege, schema
drift, replay collision or lineage mismatch suspends the affected connector.
Recovery requires credential rotation where applicable, a clean read-only
probe, reconciliation of the affected window and owner approval. Incident
records state affected fields, time range, consumers and invalidated decisions.

## Write path controls

Write capability requires a distinct connector status and a separate Action
Gateway grant. The grant binds the exact operation, owner decision, target,
packet hash, human approver, expiry, dry run, idempotency key, rollback and
audit sink. Batch partial success never becomes overall success: successful,
failed and unknown targets are recorded separately and compensation is limited
to the approved rollback scope.

Run `../../scripts/validate_operational_governance_depth.py` to verify lifecycle
states, transition guards, failure semantics and prohibited shortcuts. Passing
that validator does not activate a connector or authorize a write.
