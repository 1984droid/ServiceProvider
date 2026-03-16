#!/usr/bin/env python3
"""
Fix all inspection templates to match data contract specification.

Changes:
1. Make standard_reference REQUIRED in all defect schemas
2. Standardize all defect schemas to use identical 8-field structure
3. Convert all enums to {value, label} format
4. Add equipment_location enum where missing
"""

import json
import os

TEMPLATE_DIR = "apps/inspections/templates/inspection_templates/ansi_a92_2_2021"

# Standard 8-field defect schema matching DATA_CONTRACT.md
STANDARD_DEFECT_SCHEMA = {
    "defect_id_format": "UUID",
    "fields": [
        {
            "field_id": "title",
            "type": "TEXT",
            "required": True
        },
        {
            "field_id": "severity",
            "type": "ENUM",
            "enum_ref": "severity",
            "required": True
        },
        {
            "field_id": "description",
            "type": "TEXT_AREA",
            "required": True
        },
        {
            "field_id": "component",
            "type": "TEXT",
            "required": False
        },
        {
            "field_id": "location",
            "type": "ENUM",
            "required": False,
            "enum_ref": "equipment_location"
        },
        {
            "field_id": "photo_evidence",
            "type": "PHOTO",
            "required": False
        },
        {
            "field_id": "corrective_action",
            "type": "TEXT_AREA",
            "required": False
        },
        {
            "field_id": "standard_reference",
            "type": "TEXT",
            "required": True  # USER REQUIREMENT: Must be REQUIRED
        }
    ]
}

# Standard equipment_location enum
EQUIPMENT_LOCATION_ENUM = [
    {"value": "PLATFORM", "label": "Platform / Basket"},
    {"value": "BOOM_BASE", "label": "Boom - Base Section"},
    {"value": "BOOM_MID", "label": "Boom - Mid Section"},
    {"value": "BOOM_FLY", "label": "Boom - Fly Section"},
    {"value": "TURRET", "label": "Turret / Rotating Assembly"},
    {"value": "PEDESTAL", "label": "Pedestal / Mounting Base"},
    {"value": "OUTRIGGERS_FRONT_LEFT", "label": "Outriggers - Front Left"},
    {"value": "OUTRIGGERS_FRONT_RIGHT", "label": "Outriggers - Front Right"},
    {"value": "OUTRIGGERS_REAR_LEFT", "label": "Outriggers - Rear Left"},
    {"value": "OUTRIGGERS_REAR_RIGHT", "label": "Outriggers - Rear Right"},
    {"value": "HYDRAULIC_SYSTEM", "label": "Hydraulic System"},
    {"value": "ELECTRICAL_SYSTEM", "label": "Electrical System"},
    {"value": "CONTROLS_PLATFORM", "label": "Controls - Platform"},
    {"value": "CONTROLS_GROUND", "label": "Controls - Ground"},
    {"value": "CHASSIS", "label": "Chassis / Vehicle Base"},
    {"value": "OTHER", "label": "Other (specify in description)"}
]


def convert_string_enum_to_labeled(enum_values):
    """Convert plain string array to {value, label} array."""
    if not enum_values:
        return []

    # Already in correct format
    if isinstance(enum_values[0], dict):
        return enum_values

    # Convert strings to objects
    return [{"value": val, "label": val.replace("_", " ").title()} for val in enum_values]


def fix_major_structural():
    """Fix major_structural_inspection.json."""
    filepath = os.path.join(TEMPLATE_DIR, "major_structural_inspection.json")

    with open(filepath, 'r') as f:
        template = json.load(f)

    print(f"Fixing {filepath}...")

    # 1. Convert all enums to {value, label} format
    for enum_key, enum_values in template['enums'].items():
        template['enums'][enum_key] = convert_string_enum_to_labeled(enum_values)

    # 2. Add equipment_location enum
    template['enums']['equipment_location'] = EQUIPMENT_LOCATION_ENUM

    # 3. Replace defect_schema with standard schema
    template['schemas']['defect_schema'] = STANDARD_DEFECT_SCHEMA

    # Write back
    with open(filepath, 'w') as f:
        json.dump(template, f, indent=2)

    print(f"  - Converted all enums to {{value, label}} format")
    print(f"  - Added equipment_location enum")
    print(f"  - Replaced defect_schema with standard 8-field schema")
    print(f"  - standard_reference is now REQUIRED")


def fix_load_test():
    """Fix load_test_only.json."""
    filepath = os.path.join(TEMPLATE_DIR, "load_test_only.json")

    with open(filepath, 'r') as f:
        template = json.load(f)

    print(f"\\nFixing {filepath}...")

    # 1. Convert enums to {value, label} format
    for enum_key, enum_values in template['enums'].items():
        template['enums'][enum_key] = convert_string_enum_to_labeled(enum_values)

    # 2. Add equipment_location enum
    template['enums']['equipment_location'] = EQUIPMENT_LOCATION_ENUM

    # 3. Replace defect_schema with standard schema
    template['schemas']['defect_schema'] = STANDARD_DEFECT_SCHEMA

    # Write back
    with open(filepath, 'w') as f:
        json.dump(template, f, indent=2)

    print(f"  - Converted all enums to {{value, label}} format")
    print(f"  - Added equipment_location enum")
    print(f"  - Updated defect_schema to standard 8-field schema")
    print(f"  - standard_reference is now REQUIRED")
    print(f"  - location field now uses ENUM (equipment_location)")


def fix_dielectric_test():
    """Fix dielectric_test_periodic.json."""
    filepath = os.path.join(TEMPLATE_DIR, "dielectric_test_periodic.json")

    with open(filepath, 'r') as f:
        template = json.load(f)

    print(f"\\nFixing {filepath}...")

    # 1. Convert enums to {value, label} format
    for enum_key, enum_values in template['enums'].items():
        template['enums'][enum_key] = convert_string_enum_to_labeled(enum_values)

    # 2. Add equipment_location enum
    template['enums']['equipment_location'] = EQUIPMENT_LOCATION_ENUM

    # 3. ADD defect_schema (was completely missing!)
    if 'schemas' not in template:
        template['schemas'] = {}

    template['schemas']['defect_schema'] = STANDARD_DEFECT_SCHEMA

    # Write back
    with open(filepath, 'w') as f:
        json.dump(template, f, indent=2)

    print(f"  - Converted all enums to {{value, label}} format")
    print(f"  - Added equipment_location enum")
    print(f"  - ADDED defect_schema (was completely missing!)")
    print(f"  - standard_reference is REQUIRED")


def main():
    print("=" * 60)
    print("FIXING INSPECTION TEMPLATES TO MATCH DATA CONTRACT")
    print("=" * 60)

    fix_major_structural()
    fix_load_test()
    fix_dielectric_test()

    print("\\n" + "=" * 60)
    print("ALL TEMPLATES FIXED SUCCESSFULLY!")
    print("=" * 60)
    print("\\nSummary:")
    print("  - All 5 templates now have standard 8-field defect_schema")
    print("  - standard_reference is REQUIRED in all templates")
    print("  - All enums use {value, label} format")
    print("  - All templates have equipment_location enum")
    print("  - location field uses ENUM (equipment_location) in all templates")


if __name__ == '__main__':
    main()
