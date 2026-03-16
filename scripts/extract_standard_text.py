"""
Extract Standard Text from ANSI A92.2-2021 DOCX

Extracts section text organized by section numbers for use in
inspection templates and inspector reference.

Source: ANSI+SAIA+A92.2-2021.docx
Output: static/inspection_references/ansi_a92_2_2021/standard_text.json
"""

import json
import re
from pathlib import Path
from docx import Document


def extract_section_text(doc, section_number, max_paragraphs=100):
    """
    Extract text for a specific section number.

    Args:
        doc: Document object
        section_number: Section to find (e.g., "8.2.3", "5.4.2")
        max_paragraphs: Maximum paragraphs to extract

    Returns:
        dict with section title and content
    """
    section_data = {
        "section": section_number,
        "title": "",
        "content": "",
        "items": []
    }

    # Find the section
    found_section = False
    section_paragraphs = []

    for idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()

        # Look for section number at start of line
        if not found_section and section_number in text[:15]:
            found_section = True
            section_data["title"] = text.replace(section_number, "").strip(". ")
            continue

        # Collect paragraphs until next major section
        if found_section:
            # Stop if we hit another section at same level
            # e.g., if looking for 8.2.3, stop at 8.2.4 or 8.3
            parts = section_number.split('.')
            if len(parts) >= 2:
                # Check for next section at same level
                next_section_pattern = None
                if len(parts) == 2:  # e.g., "8.2"
                    next_num = int(parts[1]) + 1
                    next_section_pattern = f"{parts[0]}.{next_num}"
                elif len(parts) == 3:  # e.g., "8.2.3"
                    next_num = int(parts[2]) + 1
                    next_section_pattern = f"{parts[0]}.{parts[1]}.{next_num}"

                if next_section_pattern and next_section_pattern in text[:15]:
                    break

            # Add paragraph
            if text:
                section_paragraphs.append(text)

            # Safety limit
            if len(section_paragraphs) >= max_paragraphs:
                break

    # Process collected paragraphs
    if section_paragraphs:
        # First paragraph is usually the intro
        section_data["content"] = section_paragraphs[0] if section_paragraphs else ""

        # Look for numbered/bulleted items
        for para in section_paragraphs:
            # Match patterns like (1), (2), etc. or bullet points
            if re.match(r'^\(\d+\)', para) or para.startswith('•') or para.startswith('-'):
                section_data["items"].append(para)
            elif len(para) < 200 and not section_data["items"]:
                # Short paragraphs before items list might be part of content
                if section_data["content"]:
                    section_data["content"] += " " + para
                else:
                    section_data["content"] = para

    return section_data


def extract_all_sections(docx_path):
    """Extract all key ANSI sections for inspection reference."""

    print("Extracting standard text from ANSI A92.2-2021 DOCX...\n")

    doc = Document(docx_path)

    standard_text = {
        "standard": "ANSI A92.2-2021",
        "title": "Vehicle-Mounted Elevating and Rotating Aerial Devices",
        "extracted_date": "2026-03-15",
        "sections": {}
    }

    # Key sections for inspections
    sections_to_extract = {
        # Dielectric Testing
        "5.3.2": "Insulating Boom Sections",
        "5.3.3": "Periodic Electrical Test",
        "5.4.2": "Qualification Test Procedures",
        "5.4.3": "Periodic Electrical Test Procedures",
        "5.4.3.1": "Test Procedures for Category A and B",
        "5.4.3.2": "Test Procedures for Category C, D, and E",
        "5.4.3.3": "Test Procedures for Aerial Ladders and Vertical Towers",
        "5.4.3.4": "Test Procedures for Chassis Insulating Systems",
        "5.4.3.5": "Test Procedures for Insulating Liners",
        "5.4.3.6": "Upper Control High Resistance Test",

        # Load Testing
        "4.5.1": "Stability on Level Surface Test",

        # Inspections
        "8.2.2": "Inspection Intervals",
        "8.2.3": "Frequent Inspection",
        "8.2.4": "Periodic Inspection or Test",
        "8.2.5": "Major Structural Inspection",

        # Documentation
        "8.2.6": "Inspection and Test Records",
    }

    print("Extracting sections:\n")

    for section_num, expected_title in sections_to_extract.items():
        print(f"  {section_num}: {expected_title}...", end=" ")

        section_data = extract_section_text(doc, section_num)

        if section_data["content"] or section_data["items"]:
            standard_text["sections"][section_num] = section_data
            print(f"OK ({len(section_data['content'])} chars, {len(section_data['items'])} items)")
        else:
            print("NOT FOUND")

    return standard_text


