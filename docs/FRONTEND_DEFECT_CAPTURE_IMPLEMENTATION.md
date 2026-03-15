# Frontend Defect Capture Implementation

**Date:** 2026-03-15
**Status:** ✅ Complete
**Purpose:** Document the frontend implementation of structured defect capture during inspection execution

---

## Overview

Implemented a complete frontend system for capturing structured defects during inspection execution, following the defect_schema specification. Inspectors can now document defects with rich details, photos, and corrective actions directly within inspection steps.

---

## Components Created

### 1. AddDefectModal.tsx
**Location:** `frontend/src/features/inspections/steps/AddDefectModal.tsx`

**Purpose:** Modal form for adding/editing defects using defect_schema

**Features:**
- All 8 defect_schema fields supported
- Real-time validation with character counters
- Conditional photo requirements based on severity
- Auto-populates component from triggering field
- Edit mode support
- Mobile-friendly full-screen modal

**Fields:**
```typescript
{
  defect_id: string (UUID, auto-generated)
  title: string (required, max 200 chars)
  severity: SAFE | MINOR | SERVICE_REQUIRED | UNSAFE_OUT_OF_SERVICE (required)
  description: string (required, max 2000 chars)
  component?: string (max 100 chars)
  location?: string (max 200 chars)
  photo_evidence?: string[] (conditionally required)
  corrective_action?: string (max 1000 chars)
  standard_reference?: string (max 100 chars)
}
```

**Validation Rules:**
- ✅ Required fields: title, severity, description
- ✅ Photos REQUIRED when severity = SERVICE_REQUIRED or UNSAFE_OUT_OF_SERVICE
- ✅ Photos SUGGESTED when severity = MINOR
- ✅ Character limit validation with counters
- ✅ Max 10 photos per defect

---

### 2. StepDefectsList.tsx
**Location:** `frontend/src/features/inspections/steps/StepDefectsList.tsx`

**Purpose:** Display and manage defects within a step

**Features:**
- Color-coded severity badges
- Photo count indicators
- Edit/Delete actions
- Expandable defect details
- Component and location display
- Corrective action display

**Visual Design:**
- Severity-based left border colors
- SAFE: Green (`#10b981`)
- MINOR: Yellow (`#f59e0b`)
- SERVICE_REQUIRED: Orange (`#ea580c`)
- UNSAFE_OUT_OF_SERVICE: Red (`#dc2626`)

---

### 3. VisualInspectionStep.tsx (Enhanced)
**Location:** `frontend/src/features/inspections/steps/VisualInspectionStep.tsx`

**Purpose:** Enhanced visual inspection step with defect capture support

**New Features:**
- Detects ADD_DEFECT_ITEMS mode from step config
- Auto-detects defect trigger values in assessments
- Highlights fields with defect conditions (yellow ring)
- Shows defect alert banner when conditions detected
- Manages defects array in step values
- Pre-populates defect modal from assessment data

**Defect Trigger Values:**
```typescript
[
  'FAIL',
  'EXCESSIVE',
  'REQUIRES_REPLACEMENT',
  'SERVICE_REQUIRED',
  'UNSAFE_OUT_OF_SERVICE',
  'MODERATE',
  'MINOR',
]
```

**UI Enhancements:**
- ⚠️ Defect alert banner with count
- 🔶 Yellow ring highlight on fields with defect values
- ➕ Add Defect button (prominent when conditions detected)
- Guidance section for inspection instructions
- Defects list below assessment fields
- Dashed border "Add Defect" button always available

---

## Integration Points

### StepRenderer.tsx
**Changes:**
- Added `schemas` prop
- Extracts `defectSchema` from schemas using `step.defect_schema_ref`
- Passes `defectSchema` to VisualInspectionStep

### InspectionExecutePage.tsx
**Changes:**
- Added `schemas` to InspectionTemplate interface
- Extracts schemas from `templateSnapshot.schemas`
- Passes schemas to StepRenderer

---

## Data Flow

### 1. Template Loading
```
Backend API → template_snapshot
  ↓
InspectionExecutePage.loadInspectionData()
  ↓
transformedTemplate { schemas: {...} }
  ↓
StepRenderer { schemas }
  ↓
VisualInspectionStep { defectSchema }
```

### 2. Defect Capture Workflow
```
1. Inspector selects assessment value
   ├─ boom_pivot_pins_condition = "EXCESSIVE"
   └─ Triggers defect indicator
      ↓
2. Yellow ring highlights field
   ├─ Shows "⚠️ Defect condition" label
   └─ Defect alert banner appears
      ↓
3. Inspector clicks "Add Defect"
   ├─ Modal opens
   ├─ Pre-populated: component = "Boom Pivot Pins"
   └─ Inspector fills details
      ↓
4. Validation
   ├─ Required fields check
   ├─ Character limits check
   └─ Photo requirement check (based on severity)
      ↓
5. Save defect
   ├─ Adds to defects array in step values
   ├─ step_data[step_key].defects.push(defect)
   └─ Displays in StepDefectsList
      ↓
6. Auto-save (30 seconds)
   ├─ useStepData hook auto-saves
   └─ Backend stores in InspectionRun.step_data
```

