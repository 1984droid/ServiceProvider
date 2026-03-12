# State Machines Contract

## WorkOrder
- OPEN → IN_PROGRESS → COMPLETE
- OPEN/IN_PROGRESS → CANCELLED (optional)
Rules:
- COMPLETE is idempotent (second completion call produces no duplicates)
- started_at/completed_at set on first transition

## Invoice
- DRAFT → ISSUED → (PAID/PARTIAL)
- ISSUED → VOID (with audit record)
Rules:
- ISSUED is immutable (only via CreditMemo/adjustment)
- balances computed from allocations

## InspectionRun
- DRAFT → FINALIZED
Rules:
- FINALIZED is immutable (revision model later if needed)

## InspectionDefect
- OPEN → RESOLVED
- OPEN → DEFERRED
- DEFERRED → OPEN (reopened)
Gold standard:
- UNSAFE defects add verification_status:
  NOT_REQUIRED/REQUIRED/PASSED/FAILED

## SpecialOrderPartRequest
- REQUESTED → ORDERED → RECEIVED → ISSUED
- REQUESTED/ORDERED → CANCELLED
