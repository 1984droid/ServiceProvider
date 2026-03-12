# Multi-tenant Security Contract

This document defines non-negotiable invariants.

## C-01 — Tenant scoping
Every operational record MUST have tenant_root (or tenant_id).

## C-02 — Cross-tenant relationships forbidden by default
Foreign keys must not link across tenants unless explicitly part of the trust model (SharingContract).

Examples that must be prevented:
- WorkOrderItem referencing a Defect from another tenant
- InventoryTransaction referencing a WorkOrder from another tenant
- Invoice referencing a CustomerAccount from another tenant

## C-03 — SharingContract is required for leasing visibility
Without a SharingContract:
- leasing tenant sees "unknown" or nothing
- no indirect access via shared assets is allowed

## C-04 — Redaction is enforced server-side
If permission is summary:
- do not return detailed evidence blobs, costs, or internal notes.

## Tests
The test suite must include:
- explicit cross-tenant access attempts returning 403 or empty results.
