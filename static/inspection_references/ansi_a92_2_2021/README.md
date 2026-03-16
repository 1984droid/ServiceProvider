# ANSI A92.2-2021 Reference Materials

**Source:** ANSI+SAIA+A92.2-2021.docx
**Standard:** American National Standard for Vehicle-Mounted Elevating and Rotating Aerial Devices
**Extracted:** Figures, Tables, Logos, and Equipment Symbols

---

## Directory Structure

```
ansi_a92_2_2021/
├── figures/          (9 images)  - Technical diagrams from standard
├── tables/           (17 images) - All tables as formatted PNG images
├── logos/            (2 images)  - ANSI and SAIA logos
├── symbols/          (6 images)  - Equipment warning and operational symbols
├── standard_text.json           - Standard text excerpts for templates
└── README.md
```

---

## Figures (9)

Technical diagrams referenced throughout the ANSI A92.2-2021 standard.

### Dielectric Testing
- `figure_1_dielectric_test_cat_ab.jpg` - **Figure 1**: Test setup for Category A/B devices with lower electrode
- `figure_1a_electrode_assembly_details.jpg` - **Figure 1A**: Lower test electrode assembly details
- `figure_2_dielectric_test_cat_cde.png` - **Figure 2**: Test setup for Category C/D/E devices
- `figure_2a_optional_test_config.jpg` - **Figure 2A**: Optional test configuration

### Chassis and Bonding
- `figure_3_chassis_insulating_systems.png` - **Figure 3**: Chassis and insulating systems
- `figure_3a_shunting_arrangement.jpg` - **Figure 3A**: Shunting arrangement for energized line contact
- `figure_5_bonding_arrangements.jpg` - **Figure 5**: Electrical bonding arrangements

### Testing Procedures
- `figure_4_boom_positions_test.jpg` - **Figure 4**: Boom positions during load testing
- `figure_6_upper_control_test.png` - **Figure 6**: Upper control high resistance test setup

---

## Tables (17)

All tables extracted as formatted PNG images for easy reference.

### Design and Qualification Tests
- `table_06.png` - **TABLE 1**: Design/Qualification Test Values (Category A & B with lower electrode)
- `table_07.png` - **TABLE 1**: Design/Qualification Test Values (Category C, D, E without lower electrode)
- `table_08.png` - **TABLE 1**: Design/Qualification Test Values (Insulating Ladders and Towers)

### Periodic Electrical Tests
- `table_02.png` - **TABLE 2**: Periodic Test Values (Category A & B with lower electrode)
- `table_03.png` - **TABLE 2**: Periodic Test Values (Category C, D, E without lower electrode)
- `table_04.png` - **TABLE 2**: Periodic Test Values (Insulating Ladders and Towers)
- `table_05.png` - **TABLE 2**: Periodic Test Values (Insulating Ladders)

### Overload and Line Contact Tests
- `table_15.png` - **TABLE 3**: Overload Test Line Contact Values

### Component-Specific Tests
- `table_09.png` - **TABLE 4**: Test Voltages for Insulating Liners
- `table_10.png` - **TABLE 5**: Test Voltages for Insulating Buckets

### Equipment Categories and Applications
- `table_13.png` - Equipment Categories (A, B, C, D, E, Non-Insulating)
- `table_14.png` - Test Requirements by Category
- `table_16.png` - Minimum Approach Distances

### Supplemental Tables
- `table_01.png` - Title Page
- `table_11.png` - Supplemental Table 1
- `table_12.png` - Supplemental Table 2
- `table_17.png` - Load Test Documentation

---

## Logos (2)

- `ansi_logo.png` - American National Standards Institute logo
- `saia_logo.jpg` - Scaffold & Access Industry Association logo

**Usage:** Include in PDF reports and inspection documentation for professional appearance.

---

## Equipment Symbols (6)

Warning signs and operational pictograms that appear on aerial devices:

