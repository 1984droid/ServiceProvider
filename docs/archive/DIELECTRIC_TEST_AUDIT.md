# Dielectric Test Template Audit

## ANSI A92.2-2021 Requirements vs Current Template

### Section 5.4.3: Periodic/Maintenance Test Procedures

| ANSI Section | Description | Template Coverage | Status |
|--------------|-------------|-------------------|--------|
| **5.4.3.1** | Category A & B Insulating Aerial Devices | ✅ `test_setup_cat_ab` + execution steps | COMPLETE |
| **5.4.3.2** | Category C, D, E Aerial Devices | ✅ `test_setup_cat_cde` + execution steps | COMPLETE |
| **5.4.3.3** | Aerial Ladders & Vertical Towers | ❌ **MISSING** | **NEEDS STEP** |
| **5.4.3.4** | Chassis Insulating Systems | ✅ `chassis_insulating_system_test` | COMPLETE |
| **5.4.3.5** | Insulating Liners (Bucket Liners) | ❌ **MISSING** | **NEEDS STEP** |
| **5.4.3.6** | Upper Control Components (High Resistance) | ❌ **MISSING** | **NEEDS STEP** |
| **5.4.3.7** | Extensible Boom without Permanent Electrodes | ✅ Covered by 5.4.3.2 | COMPLETE |

---

## Current Template Structure

### Steps Present (11 total):

1. ✅ `test_information` - Collect device category, method selection
2. ✅ `pre_test_visual_inspection` - Inspect vacuum limiting, lower electrode, insulating components (HAS auto_defect_on)
3. ✅ `test_equipment_verification` - Verify IEEE Std. 4-2013 compliance
4. ✅ `test_setup_cat_ab` - Setup for Category A/B devices
5. ✅ `test_setup_cat_cde` - Setup for Category C/D/E devices
6. ✅ `execute_test_method_a_ac` - AC test per Table 2
7. ✅ `execute_test_method_b_dc` - DC test per Table 2
8. ✅ `execute_test_method_c_before_use` - Before use test per Table 3
9. ✅ `chassis_insulating_system_test` - Chassis test (if equipped)
10. ✅ `test_results_evaluation` - Pass/fail determination
11. ✅ `test_documentation` - Certification and placard

### auto_defect_on Rules Present:

Only 1 step has auto_defect_on:
- `pre_test_visual_inspection` - 3 rules for visual defects

**PROBLEM**: Most test steps don't have auto_defect_on rules for test failures!

---

## Missing Components

### 1. ❌ Insulating Liner Test (Section 5.4.3.5)

**ANSI Requirement:**
> Platform liners used for insulation shall be tested in a conductive liquid or using conductive electrodes. The liner shall withstand:
> - AC voltage: 35 kV for 1 minute
> - DC voltage: 100 kV for 3 minutes
> - Max current: Not specified (breakdown is failure)

**Missing Step:**
```json
{
  "step_key": "insulating_liner_test",
  "type": "MEASUREMENT",
  "title": "Insulating Liner Test (Bucket Liner)",
  "standard_reference": "ANSI A92.2-2021 Section 5.4.3.5",
  "required": false,  // Only if equipped
  "fields": [
    {
      "field_id": "liner_equipped",
      "label": "Is unit equipped with insulating liner?",
      "type": "ENUM",
      "enum_ref": "yes_no_na",
      "required": true
    },
    {
      "field_id": "test_method_liner",
      "label": "Test Method",
      "type": "ENUM",
      "values": ["CONDUCTIVE_LIQUID", "WET_ELECTRODE"],
      "conditionally_required_if": {
        "any_field_in": ["YES"]
      }
    },
    {
      "field_id": "test_voltage_liner",
      "label": "Test Voltage (kV)",
      "type": "NUMBER",
      "help_text": "AC: 35kV for 1min, DC: 100kV for 3min"
    },
    {
      "field_id": "test_duration_liner",
      "label": "Test Duration (seconds)",
      "type": "NUMBER"
    },
    {
      "field_id": "liner_test_result",
      "label": "Liner Test Result",
      "type": "ENUM",
      "enum_ref": "pass_fail"
    }
  ],
  "auto_defect_on": [
    {
      "when": {
        "path": "liner_test_result",
        "equals": "FAIL"
      },
      "defect": {
        "title": "Insulating liner failed dielectric test",
        "severity": "UNSAFE_OUT_OF_SERVICE",
        "description": "Bucket liner failed to withstand test voltage. Liner must be replaced before unit can be returned to service.",
        "standard_reference": "ANSI A92.2-2021 Section 5.4.3.5"
      }
    }
  ]
}
```

---

### 2. ❌ Upper Control High Resistance Test (Section 5.4.3.6)

**ANSI Requirement:**
> Upper controls that incorporate components for their electrical resistance shall be tested per Figure 6:
> - AC: 40kV for 3 minutes, max 400 µA
> - DC: 56kV for 3 minutes, max 56 µA

