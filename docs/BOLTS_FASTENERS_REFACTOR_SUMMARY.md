# Bolts & Fasteners Step Refactor - Pilot Implementation

**Date:** 2026-03-15
**Template:** periodic_inspection.json
**Step:** bolts_fasteners
**Purpose:** Demonstrate new structured defect capture pattern

---

## Summary of Changes

### ✅ What Was Fixed

1. **Removed 3 redundant boolean summary fields**
   - ❌ `loose_fasteners_found` (Yes/No)
   - ❌ `missing_fasteners_found` (Yes/No)
   - ❌ `fastener_defects_found` (Yes/No)

2. **Replaced pass/fail with wear_level assessments**
   - All component fields now use `wear_level` enum
   - Provides granular assessment: NONE, MINOR, MODERATE, EXCESSIVE, REQUIRES_REPLACEMENT

3. **Updated auto_defect_on rules**
   - Now triggers on `any_field_in: [EXCESSIVE, REQUIRES_REPLACEMENT]`
   - No longer depends on summary boolean

4. **Enhanced guidance text**
   - Instructs inspectors to use "Add Defect" button
   - Clarifies photo requirements

5. **Added blocking_fail flag**
   - Step blocks finalization if critical issues found

---

## Before & After Comparison

### BEFORE (Old Pattern - Redundant)

**13 Fields:**
```
1. structural_bolts (pass_fail) - REQUIRED
2. boom_pivot_pins (pass_fail) - REQUIRED
3. boom_pivot_pin_wear (wear_level) - REQUIRED ✅ (already had this!)
4. cylinder_mounting_pins (pass_fail) - REQUIRED
5. platform_mounting_bolts (pass_fail) - REQUIRED
6. pedestal_mounting_bolts (pass_fail) - REQUIRED
7. turret_bearing_bolts (pass_fail) - REQUIRED
8. outrigger_bolts_pins (pass_fail) - REQUIRED
9. loose_fasteners_found (boolean) - REQUIRED ❌ REDUNDANT
10. missing_fasteners_found (boolean) - REQUIRED ❌ REDUNDANT
11. fastener_defects_found (boolean) - REQUIRED ❌ REDUNDANT
12. fastener_notes (text_area) - optional
13. defect_photos (photo) - optional/conditional
```

**Issues:**
- 8 components with pass/fail (binary)
- Then asks "any defects found?" 3 different ways
- If structural_bolts = FAIL, then obviously loose_fasteners_found = Yes
- Data inconsistency risk
- Confusing UX

---

### AFTER (New Pattern - Structured)

**9 Fields:**
```
1. structural_bolts_condition (wear_level) - REQUIRED
2. boom_pivot_pins_condition (wear_level) - REQUIRED
3. cylinder_mounting_pins_condition (wear_level) - REQUIRED
4. platform_mounting_bolts_condition (wear_level) - REQUIRED
5. pedestal_mounting_bolts_condition (wear_level) - REQUIRED
6. turret_bearing_bolts_condition (wear_level) - REQUIRED
7. outrigger_bolts_pins_condition (wear_level) - REQUIRED
8. fastener_notes (text_area) - optional
9. defect_photos (photo) - optional/conditional
```

**Benefits:**
- ✅ 7 components with granular wear assessment
- ✅ No redundant summary questions
- ✅ One assessment per component
- ✅ Clearer data structure
- ✅ Simpler UX

**Reduced from 13 fields to 9 fields** (-31%)

---

## Field Mapping

### Old → New

