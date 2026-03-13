# Phase 1: Inspection Execution Implementation Plan

**Goal:** Build the core inspection execution workflow - the heart of the application
**Timeline:** 3-4 weeks
**Priority:** 🔴 CRITICAL

---

## Executive Summary

This plan breaks down Phase 1 into **8 incremental milestones**, each building on the previous. We'll use **atomic components** and follow existing patterns from the Customers/Assets modules to maintain consistency and minimize custom code.

---

## Architecture Overview

### State Management Strategy
- **React Query** for server state (loading templates, saving steps, auto-save)
- **Local useState** for inspection execution state (current step, field values, draft data)
- **No Zustand** - keep it simple like VehicleForm/CustomerForm

### Component Hierarchy
```
InspectionExecutePage
├── InspectionHeader (progress, asset info)
├── InspectionStepper (step navigation)
├── StepRenderer (routes to step type)
│   ├── SetupStep
│   ├── VisualInspectionStep
│   ├── FunctionTestStep
│   ├── MeasurementStep
│   └── DefectCaptureStep
│       └── FieldRenderer (renders fields)
│           ├── TextInput (atomic)
│           ├── TextArea (atomic)
│           ├── Select (atomic)
│           ├── NumberInput (atomic)
│           ├── BooleanField (new atomic)
│           ├── PhotoField (new atomic)
│           └── EnumField (new atomic)
└── InspectionActions (Save & Exit, Previous, Next, Complete)
```

---

## Field Types & Step Types Reference

### Field Types (7 types from backend)
From `apps/inspections/schemas/template_schema.py`:
1. **BOOLEAN** - Yes/No, Pass/Fail checkboxes
2. **TEXT** - Short text input
3. **TEXT_AREA** - Multi-line text (was TEXTAREA in old format)
4. **NUMBER** - Numeric input with min/max/precision
5. **ENUM** - Single choice dropdown
6. **CHOICE_MULTI** - Multiple choice checkboxes
7. **PHOTO** - Photo upload (was ATTACHMENTS in old format)

### Step Types (5 types)
From `apps/inspections/schemas/template_schema.py`:
1. **SETUP** - Pre-inspection setup questions
2. **VISUAL_INSPECTION** - Visual checks
3. **FUNCTION_TEST** - Operational tests
4. **MEASUREMENT** - Measurements with structured data
5. **DEFECT_CAPTURE** - Record defects/issues

---

## 8-Milestone Implementation Plan

### ✅ Milestone 1: Field Renderer Foundation (8-10 hours)
**Goal:** Create atomic field components that match backend field types

**Tasks:**
1. Create `BooleanField.tsx` atomic component
   - Props: `value`, `onChange`, `label`, `required`, `disabled`
   - Style: Match existing FormField pattern with checkbox/radio options

2. Create `PhotoField.tsx` atomic component
   - Props: `value`, `onChange`, `label`, `required`, `disabled`, `multiple`
   - Features: File input, preview thumbnails, remove photo
   - Use native file input (no fancy camera APIs yet)

3. Create `NumberInput.tsx` atomic component
   - Extend TextInput with type="number"
   - Props: Add `min`, `max`, `precision`
   - Validation: Show error if out of range

4. Create `EnumField.tsx` atomic component
   - Use existing Select component
   - Props: `value`, `onChange`, `label`, `options`, `required`

5. Create `ChoiceMultiField.tsx` atomic component
   - Checkbox group
   - Props: `value[]`, `onChange`, `label`, `options`, `required`

6. Create `FieldRenderer.tsx` component
   - Takes `field` prop (SchemaField from template)
   - Routes to correct component based on `field.type`
   - Handles all 7 field types
   - Wraps each in FormField molecule for consistent labels/errors

**Files Created:**
```
components/atoms/
├── BooleanField.tsx
├── PhotoField.tsx
├── NumberInput.tsx
├── EnumField.tsx
└── ChoiceMultiField.tsx

features/inspections/
└── FieldRenderer.tsx
```

**Testing:** Create a test page that renders all 7 field types

**Deliverable:** Can render any field from a template

---

### ✅ Milestone 2: Step Renderer Foundation (10-12 hours)
**Goal:** Create step components for all 5 step types

