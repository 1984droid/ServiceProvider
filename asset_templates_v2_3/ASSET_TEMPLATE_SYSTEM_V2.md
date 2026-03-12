# Asset Template System v2 (Typed, Searchable, Audit-Ready)

Generated: 2026-02-07

This package upgrades the existing hierarchical subtype + capability system into a **more complete, safety-auditing-ready asset template system**.

It is designed to:
- minimize free text
- provide consistent **search and filter facets**
- drive **scheduled inspections and maintenance**
- support assets that do **not** have VIN/serial/model (ex: real estate)

---

## 1. Core Concepts

### 1.1 AssetSubtype (hierarchy)
Each asset has an `asset_subtype_key` (dot-notated), like:
- `fleet.tractor.sleeper`
- `real_estate.parcel`
- `tools.calibrated.torque_wrench`

Subtypes inherit defaults and capability packs from ancestors.

### 1.2 Asset Fields vs Capabilities
This system supports **two kinds** of properties:

**A) Asset Fields (hard fields)**
Defined in `asset_field_definitions.json`.

These are the "native" columns on the Asset model (or equivalent), such as:
- `identifier`
- `display_name`
- `vin`
- `serial_number`

**Important:** Not every subtype uses every field.  
Each subtype declares which Asset fields are:
- visible in UI
- required for validation

Example: Real estate subtypes do **not** show VIN/serial/model.

**B) Capabilities (typed dynamic properties)**
Defined in `capability_definitions.json`.

Capabilities are:
- strongly typed (`enum`, `bool`, `int`, `decimal`, `date`, `ref`, `string`)
- optionally filterable/searchable
- grouped for clean UI rendering

---

## 2. Capability Definition Schema (recommended)

Each capability has:
- `key`: snake_case unique key (stable)
- `type`: one of `bool|int|decimal|string|date|enum|ref`
- `enum`: list of allowed values (for enum)
- `ref_table`: lookup table name (for ref)
- `unit` + numeric validation where applicable
- `filterable`: whether it should appear as a filter facet
- `searchable`: whether it participates in search indexing
- `group`: UI section grouping

---

## 3. Capability Packs (mixins)

`capability_packs.json` defines reusable groups of capabilities, such as:
- `core.universal`
- `maintenance.time_metered`
- `real_estate.property`
- `tools.calibrated`

Subtypes attach packs so you don't have to hand-pick 50 fields per subtype.

---

## 4. Search & Filtering Guidance

### 4.1 Strong filters (recommended facets)
- All enums and booleans (status, class, type, etc.)
- Numeric fields (miles/hours, capacity, dimensions) via range filters
- Key identifiers (identifier, serial_number, vin, parcel_number, hostname)

### 4.2 Avoid free text
Allow strings only when:
- they are identifiers with patterns (VIN, MAC, IMEI)
- they are short constrained labels (site_detail <= 60)
- they are addresses/legal descriptions (real estate)

---

## 5. Inspections and Maintenance

This package includes:
- `inspection_checklists.json` (starter checklists)
- `inspection_programs.json` (schedule + checklist mapping)
- `maintenance_task_catalog.json` (atomic tasks)
- `maintenance_programs.json` (schedules + tasks)
- `subtype_program_defaults.json` (defaults per subtype)

Your application can:
1) assign default programs from subtype
2) allow asset-level overrides (optional)
3) compute due dates/meters
4) create scheduled work/inspection instances

---

## 6. Import Order

Recommended import order:
1) `asset_field_definitions.json`
2) `capability_definitions.json`
3) `capability_packs.json`
4) `maintenance_task_catalog.json`
5) `maintenance_programs.json`
6) `inspection_checklists.json`
7) `inspection_programs.json`
8) `asset_subtypes.json`
9) `subtype_program_defaults.json`

---

## 7. Notes on Compatibility with your v1 doc

Your existing v1 doc hard-codes VIN/serial in the Asset model and uses capabilities for the rest.
This v2 system is compatible with that approach **and** adds:
- subtype-specific field visibility/requirements
- capability packs
- real-estate-first modeling
- starter inspection + maintenance catalogs



---

## 8. Standards-Based Inspection Templates (AF_INSPECTION_TEMPLATE)

This package supports importing and running **standards-based modular inspection templates**.