| Old Field ID | Old Type | New Field ID | New Type | Change |
|--------------|----------|--------------|----------|--------|
| `structural_bolts` | pass_fail | `structural_bolts_condition` | wear_level | More granular |
| `boom_pivot_pins` | pass_fail | `boom_pivot_pins_condition` | wear_level | More granular |
| `boom_pivot_pin_wear` | wear_level | `boom_pivot_pins_condition` | wear_level | Consolidated |
| `cylinder_mounting_pins` | pass_fail | `cylinder_mounting_pins_condition` | wear_level | More granular |
| `platform_mounting_bolts` | pass_fail | `platform_mounting_bolts_condition` | wear_level | More granular |
| `pedestal_mounting_bolts` | pass_fail | `pedestal_mounting_bolts_condition` | wear_level | More granular |
| `turret_bearing_bolts` | pass_fail | `turret_bearing_bolts_condition` | wear_level | More granular |
| `outrigger_bolts_pins` | pass_fail | `outrigger_bolts_pins_condition` | wear_level | More granular |
| `loose_fasteners_found` | boolean | *(removed)* | - | **DELETED** |
| `missing_fasteners_found` | boolean | *(removed)* | - | **DELETED** |
| `fastener_defects_found` | boolean | *(removed)* | - | **DELETED** |
| `fastener_notes` | text_area | `fastener_notes` | text_area | No change |
| `defect_photos` | photo | `defect_photos` | photo | No change |

---

## wear_level Enum Values

```json
{
  "wear_level": [
    "NONE",                  // No wear or damage
    "MINOR",                 // Minor wear, acceptable
    "MODERATE",              // Moderate wear, monitor
    "EXCESSIVE",             // Excessive wear, requires service
    "REQUIRES_REPLACEMENT"   // Must be replaced
  ]
}
```

**Photo Requirements:**
- **REQUIRED:** EXCESSIVE, REQUIRES_REPLACEMENT
- **SUGGESTED:** MODERATE, MINOR
- **NONE:** No photo needed (NONE)

---

## Defect Workflow

### Old Workflow (Confusing)
```
1. Inspector checks structural_bolts → selects FAIL
2. Inspector checks boom_pivot_pins → selects PASS
3. Inspector checks cylinder_mounting_pins → selects FAIL
4. ...continues for all 8 components
5. Inspector then answers:
   - "Any loose fasteners found?" → Yes (redundant!)
   - "Any missing fasteners found?" → Yes (redundant!)
   - "Any defects found?" → Yes (redundant!)
6. Inspector uploads photos
7. Auto-defect creates generic defect
```

**Problems:**
- Asks same question 4 times (8 components + 3 booleans)
- No structured defect details captured
- Generic auto-defect with no specifics
- Photos not tied to specific defects

---

### New Workflow (Structured)
```
1. Inspector assesses structural_bolts_condition → NONE
2. Inspector assesses boom_pivot_pins_condition → EXCESSIVE
3. Inspector assesses cylinder_mounting_pins_condition → MODERATE
4. ...continues for all 7 components

5. System detects EXCESSIVE and MODERATE values
   → Shows "Defects Found" indicator
   → Highlights affected fields
   → Displays "Add Defect" button
   → Shows photo requirement warning

6. Inspector clicks "Add Defect" for boom_pivot_pins
   → Modal opens with defect_schema fields
   → Auto-populates:
     - title: "Excessive wear on boom pivot pins"
     - component: "Boom Pivot Pins"
   → Inspector fills:
     - severity: SERVICE_REQUIRED
     - description: "Pin diameter 1.87\" (spec 2.00\"), visible play 1/8\""
     - location: "Driver side, lower boom section, second pin from base"
     - photo_evidence: [uploads 2 photos] ✅ REQUIRED
     - corrective_action: "Replace with OEM part #BP-2045"

7. Inspector clicks "Add Defect" for cylinder_mounting_pins
   → Fills out another defect with details

8. Auto-defect rule fires when ANY field = EXCESSIVE/REQUIRES_REPLACEMENT
   → Creates summary defect for inspection report
```

**Benefits:**
✅ No redundant questions
✅ Structured defect data with component, location, photos
✅ Photos tied to specific defects
✅ Rich data for work orders
✅ Better PDF documentation

---

## auto_defect_on Changes

### BEFORE
```json
"auto_defect_on": [
  {
    "when": {
      "path": "fastener_defects_found",  // ❌ Boolean field
      "equals": true
    },
    "defect": {
      "title": "Bolt/fastener defects found during periodic inspection",
      "severity": "SERVICE_REQUIRED",
      "description": "Fastener defects detected that require correction."
    }
  }
]
```

**Problem:** Depends on redundant boolean summary field

---

