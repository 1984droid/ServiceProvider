# 04 Asset System

Tags: assets, subtypes, capabilities, field_templates, vin, real_estate

## Why this system exists
Everything else depends on assets:
- inspections, maintenance, compliance, work orders, inventory consumption, leasing billing.

Goal: a **clean, robust, typed asset system** with minimal free-text.

## Asset core vs capabilities
### Core fields (recommended hard columns)
- name / display name
- identifier (unit number)
- status flags (is_active)
- organizational ownership (owned_by_organization_id)
- optional standardized identifiers:
  - vin (vehicles)
  - serial_number (equipment)
  - plate, registration state (optional)

### Capabilities (typed dynamic properties)
Use capabilities for subtype-specific attributes:
- real estate: parcel number, address
- vehicle: axle config, fuel type
- aerial device: boom length, dielectric rating, etc.

Capabilities must be:
- typed (string/number/boolean/date/enum)
- validated (schema)
- searchable via indexed JSON queries OR extracted columns for high-value fields

## Asset subtypes
Subtype keys are hierarchical:
- fleet.tractor.sleeper
- fleet.trailer.dryvan
- aerial_device.boom_truck
- real_estate.property

## Field registry + templates
Use:
- field_registry.json: canonical field definitions
- field_templates.json: reusable UI field groups
- subtype_field_template_assignments.json: which templates apply to each subtype

Derived artifact:
- resolved_subtype_field_maps.json should be generated (not hand-edited).

## VIN profiles
Store full VIN decode response for audit/reference.
Use vin_profile_field_policy.json to control:
- what is displayed
- what is searchable

## Real estate example (no model/serial)
Real estate subtypes use:
- parcel_id / county parcel number
- address
- lease-related metadata (if needed)
No VIN/serial required.

## References
See embedded package:
- packages/asset_templates_v2_3_field_mapping_package.zip
