# 05 Troubleshooting

## Common issues and fixes

### 1) IntegrityError / unique constraint failures
Cause: seed already loaded
Fix: run reset script (or set SEED_FORCE_RESET=1)

### 2) Cross-tenant validation errors
Cause: factory created a record under wrong tenant_root
Fix: ensure every created object has tenant_root set explicitly

### 3) Inventory negatives
Cause: issuing before initial load/receiving
Fix: seed_load creates INITIAL_LOAD adjustment transactions; ensure your issue service checks available_qty.

### 4) Compliance snapshot not changing
Cause: snapshot job not run or policies missing
Fix: run snapshot recompute service in seed_verify.

### 5) QBO sync not running
Cause: no connection or worker disabled
Fix: verify outbox events are created; mock QBO endpoints in integration tests.