def create_section_excerpts():
    """
    Create short excerpts for common inspection steps.

    These are meant to be embedded directly in templates.
    """

    excerpts = {
        # Frequent Inspection (8.2.3)
        "structural_visual": {
            "section": "8.2.3(1)",
            "excerpt": "Structural members for deformation, cracks, or corrosion."
        },
        "operating_controls": {
            "section": "8.2.3(2)",
            "excerpt": "Performance test of all boom movements."
        },
        "safety_devices": {
            "section": "8.2.3(3)",
            "excerpt": "Test of all safety devices including interlocks, limit switches, and emergency controls."
        },
        "hydraulic_system": {
            "section": "8.2.3(4)-(6)",
            "excerpt": "Hydraulic system for proper oil level. Hydraulic fittings, hoses, and tubing for evidence of leakage, abnormal deformation, or excessive abrasion."
        },
        "electrical_system": {
            "section": "8.2.3(11)",
            "excerpt": "Electrical systems and components for deterioration or wear."
        },
        "fasteners": {
            "section": "8.2.3(13)",
            "excerpt": "Condition and tightness of bolts and other fasteners in accordance with the manufacturer's recommendation."
        },
        "markings": {
            "section": "8.2.3(15)",
            "excerpt": "Legible and proper identification, operational, and instructional markings."
        },

        # Periodic Inspection (8.2.4)
        "welds": {
            "section": "8.2.4(14)",
            "excerpt": "Welds, as specified by the manufacturer."
        },
        "bolts_detailed": {
            "section": "8.2.4(13)",
            "excerpt": "Condition and tightness of bolts and other fasteners."
        },

        # Dielectric Testing
        "dielectric_qualification": {
            "section": "5.4.2",
            "excerpt": "Qualification test to verify the type and magnitude of line voltage for which the aerial device has been designed."
        },
        "dielectric_periodic": {
            "section": "5.4.3",
            "excerpt": "Each insulating aerial device shall be periodically electrically tested in accordance with Table 2."
        },
        "insulating_liner": {
            "section": "5.4.3.5",
            "excerpt": "Insulating liners shall be tested in accordance with Table 4."
        },
        "upper_control_resistance": {
            "section": "5.4.3.6",
            "excerpt": "Upper controls with high electrical resistance components shall be electrically tested per Table 5."
        },

        # Load Testing
        "load_test": {
            "section": "4.5.1",
            "excerpt": "Stability test with one and one-half times the rated load capacity."
        },
    }

    return excerpts


def main():
    """Main extraction process."""

    docx_path = 'ANSI+SAIA+A92.2-2021.docx'
    output_dir = Path('static/inspection_references/ansi_a92_2_2021')

    print("="*80)
    print("ANSI A92.2-2021 Standard Text Extraction")
    print("="*80)
    print(f"\nSource: {docx_path}")
    print(f"Output: {output_dir}\n")

    # Extract sections
    standard_text = extract_all_sections(docx_path)

    # Add excerpts
    standard_text["common_excerpts"] = create_section_excerpts()

    # Save to JSON
    output_file = output_dir / 'standard_text.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(standard_text, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print("EXTRACTION COMPLETE")
    print("="*80)
    print(f"\nSections extracted: {len(standard_text['sections'])}")
    print(f"Common excerpts: {len(standard_text['common_excerpts'])}")
    print(f"\nOutput file: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024:.1f} KB")

    print("\nStandard text ready for inspection template integration!")
    print("\nNext steps:")
    print("  1. Extend template schema with standard_text_ref field")
    print("  2. Add standard text references to inspection templates")
    print("  3. Implement frontend display (inline excerpts + modal)")
    print("  4. Include in PDF reports for compliance documentation")


if __name__ == '__main__':
    main()
