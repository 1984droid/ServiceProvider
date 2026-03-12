# 03 Tenant and Trust Model

Tags: tenant, permissions, leasing, security, sharing

## Tenant types
At minimum, support these “behavior flags” (not mutually exclusive):
- RepairShop tenant
- LeasingCompany tenant
- Customer/Fleet tenant

## Data ownership rule
Every record that represents operational truth must be tenant-scoped:
- tenant_root (or tenant_id) is required on nearly all models

## Cross-tenant access is EXPLICIT
Cross-tenant access does **not** happen via guessing relationships.

### SharingContract
A SharingContract is the canonical permission grant between:
- provider_tenant (repair shop) and/or leasing_tenant
- customer_tenant (asset operator)

It defines visibility levels (examples):
- work_orders: none | summary | full
- asset_costs: none | summary | full
- provider_identity: boolean
- evidence_visibility: none | thumbnails | full (recommended, if implemented)

## Leasing monitoring
Leasing wants to see:
- compliance state (due/overdue, unsafe, pending verification)
- whether repairs are being kept up
- optionally spend summaries (permissioned)

Leasing does NOT automatically see:
- internal notes
- line-level costs/prices
- all photos/evidence (policy-driven)

## Provider verification
If enabled:
- Tenant.is_verified_provider boolean (manual workflow to start)
- Compliance rules can require verified providers for certain assets/policies

## Redaction rule of thumb
If leasing visibility is “summary”:
- show counts and statuses, not raw detailed evidence/costs.

See contracts/00_MULTI_TENANT_SECURITY.md for enforceable invariants.
