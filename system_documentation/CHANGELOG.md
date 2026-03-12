# Changelog

## v2 — 2026-02-09

**MAJOR UPDATE**: Comprehensive documentation cleanup and consolidation.

### Added
- **CRM System Spec Packages** (4 packages, NOT IMPLEMENTED):
  - crm_gold_standard_package_v1 - Domain model, API contract, workflows
  - crm_dashboards_spec_pack_v1 - Manager/Rep dashboards with KPIs
  - crm_signals_implementation_pack_v1 - Event bus and task generation
  - crm_tenant_policy_admin_ui_spec_pack_v1 - Policy configuration UI

### Changed
- **Enhanced 00_SYSTEM_INDEX.md** with expanded search keywords
- **Enhanced 06_INSPECTION_SYSTEM.md** with Crown Jewel v2 implementation status (COMPLETE)
- **Enhanced 08_WORK_ORDERS.md** with v2.2 implementation status and vocabulary
- **Enhanced 11_INVENTORY_AND_PARTS.md** with implementation status and testing
- **Enhanced 13_FINANCIAL_SYSTEM.md** with Phase F1/F3 status
- **Enhanced 16_TESTING_AND_QUALITY.md** with Playwright E2E testing guide
- **Enhanced 17_SEED_DATA_AND_DEMOS.md** with comprehensive seeding instructions
- Consolidated ~50 scattered implementation docs into system_documentation/
- Organized search keywords by category (Core, Asset, Inventory, CRM, Operations)

### Removed
- Legacy asset_templates v2_1 and v2_2 (kept only v2_3)
- Duplicate/temporary documentation files (~50 files)
- DEMO_RUNBOOK.md (obsolete)
- docs/ folder contents (merged into system_documentation/)

### Consolidated Files (merged and deleted from root)
- Crown Jewel v2 docs (5 files) → 06_INSPECTION_SYSTEM.md
- E2E testing docs (4 files) → 16_TESTING_AND_QUALITY.md
- Financial docs (2 files) → 13_FINANCIAL_SYSTEM.md
- Inventory docs (2 files) → 11_INVENTORY_AND_PARTS.md
- Work order docs (2 files) → 08_WORK_ORDERS.md
- Seeding docs (2 files) → 17_SEED_DATA_AND_DEMOS.md

### Result
- **Before**: 200+ scattered .md files across project
- **After**: 19 comprehensive system docs + 4 contracts + 13 spec packages
- **Single source of truth**: system_documentation/ folder
- **Enhanced searchability**: Keyword mappings in 00_SYSTEM_INDEX.md
- **Clear status tracking**: Every system shows COMPLETE, IN PROGRESS, or PLANNED

---

## v1 — 2026-02-08
Initial consolidated documentation package assembled from:
- Asset template system (v2.3 field mapping packages)
- Work orders gold standard package
- Leasing compliance MVP package
- Financial system (QBO-ready) package
- Inspection ↔ work order gold enhancements package
- Inventory management gold standard package + QBO mapping appendix
- Gold standard automated test suite package
- Seed data package
- Reference assessments and strategy docs