**Tasks:**
1. Create `StepHeader.tsx` component (shared)
   - Display: Step title, standard reference, step X of Y
   - Props: `step`, `currentIndex`, `totalSteps`

2. Create `SetupStep.tsx`
   - Renders step.fields using FieldRenderer
   - Simple grid layout
   - No special logic

3. Create `VisualInspectionStep.tsx`
   - Renders step.fields using FieldRenderer
   - Same as SetupStep initially

4. Create `FunctionTestStep.tsx`
   - Renders step.fields using FieldRenderer
   - Same as SetupStep initially

5. Create `MeasurementStep.tsx`
   - Renders step.fields using FieldRenderer
   - Support measurement_sets (grouped fields)
   - Table-like layout for measurements

6. Create `DefectCaptureStep.tsx`
   - Renders defect capture form
   - List existing defects
   - "Add Defect" button

7. Create `StepRenderer.tsx` component
   - Takes `step` prop
   - Routes to correct step component based on `step.type`

**Files Created:**
```
features/inspections/steps/
├── StepHeader.tsx
├── StepRenderer.tsx
├── SetupStep.tsx
├── VisualInspectionStep.tsx
├── FunctionTestStep.tsx
├── MeasurementStep.tsx
└── DefectCaptureStep.tsx
```

**Testing:** Manually render each step type with sample data

**Deliverable:** Can render any step from a template

---

### ✅ Milestone 3: Inspection Execute Page Shell (12-15 hours)
**Goal:** Build the main execution page with navigation (no saving yet)

**Tasks:**
1. Create `InspectionExecutePage.tsx`
   - Load inspection run from API: `GET /api/inspections/{id}/`
   - Load template from API: `GET /api/templates/{template_key}/`
   - Parse template JSON (already validated by backend)
   - Local state: `currentStepIndex`, `stepData`, `isLoading`, `error`

2. Create `InspectionHeader.tsx`
   - Display: Asset name, template name, inspector name
   - Progress bar: X of Y steps complete
   - Status badge (In Progress, Draft, etc.)

3. Create `InspectionStepper.tsx`
   - Visual stepper showing all steps
   - Highlight current step
   - Click to jump to step (if allowed)
   - Responsive for mobile (collapse to just current step)

4. Create `InspectionActions.tsx`
   - Buttons: "Previous", "Next", "Save & Exit", "Complete Inspection"
   - Disable Previous on first step
   - Disable Next on last step
   - Show "Complete" instead of "Next" on last step

5. Implement navigation logic
   - Next: Increment currentStepIndex
   - Previous: Decrement currentStepIndex
   - Handle step boundaries
   - No validation yet - just navigation

**Files Created:**
```
features/inspections/
├── InspectionExecutePage.tsx
├── InspectionHeader.tsx
├── InspectionStepper.tsx
└── InspectionActions.tsx
```

**API Endpoints Used:**
```
GET /api/inspections/{id}/                    # Get inspection run
GET /api/templates/{template_key}/            # Get template
```

**Testing:**
- Navigate through a real template (frequent_inspection)
- Verify all steps render correctly
- Test Previous/Next buttons

**Deliverable:** Can navigate through an inspection (read-only)

---

### ✅ Milestone 4: Step Data Management (8-10 hours)
**Goal:** Track field values as user fills out the form

**Tasks:**
1. Add state management to InspectionExecutePage
   ```typescript
   const [stepData, setStepData] = useState<Record<string, any>>({});
   // stepData format: { "step_key.field_id": value, ... }
   ```

2. Create `useStepData` hook
   - `getFieldValue(stepKey, fieldId): any`
   - `setFieldValue(stepKey, fieldId, value): void`
   - `getStepValues(stepKey): Record<string, any>`
   - Handles nested keys like "controls_check.operation"

3. Wire up FieldRenderer to stepData
   - Pass `value` from stepData
   - Pass `onChange` that updates stepData
   - Handle all field type conversions (string→number, etc.)

4. Display current step data (dev mode)
   - Show JSON of current step values
   - Help with debugging

**Files Created:**
```
features/inspections/hooks/
└── useStepData.ts
```

**Testing:**
- Fill out fields and verify state updates
- Navigate between steps and verify values persist
- Check browser console for data structure

**Deliverable:** Form is interactive, values are tracked locally

---

