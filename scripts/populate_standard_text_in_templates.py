#!/usr/bin/env python
"""
Populate standard_text objects in ANSI template files.

This script:
1. Loads standard_text.json
2. For each template, finds steps with standard_reference
3. Adds standard_text objects with matching section/excerpt
"""

import json
import re
from pathlib import Path

def extract_section_from_reference(standard_reference: str) -> str:
    """Extract section number from standard reference string.

    Examples:
        "ANSI A92.2-2021 Section 8.2.3" -> "8.2.3"
        "ANSI A92.2-2021 Section 8.2.3(1)" -> "8.2.3(1)"
        "ANSI A92.2-2021 Sections 5.6.3, 7.11.2, 8.3.2" -> "Sections 5.6.3, 7.11.2, 8.3.2"
    """
    # Match "Section" or "Sections" followed by section number(s)
    match = re.search(r'Sections?\s+([\d\.\(\),\s&]+)', standard_reference)
    if match:
        return match.group(1).strip()
    return ""

def find_matching_excerpt(section: str, standard_text_data: dict) -> dict:
    """Find matching excerpt from standard_text.json.

    Returns dict with section/excerpt or None if no match.
    """
    common_excerpts = standard_text_data.get('common_excerpts', {})

    # Try exact match first
    for key, excerpt_data in common_excerpts.items():
        if excerpt_data['section'] == section:
            return {
                'section': excerpt_data['section'],
                'excerpt': excerpt_data['excerpt'],
                'show_full_section': False
            }

    # Try partial match (e.g., "8.2.3" matches "8.2.3(1)")
    section_base = section.split('(')[0]
    for key, excerpt_data in common_excerpts.items():
        excerpt_section_base = excerpt_data['section'].split('(')[0]
        if excerpt_section_base == section_base:
            return {
                'section': excerpt_data['section'],
                'excerpt': excerpt_data['excerpt'],
                'show_full_section': False
            }

    return None

def populate_template(template_path: Path, standard_text_data: dict, dry_run: bool = False):
    """Populate standard_text objects in a template file."""
    print(f"\nProcessing: {template_path.name}")

    with open(template_path, 'r', encoding='utf-8') as f:
        template_data = json.load(f)

    steps = template_data.get('procedure', {}).get('steps', [])
    modified_count = 0

    for step in steps:
        # Skip if already has standard_text
        if 'standard_text' in step and step['standard_text']:
            continue

        # Skip if no standard_reference
        if 'standard_reference' not in step or not step['standard_reference']:
            continue

        standard_reference = step['standard_reference']
        section = extract_section_from_reference(standard_reference)

        if not section:
            print(f"  [WARN] Could not extract section from: {standard_reference}")
            continue

        # Find matching excerpt
        standard_text_obj = find_matching_excerpt(section, standard_text_data)

        if standard_text_obj:
            step['standard_text'] = standard_text_obj
            modified_count += 1
            print(f"  [OK] {step.get('step_key', '???')}: Added standard_text for section {standard_text_obj['section']}")
        else:
            print(f"  [WARN] {step.get('step_key', '???')}: No excerpt found for section {section}")

    if modified_count > 0 and not dry_run:
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
        print(f"  [SAVED] {modified_count} changes to {template_path.name}")
    elif dry_run:
        print(f"  [DRY RUN] Would save {modified_count} changes")
    else:
        print(f"  [INFO] No changes needed")

    return modified_count

def main():
    # Load standard_text.json
    standard_text_path = Path('static/inspection_references/ansi_a92_2_2021/standard_text.json')
    print(f"Loading: {standard_text_path}")

    with open(standard_text_path, 'r', encoding='utf-8') as f:
        standard_text_data = json.load(f)

    print(f"Found {len(standard_text_data['common_excerpts'])} common excerpts")

    # Process all ANSI templates
    templates_dir = Path('apps/inspections/templates/inspection_templates/ansi_a92_2_2021')
    template_files = list(templates_dir.glob('*.json'))

    print(f"\nFound {len(template_files)} template files")

    total_modified = 0
    for template_path in sorted(template_files):
        count = populate_template(template_path, standard_text_data, dry_run=False)
        total_modified += count

    print(f"\n" + "="*60)
    print(f"[COMPLETE] Modified {total_modified} steps across {len(template_files)} templates")
    print("="*60)

if __name__ == '__main__':
    main()
