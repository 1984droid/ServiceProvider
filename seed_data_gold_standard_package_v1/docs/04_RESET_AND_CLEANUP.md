# 04 Reset & Cleanup

## Why reset matters
Seed data should be reloadable without hand-cleaning the database.

Recommended approach:
- create objects with a predictable slug/prefix (e.g. demo_)
- delete by tenant_root for the demo tenants

## Reset strategies
A) Hard reset (dev only):
- delete demo tenants and all dependent objects (cascade)
- re-run seed_load

B) Soft reset:
- keep tenants and users
- delete transactional records: work orders, invoices, inventory txns, inspections
- re-run seed_load with --soft flag

See scripts/seed_reset.py for a starting point.