### ✅ Milestone 5: Manual Save & Draft Persistence (12-15 hours)
**Goal:** Save step data to backend, load draft data on page load

**Tasks:**
1. Create `inspections.api.ts` methods
   ```typescript
   saveStep(inspectionId, stepKey, data): Promise<void>
   getDraft(inspectionId): Promise<DraftData>
   ```

2. Implement "Save & Exit" button
   - Save current step data
   - Show success message
   - Navigate back to inspections list
   - Handle errors gracefully

3. Load draft data on mount
   - GET inspection to check if it has step_responses
   - Populate stepData with existing values
   - Show "Resuming draft..." message

4. Add loading states
   - Show spinner while saving
   - Disable form during save
   - Show "Saved" checkmark on success

5. Handle navigation blocking
   - Warn if user has unsaved changes
   - "You have unsaved changes. Save before leaving?"

**API Endpoints Used:**
```
POST /api/inspections/{id}/save_step/         # Save step data
GET /api/inspections/{id}/                    # Load draft data
```

**Files Updated:**
```
frontend/src/api/inspections.api.ts           # Add save methods
features/inspections/InspectionExecutePage.tsx # Save logic
features/inspections/InspectionActions.tsx     # Save button
```

**Testing:**
- Fill out step, click "Save & Exit"
- Verify data saved in database
- Reload page, verify draft data loads
- Test error handling (network failure)

**Deliverable:** Manual save works, draft persistence works

---

### ✅ Milestone 6: Auto-Save (5-8 hours)
**Goal:** Automatically save draft every 30 seconds

**Tasks:**
1. Create `useAutoSave` hook
   - Takes: `inspectionId`, `currentStepKey`, `stepData`, `enabled`
   - Debounces changes (30 seconds)
   - Only saves if data changed since last save
   - Shows "Saving..." / "Saved" indicator

2. Add auto-save indicator to header
   - Icon that shows: Saved ✓, Saving..., Error ⚠️
   - Last saved timestamp: "Saved 2 minutes ago"

3. Pause auto-save when offline
   - Detect navigator.onLine
   - Queue saves when offline
   - Flush queue when back online

**Files Created:**
```
features/inspections/hooks/
└── useAutoSave.ts

features/inspections/
└── AutoSaveIndicator.tsx
```

**Testing:**
- Fill out form, wait 30 seconds, verify auto-save
- Disconnect network, verify saves queue
- Reconnect, verify queued saves flush

**Deliverable:** Auto-save works reliably

---

### ✅ Milestone 7: Validation & Blocking Steps (10-12 hours)
**Goal:** Validate fields, handle blocking steps, prevent invalid completion

**Tasks:**
1. Create `useStepValidation` hook
   - Validate required fields
   - Validate field constraints (min/max, enum values)
   - Validate based on step.validations (backend rules)
   - Return: `{ isValid, errors }`

2. Implement blocking logic
   - If step has `blocking_fail: true`
   - If any field has failing value
   - Show warning: "Cannot proceed - this step failed"
   - Disable "Next" button

3. Implement "Complete Inspection" validation
   - Check all required steps completed
   - Check no blocking failures
   - Show validation summary before finalizing

4. Add field-level validation errors
   - Real-time validation as user types
   - Show red border and error message below field
   - Clear error when fixed

5. Add step-level validation errors
   - Show error summary at top of step
   - List all validation errors
   - Jump to first error field

**Files Created:**
```
features/inspections/hooks/
└── useStepValidation.ts

features/inspections/
└── ValidationSummary.tsx
```

**API Endpoints Used:**
```
POST /api/inspections/{id}/finalize/          # Complete inspection
```

**Testing:**
- Try to skip required fields
- Try to proceed past blocking failure
- Try to complete inspection with errors
- Verify all validation rules work

**Deliverable:** Validation prevents invalid inspections

---

### ✅ Milestone 8: Photo Capture & Defects (15-20 hours)
**Goal:** Full photo upload and defect recording

**Tasks:**
1. Enhance PhotoField component
   - Camera capture on mobile (if available)
   - File upload on desktop
   - Multiple photo support
   - Preview before upload
   - Compress images before upload (reduce size)

