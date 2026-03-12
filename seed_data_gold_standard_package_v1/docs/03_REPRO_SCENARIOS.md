# 03 Repro Scenarios (Manual workflows to validate)

These align directly with the integration gaps and gold-standard improvements.

## Scenario S1 — UNSAFE defect → repair → verification
1) Open the seeded inspection run and view defects (one is UNSAFE).
2) Generate proposals and bulk-promote into a work order.
3) Issue parts from Service Truck 12.
4) Complete the work order.
5) Verify:
   - defect.status = RESOLVED
   - defect.verification_status = REQUIRED
6) Run the seeded recheck inspection:
   - set verification PASSED
7) Confirm leasing compliance snapshot switches to COMPLIANT.

## Scenario S2 — Special order part reserved to a work order
1) Open the seeded special order request.
2) Convert to PO and mark as SENT.
3) Receive into Special Order Staging.
4) Verify reservation exists for the work order.
5) Attempt to issue same part to another WO → should fail without override.

## Scenario S3 — Core deposit lifecycle
1) Sell/issue Reman Alternator with core deposit line.
2) Confirm CoreLedgerEvent balance shows customer owes 1 core.
3) Record core return.
4) Issue credit memo.
5) Confirm open core obligation is cleared.

## Scenario S4 — QBO sync dry-run
1) Ensure tenant has a QBO connection in DISCONNECTED state.
2) Issue an invoice; confirm outbox events are created.
3) Configure sandbox credentials and re-run sync worker to validate idempotency.