**Missing Step:**
```json
{
  "step_key": "upper_control_resistance_test",
  "type": "MEASUREMENT",
  "title": "Upper Control Components High Resistance Test",
  "standard_reference": "ANSI A92.2-2021 Section 5.4.3.6 & Figure 6",
  "required": false,  // Only if equipped
  "reference_images": [
    {
      "image_id": "figure_6",
      "title": "Figure 6: Confirmation Test of Upper Control Components",
      "file_path": "ansi_a92_2_2021/figures/figure_6_upper_control_test.png",
      "display_mode": "both",
      "figure_number": "Figure 6"
    }
  ],
  "fields": [
    {
      "field_id": "high_resistance_controls_equipped",
      "label": "Unit equipped with high resistance upper controls?",
      "type": "ENUM",
      "enum_ref": "yes_no_na",
      "required": true
    },
    {
      "field_id": "control_test_voltage_type",
      "label": "Test Voltage Type",
      "type": "ENUM",
      "values": ["AC_40KV", "DC_56KV"]
    },
    {
      "field_id": "control_test_voltage",
      "label": "Test Voltage (kV)",
      "type": "NUMBER"
    },
    {
      "field_id": "control_test_duration",
      "label": "Test Duration (minutes)",
      "type": "NUMBER",
      "help_text": "Must be 3 minutes minimum"
    },
    {
      "field_id": "control_leakage_current",
      "label": "Leakage Current (microamperes)",
      "type": "NUMBER"
    },
    {
      "field_id": "control_test_result",
      "label": "Upper Control Test Result",
      "type": "ENUM",
      "enum_ref": "pass_fail"
    }
  ],
  "auto_defect_on": [
    {
      "when": {
        "path": "control_test_result",
        "equals": "FAIL"
      },
      "defect": {
        "title": "Upper control high resistance test failed",
        "severity": "UNSAFE_OUT_OF_SERVICE",
        "description": "Upper control components exceeded maximum allowable leakage current. Controls must be repaired or replaced.",
        "standard_reference": "ANSI A92.2-2021 Section 5.4.3.6"
      }
    }
  ]
}
```

---

### 3. ❌ Aerial Ladder/Vertical Tower Test (Section 5.4.3.3)

**ANSI Requirement:**
> Aerial ladders and vertical towers with insulating boom sections shall be tested per 5.4.3.2 with special positioning requirements.

**Missing Step:**
```json
{
  "step_key": "aerial_ladder_tower_test",
  "type": "MEASUREMENT",
  "title": "Aerial Ladder or Vertical Tower Test",
  "standard_reference": "ANSI A92.2-2021 Section 5.4.3.3",
  "required": false,  // Only for ladders/towers
  "fields": [
    {
      "field_id": "unit_is_ladder_or_tower",
      "label": "Is unit an aerial ladder or vertical tower?",
      "type": "ENUM",
      "enum_ref": "yes_no_na",
      "required": true
    },
    {
      "field_id": "ladder_extended_correctly",
      "label": "Ladder extended only far enough for platform to drop (or predetermined length)?",
      "type": "BOOLEAN"
    },
    {
      "field_id": "tower_rails_raised",
      "label": "Tower platform rails raised within platform confines?",
      "type": "BOOLEAN"
    },
    {
      "field_id": "ladder_tower_test_result",
      "label": "Ladder/Tower Test Result",
      "type": "ENUM",
      "enum_ref": "pass_fail"
    }
  ],
  "auto_defect_on": [
    {
      "when": {
        "path": "ladder_tower_test_result",
        "equals": "FAIL"
      },
      "defect": {
        "title": "Aerial ladder/tower dielectric test failed",
        "severity": "UNSAFE_OUT_OF_SERVICE",
        "description": "Insulating boom section failed dielectric test. Unit must not be used until repaired.",
        "standard_reference": "ANSI A92.2-2021 Section 5.4.3.3"
      }
    }
  ]
}
```

---

## Missing auto_defect_on Rules

### Steps that SHOULD have auto_defect_on but don't:

1. **`chassis_insulating_system_test`** - No auto_defect_on for test failure
   - Should trigger UNSAFE_OUT_OF_SERVICE if current > 3mA (AC) or > 100µA (DC)

2. **`execute_test_method_a_ac`** - No auto_defect_on for excessive leakage
   - Should check against Table 2 limits

3. **`execute_test_method_b_dc`** - No auto_defect_on for excessive leakage
   - Should check against Table 2 limits

4. **`execute_test_method_c_before_use`** - No auto_defect_on for excessive leakage
   - Should check against Table 3 limits

5. **`test_equipment_verification`** - No auto_defect_on for non-compliant equipment
   - Should block test if equipment doesn't meet IEEE Std. 4-2013

---

## Recommendations

### Priority 1: Add Missing Test Steps
1. Add `insulating_liner_test` step
2. Add `upper_control_resistance_test` step
3. Add `aerial_ladder_tower_test` step

### Priority 2: Add auto_defect_on Rules
Add auto_defect_on to ALL test execution steps to catch:
- Excessive leakage current
- Test failures
- Equipment non-compliance

### Priority 3: Add Reference Images
Reference images needed:
- Figure 6: Upper Control Confirmation Test
- Table 2: Periodic Electrical Test Values (for leakage limits)
- Table 3: Before Use Tests

---

## Standard References Mapping

For the script `add_standard_references_to_templates.py`, update mapping:

```python
'dielectric_test_periodic': {
    'pre_test_visual_inspection': 'ANSI A92.2-2021 Section 5.4.3.1(1)-(4) & 8.2.4(16)',
    'chassis_insulating_system_test': 'ANSI A92.2-2021 Section 5.4.3.4',
    # ADD THESE:
    'insulating_liner_test': 'ANSI A92.2-2021 Section 5.4.3.5',
    'upper_control_resistance_test': 'ANSI A92.2-2021 Section 5.4.3.6',
    'aerial_ladder_tower_test': 'ANSI A92.2-2021 Section 5.4.3.3',
}
```
