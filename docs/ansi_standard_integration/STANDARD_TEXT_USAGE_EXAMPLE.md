# Standard Text in Templates - Usage Examples

## Overview

Inspection templates can now include ANSI standard text excerpts alongside each step, providing inspectors with context and guidance during execution.

---

## Template Step with Standard Text

### Example: Operating Controls Test

```json
{
  "step_key": "operating_controls_test",
  "type": "FUNCTION_TEST",
  "title": "Operating Controls Test",
  "standard_reference": "ANSI A92.2-2021 Section 8.2.3(2)",
  "standard_text": {
    "section": "8.2.3(2)",
    "excerpt": "Performance test of all boom movements.",
    "show_full_section": false
  },
  "fields": [
    {
      "field_key": "boom_raise_test",
      "label": "Boom Raise Function",
      "type": "ENUM",
      "enum_ref": "pass_fail_na",
      "required": true
    },
    {
      "field_key": "boom_lower_test",
      "label": "Boom Lower Function",
      "type": "ENUM",
      "enum_ref": "pass_fail_na",
      "required": true
    },
    {
      "field_key": "boom_extend_test",
      "label": "Boom Extend Function",
      "type": "ENUM",
      "enum_ref": "pass_fail_na",
      "required": true
    },
    {
      "field_key": "boom_retract_test",
      "label": "Boom Retract Function",
      "type": "ENUM",
      "enum_ref": "pass_fail_na",
      "required": true
    }
  ],
  "auto_defect_on": [
    {
      "condition": {
        "any_of": [
          {"field": "boom_raise_test", "equals": "fail"},
          {"field": "boom_lower_test", "equals": "fail"},
          {"field": "boom_extend_test", "equals": "fail"},
          {"field": "boom_retract_test", "equals": "fail"}
        ]
      },
      "defect": {
        "title": "Boom Control Failure",
        "severity": "critical",
        "description": "One or more boom controls failed to operate properly",
        "standard_reference": "ANSI A92.2-2021 Section 8.2.3(2)",
        "corrective_action": "Inspect and repair hydraulic system, control valves, and electrical connections. Test all controls before returning to service."
      }
    }
  ]
}
```

---

## Complex Example with Images and Standard Text

### Example: Dielectric Test - Category A/B

```json
{
  "step_key": "dielectric_test_cat_ab_setup",
  "type": "SETUP",
  "title": "Dielectric Test Setup - Category A/B",
  "standard_reference": "ANSI A92.2-2021 Section 5.4.3.1",
  "standard_text": {
    "section": "5.4.3.1",
    "excerpt": "Test procedures for Category A and B aerial devices with lower test electrode system. Test criteria of Table 1 shall be followed for the appropriate application (ac and/or dc).",
    "show_full_section": true
  },
  "reference_images": [
    {
      "image_id": "figure_1",
      "title": "Figure 1: Dielectric Test Setup for Category A/B",
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
  ],
  "fields": [
    {
      "field_key": "unit_rating",
      "label": "Unit Rated Line Voltage (kV)",
      "type": "ENUM",
      "enum_ref": "voltage_ratings",
      "required": true,
      "help_text": "Select the rated line voltage from equipment nameplate"
    },
    {
      "field_key": "test_type",
      "label": "Test Type",
      "type": "ENUM",
      "enum_ref": "ac_dc_test_type",
      "required": true
    },
    {
      "field_key": "electrode_installed",
      "label": "Lower Test Electrode Installed",
      "type": "BOOLEAN",
      "required": true
    }
  ]
}
```

---

## Available Standard Text Excerpts

From `static/inspection_references/ansi_a92_2_2021/standard_text.json`:

### Frequent Inspection (8.2.3)

```json
{
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
  }
}
```

### Periodic Inspection (8.2.4)

```json
{
  "welds": {
    "section": "8.2.4(14)",
    "excerpt": "Welds, as specified by the manufacturer."
  },
  "bolts_detailed": {
    "section": "8.2.4(13)",
    "excerpt": "Condition and tightness of bolts and other fasteners."
  }
}
```

### Dielectric Testing (5.4.x)

```json
{
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
  }
}
```

### Load Testing (4.5.1)

```json
{
  "load_test": {
    "section": "4.5.1",
    "excerpt": "Stability test with one and one-half times the rated load capacity."
  }
}
```

---

## Frontend Display Mock-up

When an inspector views a step with standard text:

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 2 of 22                                                     │
│ Operating Controls Test                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Test all boom operating controls for proper function.           │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📖 ANSI A92.2-2021 Section 8.2.3(2)                         │ │
│ │ "Performance test of all boom movements."                   │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ☐ Boom Raise Function        [Pass / Fail / N/A]               │
│ ☐ Boom Lower Function        [Pass / Fail / N/A]               │
│ ☐ Boom Extend Function       [Pass / Fail / N/A]               │
│ ☐ Boom Retract Function      [Pass / Fail / N/A]               │
│ ☐ Boom Rotation (if equipped) [Pass / Fail / N/A]              │
│                                                                  │
│ [Previous]                                        [Next Step] → │
└─────────────────────────────────────────────────────────────────┘
```

With full section available:

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 5 of 22                                                     │
│ Dielectric Test Setup - Category A/B                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📖 ANSI A92.2-2021 Section 5.4.3.1                          │ │
│ │ "Test procedures for Category A and B aerial devices with   │ │
│ │ lower test electrode system. Test criteria of Table 1 shall │ │
│ │ be followed for the appropriate application (ac and/or dc)."│ │
│ │                                                              │ │
│ │ [View Full Section 5.4.3.1] [View Table 2]                  │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ [Figure 1: Test Setup] (inline image shown here)                │
│                                                                  │
│ Unit Rated Line Voltage: [46kV ▼]                               │
│ Test Type: [60 Hz AC ▼]                                          │
│ ☑ Lower Test Electrode Installed                                │
│                                                                  │
│ [Previous]                                        [Next Step] → │
└─────────────────────────────────────────────────────────────────┘
```

---

## Benefits

### For Inspectors
- ✅ **Context at point of work** - Standard requirements right where they need them
- ✅ **Training while working** - Learn ANSI requirements during inspection
- ✅ **Confidence** - Know exactly what the standard requires
- ✅ **No manual lookup** - No flipping through PDF or paper standard

### For Quality
- ✅ **Compliance** - Every step shows ANSI reference
- ✅ **Consistency** - All inspectors see same standard text
- ✅ **Documentation** - PDF reports include standard references
- ✅ **Audit trail** - Clear connection between work and standard

### For Customers
- ✅ **Transparency** - See exactly what standard requires
- ✅ **Trust** - Inspections clearly follow ANSI standard
- ✅ **Compliance proof** - Reports show standard references

---

## Implementation Checklist

- [x] Extract standard text from ANSI DOCX
- [x] Create `standard_text.json` with common excerpts
- [x] Extend Pydantic schema with `StandardTextReference`
- [x] Add `standard_text` field to `ProcedureStep`
- [ ] Add standard text to frequent inspection template
- [ ] Add standard text to periodic inspection template
- [ ] Add standard text to dielectric test template
- [ ] Implement frontend display (inline excerpts)
- [ ] Implement "View Full Section" modal
- [ ] Include standard text in PDF reports
- [ ] Test with real inspectors

---

## Copyright Note

⚠️ **Important:** ANSI A92.2-2021 is a copyrighted standard. The excerpts used are:

- **Short** (1-2 sentences per step)
- **For compliance purposes** (operational guidance)
- **Referenced properly** (with section numbers)
- **Not redistributing full standard**

This falls under fair use for compliance purposes. Full standard must be purchased from ANSI.