### 3. Step Data Structure
```json
{
  "bolts_fasteners": {
    "structural_bolts_condition": "NONE",
    "boom_pivot_pins_condition": "EXCESSIVE",
    "cylinder_mounting_pins_condition": "MODERATE",
    ...
    "fastener_notes": "General condition good",
    "defect_photos": ["photo1.jpg"],

    "defects": [
      {
        "defect_id": "uuid-1",
        "title": "Excessive wear on boom pivot pins",
        "severity": "SERVICE_REQUIRED",
        "description": "Pin diameter 1.87\" (spec 2.00\")...",
        "component": "Boom Pivot Pins",
        "location": "Driver side, lower boom",
        "photo_evidence": ["photo1.jpg", "photo2.jpg"],
        "corrective_action": "Replace with OEM part #BP-2045",
        "standard_reference": "ANSI A92.2-2021 Section 8.2.4(13)"
      }
    ]
  }
}
```

---

## User Experience Flow

### Scenario: Boom Pivot Pin Wear

**Step 1: Assessment**
```
Inspector opens "Bolts, Pins, and Fasteners" step
↓
Sees guidance:
  • "Assess condition and wear level for each component"
  • "When EXCESSIVE wear found, click 'Add Defect'"
  • "Include photos - required for EXCESSIVE wear"
↓
Assesses "Boom Pivot Pins": Selects "EXCESSIVE"
```

**Step 2: Defect Detection**
```
✓ Field highlights with yellow ring
✓ "⚠️ Defect condition" label appears
✓ Alert banner shows:
  "⚠️ Defect Conditions Detected"
  "1 field(s) require defect documentation"
  [➕ Add Defect] button
```

**Step 3: Add Defect**
```
Inspector clicks "Add Defect"
↓
Modal opens with pre-filled:
  Component: "Boom Pivot Pins"
↓
Inspector fills:
  Severity: "SERVICE_REQUIRED" ⚠️ Photos REQUIRED
  Title: "Excessive wear on boom pivot pins"
  Description: "Pin diameter measured 1.87\" (spec 2.00\").
                Visible play in joint ~1/8\" movement..."
  Location: "Driver side, lower boom, second pin from base"
  Photos: [uploads 2 photos] ✓
  Corrective Action: "Replace with OEM part #BP-2045..."
  Standard: "ANSI A92.2-2021 Section 8.2.4(13)"
↓
Clicks "Add Defect"
```

**Step 4: Defect Displayed**
```
Defect card appears below assessment fields:
┌─────────────────────────────────────────┐
│ 🟧 SERVICE_REQUIRED  📷 2 photos       │
│                           [Edit][Delete] │
├─────────────────────────────────────────┤
│ Excessive wear on boom pivot pins      │
│                                         │
│ Pin diameter measured 1.87\"...        │
│                                         │
│ Component: Boom Pivot Pins              │
│ Location: Driver side, lower boom...   │
│                                         │
│ Corrective Action:                      │
│ Replace with OEM part #BP-2045...       │
└─────────────────────────────────────────┘
```

**Step 5: Save & Continue**
```
Inspector clicks "Save Draft" or navigates to next step
↓
Auto-save triggered
↓
Defect stored in step_data
↓
Backend will convert to InspectionDefect on finalization
```

---

## Visual Design

### Defect Alert Banner
```
┌────────────────────────────────────────────────────┐
│ ⚠️ Defect Conditions Detected    [➕ Add Defect]  │
│                                                    │
│ 2 field(s) require defect documentation.          │
│ Click "Add Defect" to document details.           │
└────────────────────────────────────────────────────┘
Background: #fef3c7 (yellow-50)
Border-left: #f59e0b (yellow-400) 4px
```

### Field Highlight (when defect value detected)
```
┌───────────────────────────────────┐
│ ⚠️ Defect condition               │ ← Yellow label
├───────────────────────────────────┤
│ Boom Pivot Pins:                  │
│ [EXCESSIVE ▼]                     │
└───────────────────────────────────┘
Ring: ring-2 ring-yellow-400
```

### Modal Severity Indicator
```
When severity = SERVICE_REQUIRED:
┌────────────────────────────────────┐
│ ⚠️ Photos REQUIRED for this level │
└────────────────────────────────────┘
Background: #fee2e2 (red-50)
Border: #fca5a5 (red-300)

When severity = MINOR:
┌────────────────────────────────────┐
│ 📷 Photos strongly recommended     │
└────────────────────────────────────┘
Background: #fef3c7 (yellow-50)
Border: #fde047 (yellow-300)
```

---

## TypeScript Interfaces

### DefectData
```typescript
export interface DefectData {
  defect_id: string;
  title: string;
  severity: 'SAFE' | 'MINOR' | 'SERVICE_REQUIRED' | 'UNSAFE_OUT_OF_SERVICE';
  description: string;
  component?: string;
  location?: string;
  photo_evidence?: string[];
  corrective_action?: string;
  standard_reference?: string;
}
```

