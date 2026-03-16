"""
Add Standard References to auto_defect_on Rules

Maps inspection steps to ANSI A92.2-2021 sections and adds
standard_reference to all auto_defect_on defect objects.

Usage:
    python scripts/add_standard_references_to_templates.py

Updates templates in place with proper standard references.
"""

import json
import os
from pathlib import Path

# ANSI A92.2-2021 Section Mappings
# Based on Section 8.2 - Inspection and Testing Classifications

STANDARD_REFERENCE_MAP = {
    # ========================================================================
    # FREQUENT INSPECTION (Section 8.2.3)
    # ========================================================================
    'frequent_inspection': {
        'operating_controls_test': 'ANSI A92.2-2021 Section 8.2.3(2)',
        'emergency_controls_test': 'ANSI A92.2-2021 Section 8.2.3(2) & (3)',
        'safety_devices_test': 'ANSI A92.2-2021 Section 8.2.3(3)',
        'visual_structural_inspection': 'ANSI A92.2-2021 Section 8.2.3(1)',
        'visual_hydraulic_inspection': 'ANSI A92.2-2021 Section 8.2.3(6)',
        'visual_electrical_inspection': 'ANSI A92.2-2021 Section 8.2.3(7)',
        'markings_placards': 'ANSI A92.2-2021 Section 8.2.3(5)',
    },

    # ========================================================================
    # PERIODIC INSPECTION (Section 8.2.4)
    # ========================================================================
    'periodic_inspection': {
        'structural_components': 'ANSI A92.2-2021 Section 8.2.4(1)',
        'welds_inspection': 'ANSI A92.2-2021 Section 8.2.4(14)',
        'bolts_fasteners': 'ANSI A92.2-2021 Section 8.2.4(13)',
        'hydraulic_system': 'ANSI A92.2-2021 Section 8.2.4(4)-(6)',
        'electrical_system': 'ANSI A92.2-2021 Section 8.2.4(11)',
        'operating_controls': 'ANSI A92.2-2021 Section 8.2.4(12)',
        'emergency_controls': 'ANSI A92.2-2021 Section 8.2.4(12)',
        'safety_devices': 'ANSI A92.2-2021 Section 8.2.4(12)',
        'markings_placards_manuals': 'ANSI A92.2-2021 Section 8.2.4(15)',
    },

    # ========================================================================
    # MAJOR STRUCTURAL INSPECTION (Section 8.2.5)
    # ========================================================================
    'major_structural_inspection': {
        'work_documentation_review': 'ANSI A92.2-2021 Section 8.2.5',
        'detailed_structural_inspection': 'ANSI A92.2-2021 Section 8.2.5(2)',
        'weld_inspection_detailed': 'ANSI A92.2-2021 Section 8.2.4(14) & 8.2.5(2)',
        'bolts_pins_fasteners_detailed': 'ANSI A92.2-2021 Section 8.2.4(2) & (13)',
        'hydraulic_system_detailed': 'ANSI A92.2-2021 Section 8.2.4(3)-(9)',
        'functional_testing': 'ANSI A92.2-2021 Section 8.2.4(12)',
        'markings_and_documentation': 'ANSI A92.2-2021 Section 8.2.4(15)',
    },

    # ========================================================================
    # LOAD TEST (Section 4.5.1 & 8.2.5)
    # ========================================================================
    'load_test_only': {
        'boom_raise_test': 'ANSI A92.2-2021 Section 4.5.1 & 8.2.5(1)',
        'boom_extend_test': 'ANSI A92.2-2021 Section 4.5.1 & 8.2.5(1)',
        'boom_rotation_test': 'ANSI A92.2-2021 Section 4.5.1 & 8.2.5(1)',
        'boom_lowering_test': 'ANSI A92.2-2021 Section 4.5.1 & 8.2.5(1)',
        'post_test_inspection': 'ANSI A92.2-2021 Section 8.2.5(2)',
    },

    # ========================================================================
    # DIELECTRIC TEST (Section 5.4.3, Tables 2-3)
    # ========================================================================
    'dielectric_test_periodic': {
        'pre_test_visual_inspection': 'ANSI A92.2-2021 Section 5.4.3.1(1)-(4) & 8.2.4(16)',
    },
}


def add_standard_references_to_template(template_path: Path, template_key: str) -> bool:
    """
    Add standard_reference to auto_defect_on rules in a template.

    Args:
        template_path: Path to template JSON file
        template_key: Template identifier (e.g., 'periodic_inspection')

    Returns:
        True if changes were made, False otherwise
    """
    # Load template
    with open(template_path, 'r', encoding='utf-8') as f:
        template = json.load(f)

    # Get reference map for this template
    if template_key not in STANDARD_REFERENCE_MAP:
        print(f"  [WARN] No reference mapping for template: {template_key}")
        return False

    reference_map = STANDARD_REFERENCE_MAP[template_key]

    # Track changes
    changes_made = False
    steps_updated = []

    # Process each step
    steps = template.get('procedure', {}).get('steps', [])
    for step in steps:
        step_key = step.get('step_key')
        auto_defect_rules = step.get('auto_defect_on', [])

        if not auto_defect_rules:
            continue

        # Get standard reference for this step
        standard_ref = reference_map.get(step_key)
        if not standard_ref:
            print(f"  [WARN] No reference mapping for step: {step_key}")
            continue

        # Add standard_reference to each auto_defect_on rule
        for rule in auto_defect_rules:
            defect = rule.get('defect', {})

            # Check if already has standard_reference
            if 'standard_reference' in defect:
                continue

            # Add standard_reference
            defect['standard_reference'] = standard_ref
            changes_made = True

        if changes_made:
            steps_updated.append(step_key)

    # Save if changes were made
    if changes_made:
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        print(f"  [OK] Updated {len(steps_updated)} steps: {', '.join(steps_updated)}")
        return True
    else:
        print(f"  [INFO] No changes needed (all rules already have references)")
        return False


def main():
    """Process all templates and add standard references."""
    print("=" * 80)
    print("Adding Standard References to auto_defect_on Rules")
    print("=" * 80)
    print()

    # Template directory
    template_dir = Path('apps/inspections/templates/inspection_templates/ansi_a92_2_2021')

    if not template_dir.exists():
        print(f"❌ Template directory not found: {template_dir}")
        return

    # Template files to process
    templates_to_process = {
        'frequent_inspection.json': 'frequent_inspection',
        'periodic_inspection.json': 'periodic_inspection',
        'major_structural_inspection.json': 'major_structural_inspection',
        'load_test_only.json': 'load_test_only',
        'dielectric_test_periodic.json': 'dielectric_test_periodic',
    }

    total_updated = 0

    for filename, template_key in templates_to_process.items():
        template_path = template_dir / filename

        if not template_path.exists():
            print(f"[WARN] Template not found: {filename}")
            continue

        print(f"Processing: {filename}")

        if add_standard_references_to_template(template_path, template_key):
            total_updated += 1

        print()

    print("=" * 80)
    print(f"[COMPLETE] Updated {total_updated} of {len(templates_to_process)} templates")
    print("=" * 80)


if __name__ == '__main__':
    main()
