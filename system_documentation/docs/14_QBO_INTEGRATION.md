# 14 QuickBooks Online Integration

Tags: qbo, integration, oauth, idempotency, mapping, webhooks

## Philosophy
QuickBooks Online is the accounting system-of-record.
Your platform is the operational system-of-record.

## Connection model
Per tenant:
- QBOConnection stores realmId and encrypted tokens
- token refresh handled automatically
- revocation results in DISCONNECTED state requiring re-auth

## Sync strategy (recommended v1)
Push-first:
- Customers, Vendors
- Items (parts/services)
- Invoices / SalesReceipts
- Payments
- VendorBills / VendorCredits
- CreditMemos

## Inventory sync mode
Default: FINANCIAL_ONLY
- do not sync bin/truck stock quantities
- sync financial documents only

Opt-in future mode: QTY_ON_HAND_AGGREGATE.

## Idempotency
Required:
- QBOMapping table (local_id ↔ qbo_id + SyncToken)
- outbox queue with unique idempotency keys
- retries must not create duplicates

## Core deposit pattern
Reman sale uses:
- part line + core deposit line
Core return uses:
- CreditMemo for deposit line
Vendor core credits use:
- VendorCredit

## References
- packages/financial_system_qbo_ready_package_v1.zip
- packages/inventory_qbo_mapping_appendix_package_v1.zip
