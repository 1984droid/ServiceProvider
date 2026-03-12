# 07 Inspection → Work Orders Integration

Tags: defects, proposals, verification, safety, workflow

## Purpose
Bridge inspection findings to corrective action without free-text chaos.

## Staging model
InspectionDefect does not become a WorkOrderItem directly.
Instead:
1) InspectionDefect
2) WorkOrderLineProposal (editable staging)
3) WorkOrderItem (execution line)

This allows:
- automation suggestions
- human review
- audit of “why this fix was selected”

## Proposal generation
- If a seed mapping exists: propose verb/noun/location and default estimates
- If no mapping exists: generate a conservative fallback proposal and flag origin=FALLBACK

## Gold standard verification loop (UNSAFE)
When a WorkOrder completes and resolves an UNSAFE defect:
- defect.status = RESOLVED (work performed)
- defect.verification_status = REQUIRED
- recheck inspection must be performed:
  - PASSED → compliant
  - FAILED → remain noncompliant/out-of-service

## Evidence propagation
WorkOrderItem should reference:
- defect evidence (photos/measurements) via evidence_reference JSON
Do not duplicate blobs; reference attachment IDs.

## Financial quote readiness
Proposals should include estimates:
- estimated_unit_cost
- estimated_unit_price
- estimated_labor_hours
Promoting proposal → WorkOrderItem copies these values forward.

## References
- packages/inspection_work_order_gold_enhancements_package_v1.zip
- references/INSPECTION_WORK_ORDER_INTEGRATION_ASSESSMENT.md
