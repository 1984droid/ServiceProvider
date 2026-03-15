#!/usr/bin/env python3
"""
Add defect_photos field to all visual inspection steps in inspection templates.

This script adds a PHOTO field that is:
- Required when any field in the step = FAIL, EXCESSIVE, REQUIRES_REPLACEMENT, SERVICE_REQUIRED, UNSAFE_OUT_OF_SERVICE
- Suggested (warning) when any field = MODERATE, MINOR
- Not shown for clean results (PASS, SAFE, NONE, etc.)
"""

import json
import sys
from pathlib import Path

# Navigate to project root
script_dir = Path(__file__).parent
project_root = script_dir.parent
templates_dir = project_root / 'apps' / 'inspections' / 'templates' / 'inspection_templates' / 'ansi_a92_2_2021'

def add_photo_field_to_step(step):
    """Add defect_photos field to a step if it's a visual inspection."""

    if step.get('type') != 'VISUAL_INSPECTION':
        return step

    # Check if photo field already exists
    fields = step.get('fields', [])
    has_photo_field = any(f.get('field_id') == 'defect_photos' for f in fields)

    if has_photo_field:
        print(f"  [OK] {step['step_key']}: Already has defect_photos field")
        return step

    # Define the photo field
    photo_field = {
        "field_id": "defect_photos",
        "label": "Defect Photos",
        "type": "PHOTO",
        "required": False,
        "help_text": "Upload photo(s) of any defects, damage, or wear found. Required for FAIL conditions and excessive wear. Strongly recommended for all issues.",
        "conditionally_required_if": {
            "any_field_in": ["FAIL", "EXCESSIVE", "REQUIRES_REPLACEMENT", "SERVICE_REQUIRED", "UNSAFE_OUT_OF_SERVICE"],
            "description": "Photos required when defects found"
        },
        "conditionally_suggested_if": {
            "any_field_in": ["MODERATE", "MINOR"],
            "description": "Photos strongly recommended for documentation"
        }
    }

    # Add photo field at the end of fields array
    fields.append(photo_field)
    step['fields'] = fields

    print(f"  [OK] {step['step_key']}: Added defect_photos field ({len(fields)} total fields)")

    return step

def process_template(template_path):
    """Process a single template file."""

    print(f"\nProcessing: {template_path.name}")
    print("=" * 60)

    # Load template
    with open(template_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get steps
    steps = data.get('procedure', {}).get('steps', [])

    if not steps:
        print("  ⚠ No steps found in template")
        return

    # Count visual inspection steps
    visual_steps = [s for s in steps if s.get('type') == 'VISUAL_INSPECTION']
    print(f"\nFound {len(visual_steps)} visual inspection steps out of {len(steps)} total steps")
    print()

    # Update each step
    updated_count = 0
    for step in steps:
        original_fields_count = len(step.get('fields', []))
        step = add_photo_field_to_step(step)
        new_fields_count = len(step.get('fields', []))

        if new_fields_count > original_fields_count:
            updated_count += 1

    # Save updated template
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Updated {updated_count} steps in {template_path.name}")
    print(f"[OK] Saved to {template_path}")

def main():
    """Main entry point."""

    print("=" * 60)
    print("Adding defect_photos fields to inspection templates")
    print("=" * 60)

    # Process both templates
    templates = [
        templates_dir / 'periodic_inspection.json',
        templates_dir / 'frequent_inspection.json',
    ]

    for template_path in templates:
        if not template_path.exists():
            print(f"\n⚠ Template not found: {template_path}")
            continue

        process_template(template_path)

    print("\n" + "=" * 60)
    print("[OK] All templates updated successfully")
    print("=" * 60)

if __name__ == '__main__':
    main()
