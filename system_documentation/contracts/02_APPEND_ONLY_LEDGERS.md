# Append-only Ledgers Contract

This system depends on auditable ledgers.

## InventoryTransaction ledger
- append-only
- Stock cache must be derived from ledger
- adjustments must have reason codes and actor

## AssetCostEvent ledger
- emitted on work order completion and non-WO expenses
- append-only
- idempotent emission required (no duplicates on retries)

## CoreLedgerEvent ledger
- append-only
- balances derived from aggregation per party+part
- credits/refunds close obligations via events

## Required tests (examples)
- completing the same work order twice creates no duplicate AssetCostEvents
- applying the same inventory receipt twice is prevented via idempotency key/unique constraint