2. Create photo upload API
   ```typescript
   uploadPhoto(inspectionId, stepKey, fieldId, file): Promise<{ url }>
   deletePhoto(inspectionId, photoId): Promise<void>
   ```

3. Create defect capture workflow
   - "Add Defect" button opens modal
   - DefectCaptureModal with form fields from defect_schema
   - Fields: title, severity, location, photos, notes
   - Save defect via API
   - Show defects list in step

4. Auto-defect generation
   - Check step.auto_defect_on conditions
   - When condition met, auto-create defect
   - Show notification: "Defect automatically created"

5. Handle defect photos
   - Same photo upload as regular fields
   - Associate photos with defects
   - Show thumbnails in defect list

**Files Created:**
```
features/inspections/
├── DefectCaptureModal.tsx
├── DefectsList.tsx
└── PhotoPreview.tsx

frontend/src/api/
└── photos.api.ts
```

**API Endpoints Used:**
```
POST /api/inspections/{id}/upload_photo/      # Upload photo
DELETE /api/photos/{id}/                      # Delete photo
POST /api/inspections/{id}/defects/           # Create defect
GET /api/inspections/{id}/defects/            # List defects
```

**Testing:**
- Upload photos on desktop
- Take photos on mobile (if possible)
- Create defects manually
- Verify auto-defects trigger
- Test photo compression

**Deliverable:** Full photo and defect support

---

## Implementation Sequence

### Week 1: Foundation
- Day 1-2: Milestone 1 (Field Renderer)
- Day 3-4: Milestone 2 (Step Renderer)
- Day 5: Milestone 3 (Execute Page Shell)

### Week 2: Interactivity
- Day 1: Milestone 4 (Step Data Management)
- Day 2-3: Milestone 5 (Manual Save)
- Day 4: Milestone 6 (Auto-Save)
- Day 5: Testing & bug fixes

### Week 3: Validation & Media
- Day 1-2: Milestone 7 (Validation)
- Day 3-5: Milestone 8 (Photos & Defects)

### Week 4: Polish & Testing
- Day 1-2: End-to-end testing with real templates
- Day 3: Bug fixes and edge cases
- Day 4: Performance optimization
- Day 5: Documentation and handoff

---

## Success Criteria

### Must Have (MVP)
- ✅ Can load any inspection template
- ✅ Can navigate through all steps
- ✅ Can fill out all field types
- ✅ Auto-save works
- ✅ Draft persistence works
- ✅ Validation prevents invalid data
- ✅ Can upload photos
- ✅ Can record defects
- ✅ Can complete inspection

### Nice to Have (Post-MVP)
- ⏳ Offline support (queue saves)
- ⏳ Camera capture on mobile
- ⏳ PDF generation preview
- ⏳ Undo/redo functionality
- ⏳ Copy from previous inspection

---

## Risk Mitigation

### Risk 1: Complex Template Logic
**Mitigation:** Start with simplest template (frequent_inspection), then test with more complex ones

### Risk 2: Photo Upload Performance
**Mitigation:** Implement client-side image compression, lazy loading

### Risk 3: Validation Complexity
**Mitigation:** Validate one level at a time (field → step → inspection)

### Risk 4: Auto-Save Conflicts
**Mitigation:** Use optimistic updates, queue conflicting saves

---

## Development Best Practices

1. **Atomic Components First** - Reuse TextInput, Select, FormField, etc.
2. **Type Safety** - Create TypeScript interfaces for all data structures
3. **Test As You Go** - Test each milestone before moving to next
4. **Use Existing Patterns** - Follow VehicleForm/CustomerForm patterns
5. **Mobile First** - Inspectors use tablets, so test on mobile viewport
6. **Error Handling** - Every API call needs try/catch and user feedback
7. **Loading States** - Show spinners/skeletons while loading
8. **Accessibility** - Use semantic HTML, ARIA labels, keyboard navigation

---

## Next Steps After Phase 1

Once Phase 1 is complete:
- **Phase 2:** Inspection Results & PDF viewing (2 weeks)
- **Phase 3:** Work Orders from defects (2 weeks)
- **Phase 4:** Dashboard & Analytics (1 week)

---

**Total Estimated Effort:** 80-100 hours (3-4 weeks for 1 developer)
**Priority:** CRITICAL - Blocks all inspection functionality
**Dependencies:** None - can start immediately