### DefectSchema (from template)
```typescript
interface DefectSchema {
  defect_id_format: string; // "UUID"
  fields: Array<{
    field_id: string;
    type: string;
    required: boolean;
    max_length?: number;
    enum_ref?: string;
    conditionally_required_if?: {
      field: string;
      values: string[];
    };
    help_text?: string;
  }>;
}
```

---

## Backend Contract

### What Frontend Sends
```json
// PATCH /api/inspections/{id}/save_step/
{
  "step_key": "bolts_fasteners",
  "field_data": {
    "structural_bolts_condition": "NONE",
    "boom_pivot_pins_condition": "EXCESSIVE",
    "defects": [
      {
        "defect_id": "uuid-1",
        "title": "Excessive wear on boom pivot pins",
        "severity": "SERVICE_REQUIRED",
        "description": "...",
        "component": "Boom Pivot Pins",
        "location": "Driver side...",
        "photo_evidence": ["photo1.jpg", "photo2.jpg"],
        "corrective_action": "...",
        "standard_reference": "..."
      }
    ]
  },
  "validate": false
}
```

### What Backend Should Do
1. Store in `InspectionRun.step_data[step_key]`
2. On finalization, convert defects array to `InspectionDefect` records
3. Map severity: `SERVICE_REQUIRED` → `MAJOR`
4. Store photos in `defect_details.photos`

---

## Testing Checklist

### Component Tests
- [ ] AddDefectModal validation
  - [ ] Required fields enforced
  - [ ] Photo required when severity = SERVICE_REQUIRED
  - [ ] Photo required when severity = UNSAFE_OUT_OF_SERVICE
  - [ ] Photo suggested when severity = MINOR
  - [ ] Character limits enforced
  - [ ] Edit mode pre-populates correctly

- [ ] StepDefectsList rendering
  - [ ] Severity colors correct
  - [ ] Photo count displays
  - [ ] Edit/Delete buttons work
  - [ ] Empty state when no defects

- [ ] VisualInspectionStep defect detection
  - [ ] Detects defect trigger values
  - [ ] Highlights correct fields
  - [ ] Alert banner shows/hides correctly
  - [ ] Pre-populates modal from field
  - [ ] Defects array updates in step values

### Integration Tests
- [ ] Complete defect capture flow
  - [ ] Select EXCESSIVE → defect alert appears
  - [ ] Add defect → modal opens
  - [ ] Fill defect → validation works
  - [ ] Save defect → appears in list
  - [ ] Edit defect → modal pre-populated
  - [ ] Delete defect → removes from list
  - [ ] Auto-save → defects persist

- [ ] Multi-defect scenario
  - [ ] Can add multiple defects per step
  - [ ] Each defect has unique ID
  - [ ] All defects save correctly

- [ ] Photo upload
  - [ ] Photos upload successfully
  - [ ] Photos display in defect card
  - [ ] Photos save in step_data
  - [ ] Required photo validation blocks save

### Edge Cases
- [ ] No defect_schema (falls back to basic mode)
- [ ] Step without ADD_DEFECT_ITEMS mode
- [ ] Defects from previous save load correctly
- [ ] Navigation with unsaved defect (auto-save)
- [ ] Disabled mode (view-only) hides buttons

---

## Future Enhancements

### Phase 2
1. **Photo Management**
   - Lightbox/gallery view for photos
   - Photo annotation/markup
   - Photo comparison (before/after)

2. **Defect Templates**
   - Common defect library
   - Auto-suggest titles based on component
   - Quick-add buttons for common issues

3. **Enhanced Validation**
   - Warn if defect condition but no defect added
   - Require defect documentation before navigation
   - Validation summary before finalization

4. **Bulk Operations**
   - Copy defect to multiple steps
   - Merge similar defects
   - Export defects to CSV

---

## Files Modified/Created

### Created
1. `frontend/src/features/inspections/steps/AddDefectModal.tsx` (392 lines)
2. `frontend/src/features/inspections/steps/StepDefectsList.tsx` (137 lines)

### Modified
1. `frontend/src/features/inspections/steps/VisualInspectionStep.tsx`
   - Added defect capture logic (~200 lines added)
   - Defect detection and highlighting
   - Modal management
   - Defects array handling

2. `frontend/src/features/inspections/steps/StepRenderer.tsx`
   - Added `schemas` prop
   - Extract and pass `defectSchema` to VisualInspectionStep

3. `frontend/src/features/inspections/InspectionExecutePage.tsx`
   - Added `schemas` to template interface
   - Extract schemas from template_snapshot
   - Pass schemas to StepRenderer

---

## Success Metrics

✅ **Functionality:**
- Defects can be added with all 8 schema fields
- Photo requirements enforced based on severity
- Defects display in step with edit/delete
- Defects save to step_data correctly

✅ **User Experience:**
- Clear visual indicators for defect conditions
- Intuitive workflow (assess → alert → add → review)
- Mobile-friendly modal design
- Character counters prevent data loss

✅ **Data Quality:**
- Structured defect data for work orders
- Photos captured and linked
- Rich corrective action documentation
- Standard references for compliance

---

**Status:** ✅ Complete and ready for testing
**Next Step:** Backend processing of defects array on inspection finalization