### AFTER
```json
"auto_defect_on": [
  {
    "when": {
      "any_field_in": [                  // ✅ Checks actual assessments
        "EXCESSIVE",
        "REQUIRES_REPLACEMENT"
      ]
    },
    "defect": {
      "title": "Critical fastener wear/damage found during periodic inspection",
      "severity": "SERVICE_REQUIRED",
      "description": "Fastener condition requires replacement or repair. See defect details for specific components and recommendations."
    }
  }
]
```

**Benefits:**
✅ Triggers on actual condition values
✅ No dependency on summary boolean
✅ More descriptive defect message
✅ Directs to defect details for specifics

---

## UI Changes Required

### Step Display

**BEFORE:**
```
┌─────────────────────────────────────────────────┐
│ Bolts, Pins, and Fasteners                      │
├─────────────────────────────────────────────────┤
│ Structural Bolts: [PASS ▼]                      │
│ Boom Pivot Pins: [FAIL ▼]                       │
│ Boom Pivot Pin Wear: [EXCESSIVE ▼]              │
│ Cylinder Mounting Pins: [PASS ▼]                │
│ Platform Mounting Bolts: [PASS ▼]               │
│ Pedestal Mounting Bolts: [PASS ▼]               │
│ Turret Bearing Bolts: [PASS ▼]                  │
│ Outrigger Bolts: [PASS ▼]                       │
│                                                  │
│ Any loose fasteners? ⚪ Yes ⚪ No                │
│ Any missing fasteners? ⚪ Yes ⚪ No              │
│ Any defects found? ⚪ Yes ⚪ No                  │
│                                                  │
│ Notes: [                                    ]    │
│ Photos: [📷 Upload]                              │
└─────────────────────────────────────────────────┘
```

---

