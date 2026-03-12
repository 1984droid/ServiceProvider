# System Documentation — Gold Standard Package (v1)

Generated: 2026-02-08

This is the **canonical documentation bundle** for the platform you've been designing/building:
- Asset system (subtypes, capabilities, field templates)
- Inspections (standards packs, evidence)
- Work orders (structured vocabulary, costing)
- Maintenance (due instances, meter integration)
- Inventory (multi-location, purchasing, special orders, cores)
- Financials (AR/POS/leasing billing) + QuickBooks Online (QBO) sync
- Leasing compliance monitoring (cross-tenant visibility + auditability)
- Testing + seed data

This package is meant to be **searchable**, **organized**, and usable by both:
- your coding agent (implementation roadmap + invariants), and
- future engineers (why decisions were made and how systems interact).

## Quick links
- `docs/00_SYSTEM_INDEX.md` — start here (table of contents + search keywords)
- `docs/10_KEY_FLOWS.md` — end-to-end flows (inspection→WO→invoice, purchasing, cores)
- `contracts/` — non-negotiable invariants (tenant isolation, idempotency, ledgers)
- `diagrams/` — mermaid diagrams you can paste into docs/wiki
- `packages/` — the spec packages generated so far (copied in for convenience)
- `references/` — agent assessments + source notes
- `data/` — vocabulary CSVs (nouns/verbs/locations)

## How to use this
1) Read `docs/00_SYSTEM_INDEX.md`
2) Implement module-by-module (Assets → Work Orders → Inspections → Maintenance → Inventory → Financials → Leasing)
3) Enforce contracts (especially multi-tenant + idempotency) from day one
4) Keep this package versioned. Changes should update:
   - `CHANGELOG.md`
   - relevant contract docs
   - relevant diagrams

## Design posture
- Operational truth lives in your platform.
- Accounting truth lives in QuickBooks Online.
- Safety/compliance truth lives in inspections + verification + immutable audit trails.

