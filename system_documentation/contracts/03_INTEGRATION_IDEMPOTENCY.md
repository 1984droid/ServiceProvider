# Integration Idempotency Contract

## QBO sync
- All QBO pushes MUST be idempotent.
- Use QBOMapping(local_id ↔ qbo_id + SyncToken).
- Use Outbox events with unique idempotency keys:
  (tenant_id, provider, entity_type, local_id, action)

## Retry behavior
- If create succeeded but response lost: retry must not create duplicates.
- If mapping exists: update, do not create.

## Webhooks
- Dedupe webhook events by payload hash + timestamp window.
- Never apply webhook deltas blindly; re-fetch entity if needed.