Included pack:
- `inspection_template_pack_manifest.json`
- `inspection_templates/ansi_a92_2_2021/*.json`

### Why keep templates as raw JSON?
These templates contain:
- step types (VISUAL_CHECK, MEASUREMENT, DEFECT_CAPTURE, etc.)
- field-level validation and required steps
- rules that auto-generate defects/findings
- evidence policies and hashing policy for audit integrity

### How templates connect to assets
AF templates rely on an `asset.capabilities` *tag list* for applicability/visibility.
Use `inspection_asset_capability_tag_map.json` to derive those tags from your typed capabilities.

### How templates connect to programs
`inspection_programs.json` includes an `engine: "AF_INSPECTION_TEMPLATE"` program that composes the A92.2 modules and applies template applicability to include/exclude modules per asset.



---

## 9. Work Order Vocabulary (Nouns / Verbs / Locations)

To keep work orders **structured, searchable, and filterable**, this package includes a controlled vocabulary:

Folder: `work_order_vocabulary/`

Files:
- `noun_categories.json` – 21 categories (Brakes & Air, Equipment & Hydraulics, etc.)
- `nouns.json` – 682 nouns (parts/components + service/procedure nouns + fees/supplies)
- `verbs.json` – 89 verbs (inspect, diagnose, torque, adjust, replace, repair, etc.)
- `location_categories.json` – 9 location category groups
- `service_locations.json` – 69 standardized location codes (boom, bucket, cab interior, etc.)
- `work_order_line_schema.json` – reference schema for a structured line item

### 9.1 Key design: nouns are the “things”, verbs are the “actions”
A Work Order Line should reference:
- `verb_key` (what action is being performed)
- `noun_key` (what object/system/component/service noun)
- `location_code` (where on the asset)

Optional: add qualifiers later (side/position) as structured fields.

### 9.2 Stable keys
For nouns, this package generates:
- `noun_key = <category_key>.<slug(item)>`

Example:
- `equipment_and_hydraulics.aerial_boom`
- `inspections_and_preventive_maintenance.dielectric_testing`

### 9.3 Parts Department classification
For parts/inventory, store a reference to `noun_key` on each part record.
This enables:
- reporting (“top parts by noun”, “cost by system”)
- intelligent defaults for service writer lines

---

## 10. Inspection → Work Order Integration (Seeded)

Folder: `work_order_integration/`

Files:
- `inspection_defect_catalog_ansi_a92_2_2021.json` – extracted defect rules from ANSI A92.2 templates
- `inspection_defect_to_work_order_seed_map_ansi_a92_2_2021.json` – starter mapping from defects to recommended Work Order Lines (verb+noun+location)

### 10.1 Intended flow
1) Run an AF inspection template program (ex: A92.2 periodic)
2) Template rules generate defects/findings (with severity + standard references)
3) Use the seed map to propose one or more structured Work Order Lines
4) Service writer reviews/approves (optional)
5) Work order becomes the execution vehicle for corrective action

### 10.2 Refinement strategy
The seed map is intentionally conservative and module-based. Over time, refine by:
- `template_key + step_key` granularity
- adding multiple line suggestions per defect (labor + parts)
- mapping severity to priority / OOS policy
- mapping certain defects to specific nouns (ex: decals → `aerial_placard_decal`)



---

## 9. Subtype Field Templates (Comprehensive Field Mapping)

This package includes a comprehensive, repair-focused field mapping system based on the following principles:

- Every subtype has an explicit list of fields to capture (no guessing).
- Templates support nested fields:
  - `vin_profile.*` (VIN decode profile, repair-relevant only)
  - `capability.*` (typed dynamic properties)
  - `asset.*` (hard fields on the asset model)
- Not all assets have VIN/serial/model; subtype templates declare what applies (ex: real estate requires parcel/address).
- Templates are composable (like capability packs) to avoid duplication.

Files:
- `field_registry.json` — canonical field metadata + aliases
- `field_templates.json` — reusable field templates (sections, required fields, conditions)
- `subtype_field_template_assignments.json` — subtype → templates
- `resolved_subtype_field_maps.json` — expanded per-subtype field lists (roadmap artifact)
- `vin_profile_field_policy.json` — show/do-not-show policy for VIN profile fields