**AFTER:**
```
┌─────────────────────────────────────────────────┐
│ Bolts, Pins, and Fasteners                      │
│ ⚠️  DEFECTS FOUND - Click "Add Defect" to      │
│     document details                             │
├─────────────────────────────────────────────────┤
│ Structural Bolts: [NONE ▼]                      │
│ Boom Pivot Pins: [EXCESSIVE ▼] ⚠️ 📷 REQUIRED  │
│ Cylinder Mounting Pins: [MODERATE ▼] 📷 Suggested│
│ Platform Mounting Bolts: [NONE ▼]               │
│ Pedestal Mounting Bolts: [NONE ▼]               │
│ Turret Bearing Bolts: [NONE ▼]                  │
│ Outrigger Bolts: [NONE ▼]                       │
│                                                  │
│ Notes: [                                    ]    │
│ Photos: [📷 Upload] Required for EXCESSIVE wear │
│                                                  │
│ [➕ Add Defect] (2 defects documented)          │
│                                                  │
│ Defects:                                         │
│ ┌────────────────────────────────────────────┐  │
│ │ 🔴 SERVICE_REQUIRED                         │  │
│ │ Excessive wear on boom pivot pins          │  │
│ │ Location: Driver side, lower boom          │  │
│ │ Photos: 2 attached                         │  │
│ │ [Edit] [Delete]                            │  │
│ └────────────────────────────────────────────┘  │
│ ┌────────────────────────────────────────────┐  │
│ │ 🟡 MINOR                                    │  │
│ │ Moderate wear on cylinder mounting pins    │  │
│ │ Location: Boom lift cylinder, driver side  │  │
│ │ Photos: 1 attached                         │  │
│ │ [Edit] [Delete]                            │  │
│ └────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Data Structure Changes

### step_data Storage

**BEFORE:**
```json
{
  "bolts_fasteners": {
    "structural_bolts": "FAIL",
    "boom_pivot_pins": "FAIL",
    "boom_pivot_pin_wear": "EXCESSIVE",
    "cylinder_mounting_pins": "PASS",
    "platform_mounting_bolts": "PASS",
    "pedestal_mounting_bolts": "PASS",
    "turret_bearing_bolts": "PASS",
    "outrigger_bolts_pins": "PASS",
    "loose_fasteners_found": true,
    "missing_fasteners_found": false,
    "fastener_defects_found": true,
    "fastener_notes": "Boom pivot pins worn",
    "defect_photos": ["photo1.jpg", "photo2.jpg"]
  }
}
```

---

**AFTER:**
```json
{
  "bolts_fasteners": {
    "structural_bolts_condition": "NONE",
    "boom_pivot_pins_condition": "EXCESSIVE",
    "cylinder_mounting_pins_condition": "MODERATE",
    "platform_mounting_bolts_condition": "NONE",
    "pedestal_mounting_bolts_condition": "NONE",
    "turret_bearing_bolts_condition": "NONE",
    "outrigger_bolts_pins_condition": "NONE",
    "fastener_notes": "General condition acceptable except as noted in defects",
    "defect_photos": ["photo1.jpg", "photo2.jpg"],

    "defects": [
      {
        "defect_id": "uuid-1",
        "title": "Excessive wear on boom pivot pins",
        "severity": "SERVICE_REQUIRED",
        "description": "Boom pivot pin diameter measured at 1.87\" (spec 2.00\"). Visible play in boom joint approximately 1/8\" vertical movement when boom raised.",
        "component": "Boom Pivot Pins",
        "location": "Driver side, lower boom section, second pivot pin from base",
        "photo_evidence": ["photo1.jpg", "photo2.jpg"],
        "corrective_action": "Replace boom pivot pin with OEM part #BP-2045. Inspect bushing for wear during disassembly. If bushing worn, replace with part #BS-2046.",
        "standard_reference": "ANSI A92.2-2021 Section 8.2.4(13)"
      },
      {
        "defect_id": "uuid-2",
        "title": "Moderate wear on cylinder mounting pins",
        "severity": "MINOR",
        "description": "Slight play detected in boom lift cylinder upper mounting pin. Pin diameter within spec but showing early wear pattern.",
        "component": "Hydraulic Cylinder Mounting Pins",
        "location": "Boom lift cylinder, driver side, upper pin",
        "photo_evidence": ["photo3.jpg"],
        "corrective_action": "Monitor condition, re-check at next periodic inspection. Plan for replacement at 50 operating hours."
      }
    ]
  }
}
```

---

## Migration Strategy

### For Existing Inspections (In Progress)

**No migration needed** - Existing field values remain valid:
- Old `pass_fail` values (PASS, FAIL) are still valid in historical data
- Frontend can handle both old and new field structures
- Only new inspections use new field IDs

### For Templates

**Periodic Inspection:** ✅ UPDATED
**Frequent Inspection:** ⏳ TODO (apply same pattern)
**Other Templates:** ⏳ TODO (assess which steps need refactoring)

---

## Testing Checklist

### Frontend
- [ ] wear_level dropdown renders with 5 values
- [ ] Photo requirement indicator shows for EXCESSIVE/REQUIRES_REPLACEMENT
- [ ] Photo suggestion shows for MODERATE/MINOR
- [ ] "Add Defect" button appears when defect conditions detected
- [ ] Defect modal opens with pre-populated component
- [ ] Defect list displays added defects
- [ ] Can edit/delete defects before finalization
- [ ] Step validation checks photo requirements

### Backend
- [ ] auto_defect_on triggers on any_field_in values
- [ ] Defects from step_data convert to InspectionDefect records
- [ ] defect_details JSON includes all schema fields
- [ ] Photos link correctly to defects
- [ ] Work orders can be created from defects
- [ ] PDF export includes defect details and photos

### Integration
- [ ] Complete inspection flow: assessment → defect → work order → PDF
- [ ] Photo upload and storage
- [ ] Defect edit/delete before finalization
- [ ] Immutability after finalization

---

## Next Steps

1. **Apply to frequent_inspection.json** - Same pattern
2. **Test with real inspection data** - QA on dev environment
3. **Refactor other visual inspection steps:**
   - structural_components
   - welds_inspection
   - hydraulic_system
   - electrical_system
4. **Build frontend components:**
   - AddDefectButton
   - AddDefectModal
   - DefectList
   - DefectItem
5. **Enhance PDF export** - Include defect photos

---

**Status:** ✅ Periodic template updated, ready for testing
**Next:** Apply to frequent_inspection.json