- `equipment_symbols_1.jpg` - High voltage warning signs
- `equipment_symbols_2.jpg` - Boom movement indicators
- `equipment_symbols_3.jpg` - Operational control symbols
- `equipment_symbols_4.jpg` - Safety pictograms
- `equipment_symbols_5.jpg` - Capacity rating markers
- `equipment_symbols_6.jpg` - Operational marking symbols

**Usage:** Reference during markings and placards inspection steps.

---

## Usage in Inspection Templates

### Reference Images in Templates

```json
{
  "step_key": "dielectric_test_setup",
  "step_number": 1,
  "title": "Dielectric Test Setup - Category A/B",
  "reference_images": [
    {
      "image_id": "figure_1",
      "title": "Figure 1: Test Setup for Category A/B",
      "file_path": "ansi_a92_2_2021/figures/figure_1_dielectric_test_cat_ab.jpg",
      "caption": "Lower test electrode system configuration per Section 5.4.2",
      "display_mode": "inline",
      "figure_number": "Figure 1"
    },
    {
      "image_id": "table_2_cat_ab",
      "title": "TABLE 2: Periodic Test Values",
      "file_path": "ansi_a92_2_2021/tables/table_02.png",
      "caption": "Test voltage and current limits for Category A/B devices",
      "display_mode": "modal",
      "figure_number": "Table 2"
    }
  ]
}
```

### Display Modes
- **inline**: Image always visible on inspection screen
- **modal**: Click/tap to view full size
- **both**: Thumbnail inline + click for full size

---

## File Formats

- **Figures**: JPEG/PNG (original format from standard)
- **Tables**: PNG (generated from DOCX tables)
- **Logos**: PNG/JPEG (original format)
- **Symbols**: JPEG (original format)

---

## Standard Text (`standard_text.json`)

ANSI standard text excerpts for use in inspection templates.

### Purpose

Provide inspectors with relevant ANSI standard text **at the point of work** - right on the inspection screen alongside each step.

### Contents

**14 common excerpts** covering:
- Frequent Inspection (Section 8.2.3): Structural, controls, safety devices, hydraulic, electrical, fasteners, markings
- Periodic Inspection (Section 8.2.4): Welds, bolts
- Dielectric Testing (Section 5.4.x): Qualification, periodic, liner, upper control resistance
- Load Testing (Section 4.5.1): Stability test

### Usage in Templates

```json
{
  "step_key": "operating_controls_test",
  "title": "Operating Controls Test",
  "standard_reference": "ANSI A92.2-2021 Section 8.2.3(2)",
  "standard_text": {
    "section": "8.2.3(2)",
    "excerpt": "Performance test of all boom movements.",
    "show_full_section": false
  },
  "fields": [...]
}
```

### Benefits

✅ **Training while working** - Inspectors learn ANSI requirements during inspection
✅ **Compliance confidence** - Know exactly what the standard requires
✅ **No manual lookup** - No flipping through PDF or paper standard
✅ **Documentation** - PDF reports include standard references

### Copyright Notice

⚠️ Excerpts are short (1-2 sentences) for compliance purposes. Full ANSI A92.2-2021 standard must be purchased from ANSI. These excerpts fall under fair use for operational compliance guidance.

---

## Notes

- All images extracted from official ANSI+SAIA+A92.2-2021.docx document
- Tables are rendered as images for consistent display across platforms
- Figure numbers correspond to ANSI A92.2-2021 standard references
- Images optimized for web/mobile display while maintaining readability
- Standard text excerpts are short and for compliance purposes only

---

## Related Files

- Source: `ANSI+SAIA+A92.2-2021.docx`
- Image Extraction: `scripts/extract_ansi_from_docx.py`
- Text Extraction: `scripts/extract_standard_text.py`
- Template Schema: `apps/inspections/schemas/template_schema.py`
- Usage Examples: `STANDARD_TEXT_USAGE_EXAMPLE.md`
