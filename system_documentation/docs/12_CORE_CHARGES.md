# 12 Core Charges

Tags: cores, rebuildables, deposits, credit_memo, vendor_credit

## Problem
Rebuildable/reman parts create core obligations:
- customers owe cores back to you
- you owe cores back to vendors (or pay core charges)

## Gold standard model
Track cores as a ledger:
- CoreLedgerEvent (append-only)

Event types:
- CORE_CHARGED (obligation created)
- CORE_RETURNED (physical return logged)
- CORE_CREDIT_ISSUED (credit memo or vendor credit posted)
- CORE_WRITEOFF (obligation closed without return)

Balances derived:
- open_core_qty = charged - returned - writeoff (and/or credit)

## Customer-facing core deposit
Best practice:
- invoice includes explicit “core deposit” line
- core return triggers CreditMemo
- ledger closes obligation

## Vendor core credits
Vendor bill may include core charge.
When cores returned and vendor issues credit:
- VendorCredit synced to QBO
- ledger closes obligation

## References
- packages/inventory_management_gold_standard_package_v1.zip
- packages/inventory_qbo_mapping_appendix_package_v1.zip
