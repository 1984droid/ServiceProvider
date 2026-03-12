# 00 System Index

This index is written for fast search and “where do I start” clarity.

## Table of contents
1. [System Overview](01_SYSTEM_OVERVIEW.md)
2. [Glossary](02_GLOSSARY.md)
3. [Tenant and Trust Model](03_TENANT_AND_TRUST_MODEL.md)
4. [Asset System](04_ASSET_SYSTEM.md)
5. [Meters and Telemetry](05_METERS_AND_TELEMETRY.md)
6. [Inspection System](06_INSPECTION_SYSTEM.md)
7. [Inspection → Work Orders Integration](07_INSPECTION_TO_WORK_ORDERS.md)
8. [Work Orders](08_WORK_ORDERS.md)
9. [Maintenance](09_MAINTENANCE.md)
10. [Key End-to-End Flows](10_KEY_FLOWS.md)
11. [Inventory and Parts](11_INVENTORY_AND_PARTS.md)
12. [Core Charges](12_CORE_CHARGES.md)
13. [Financial System](13_FINANCIAL_SYSTEM.md)
14. [QuickBooks Online Integration](14_QBO_INTEGRATION.md)
15. [Leasing Compliance Monitoring](15_LEASING_COMPLIANCE.md)
16. [Testing and Quality](16_TESTING_AND_QUALITY.md)
17. [Seed Data and Demo Scenarios](17_SEED_DATA_AND_DEMOS.md)
18. [Operations Runbook](18_OPERATIONS_RUNBOOK.md)
19. [Source Packages](19_SOURCE_PACKAGES.md)

## Key Search Keywords

### Core Architecture
- **"tenant isolation"** → contracts/00_MULTI_TENANT_SECURITY.md
- **"sharing contract"** → docs/03_TENANT_AND_TRUST_MODEL.md

### Asset & Inspection
- **"capabilities vs fields"** → docs/04_ASSET_SYSTEM.md
- **"field templates"** → docs/04_ASSET_SYSTEM.md
- **"Crown Jewel v2"** → docs/06_INSPECTION_SYSTEM.md
- **"idempotent defects"** → docs/06_INSPECTION_SYSTEM.md
- **"inspection templates"** → docs/06_INSPECTION_SYSTEM.md
- **"ANSI A92.2"** → docs/06_INSPECTION_SYSTEM.md
- **"proposal staging"** → docs/07_INSPECTION_TO_WORK_ORDERS.md
- **"unsafe verification"** → docs/07_INSPECTION_TO_WORK_ORDERS.md

### Work Orders & Maintenance
- **"work order vocabulary"** → docs/08_WORK_ORDERS.md
- **"maintenance due instance"** → docs/09_MAINTENANCE.md

### Inventory & Financial
- **"inventory ledger"** → docs/11_INVENTORY_AND_PARTS.md + contracts/02_APPEND_ONLY_LEDGERS.md
- **"special order parts"** → docs/11_INVENTORY_AND_PARTS.md
- **"core deposit"** → docs/12_CORE_CHARGES.md + docs/14_QBO_INTEGRATION.md
- **"QBO idempotency"** → contracts/03_INTEGRATION_IDEMPOTENCY.md
- **"asset cost event"** → docs/13_FINANCIAL_SYSTEM.md + contracts/02_APPEND_ONLY_LEDGERS.md

### Development & Operations
- **"E2E testing"** → docs/16_TESTING_AND_QUALITY.md
- **"Playwright"** → docs/16_TESTING_AND_QUALITY.md
- **"seed data"** → docs/17_SEED_DATA_AND_DEMOS.md

## Source packages included
See `MANIFEST.json` and `docs/19_SOURCE_PACKAGES.md`.
