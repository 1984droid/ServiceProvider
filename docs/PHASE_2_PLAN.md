# Phase 2: Inspection Review & Work Order Generation

**Status:** 📋 PLANNING
**Est. Duration:** 2-3 weeks
**Prerequisites:** Phase 1 (Inspection Execution) ✅ COMPLETE

---

## Executive Summary

Phase 2 bridges the gap between **inspection completion** and **work order generation**. Inspectors complete inspections in Phase 1, but currently there's no way to:
1. **Review** completed inspections with defects highlighted
2. **Finalize** inspections (make them immutable)
3. **Create work orders** from inspection defects
4. **Track** defect → work order lifecycle

This phase delivers the **Inspection Review UI** and **Work Order Creation Workflow**, enabling the complete inspection-to-repair workflow.

---

## Current State Analysis

### ✅ What We Have (Phase 1)
- **Backend:**
  - InspectionRun model with step_data storage
  - InspectionDefect model with rule evaluation
  - WorkOrder model with polymorphic asset references
  - Rule evaluation engine (14 assertion types)
  - Defect generation service (idempotent)
  - Work order meter update signals

- **Frontend:**
  - Inspection execution page (7 field types, 5 step types)
  - Step navigation with progress tracking
  - Auto-save + manual save functionality
  - Validation and blocking navigation
  - InspectionsListPage with status filtering

- **Testing:**
  - 175 backend tests passing (including 71 rule evaluation tests)
  - Comprehensive coverage of models, services, APIs

### ❌ What's Missing (Phase 2 Scope)
- **No inspection review/finalization UI**
  - Can't see all defects found in an inspection
  - Can't make inspection immutable (finalized state)
  - No signature capture for inspector sign-off

- **No work order creation workflow**
  - Can't create work orders from defects
  - Can't group multiple defects into one WO
  - No WO priority/scheduling UI

- **No defect tracking**
  - Can't see defect status (OPEN → WORK_ORDER_CREATED → RESOLVED)
  - No visual indicators for defect severity
  - No defect photos/details display

- **No inspection PDF export**
  - Can't generate inspection reports
  - No printable/shareable inspection results

---

## Phase 2 Goals

### Primary Objectives
1. **Inspection Finalization Flow** - Inspector reviews, signs, and locks inspection
2. **Defect Review UI** - Visual display of all defects with severity indicators
3. **Work Order Creation** - Select defects → create work order with scheduling
4. **Defect Lifecycle Tracking** - Status updates as work progresses

### Success Criteria
- ✅ Inspector can finalize inspection with signature
- ✅ Once finalized, inspection step_data is immutable
- ✅ All defects clearly visible with severity/location
- ✅ Can create work order from 1 or more defects
- ✅ Defect status updates when work order created
- ✅ Work order links back to source inspection
- ✅ All actions tested (unit + integration)

---

## Architecture Overview

### Data Flow
```
Inspector Completes Inspection (Phase 1)
          ↓
Review Inspection Results (Phase 2 NEW)
          ↓
Sign & Finalize Inspection (Phase 2 NEW)
   ├─→ InspectionRun.finalized_at = now()
   ├─→ InspectionRun.status = 'COMPLETED'
   └─→ step_data becomes IMMUTABLE
          ↓
View Defects List (Phase 2 NEW)
   ├─→ CRITICAL (red badge)
   ├─→ MAJOR (orange badge)
   ├─→ MINOR (yellow badge)
   └─→ ADVISORY (blue badge)
          ↓
Select Defects for Repair (Phase 2 NEW)
          ↓
Create Work Order (Phase 2 NEW)
   ├─→ WorkOrder.source = 'INSPECTION'
   ├─→ WorkOrder.source_inspection_run_id = inspection.id
   ├─→ Link selected defects to work order
   └─→ Defect.status = 'WORK_ORDER_CREATED'
          ↓
Work Order Execution (Phase 3 scope)
```

### Component Architecture
```
frontend/src/features/inspections/
   ├─ InspectionReviewPage.tsx (NEW)
   │     ├─ InspectionReviewHeader.tsx (NEW)
   │     ├─ InspectionStepReview.tsx (NEW)
   │     └─ InspectionDefectsList.tsx (NEW)
   │
   ├─ InspectionFinalize.tsx (NEW)
   │     ├─ SignatureCapture.tsx (NEW)
   │     └─ FinalizeConfirmModal.tsx (NEW)
   │
   └─ DefectToWorkOrderModal.tsx (NEW)
         ├─ DefectSelection.tsx (NEW)
         ├─ WorkOrderScheduling.tsx (NEW)
         └─ WorkOrderPrioritySelector.tsx (NEW)

frontend/src/features/work-orders/ (NEW directory)
   ├─ WorkOrdersListPage.tsx (NEW)
   ├─ WorkOrderDetailPage.tsx (NEW)
   └─ WorkOrderForm.tsx (NEW)
```

---

## Milestones

### Milestone 1: Inspection Review Page
**Goal:** Display completed inspection with read-only step data and defect summary

**Backend Tasks:**
- [ ] Add `GET /api/inspections/{id}/review/` endpoint
  - Returns inspection with expanded step_data
  - Includes defect summary (count by severity)
  - Returns finalization status

**Frontend Tasks:**
- [ ] Create `InspectionReviewPage.tsx`
  - Display all steps in read-only mode
  - Show step completion status
  - Display field values (not editable)

- [ ] Create `InspectionReviewHeader.tsx`
  - Asset info, inspector, date
  - Status badge (DRAFT/IN_PROGRESS/COMPLETED)
  - Defect count summary

- [ ] Create `InspectionStepReview.tsx`
  - Reuse FieldRenderer in read-only mode
  - Visual indicators for failed steps

**Tests:**
- [ ] Review endpoint returns correct data
- [ ] Review page displays all steps
- [ ] Read-only fields cannot be edited

**Deliverables:**
- Inspector can review completed inspection
- All field data visible in clean format
- Est. 2-3 days

---

### Milestone 2: Defect List & Details
**Goal:** Display all defects from inspection with severity, location, photos

**Backend Tasks:**
- [ ] Enhance `GET /api/inspections/{id}/defects/` endpoint
  - Group defects by severity
  - Include evaluation trace
  - Return defect photos if attached

**Frontend Tasks:**
- [ ] Create `InspectionDefectsList.tsx`
  - Severity badges (CRITICAL/MAJOR/MINOR/ADVISORY)
  - Defect title + description
  - Location (module_key.step_key)
  - Status indicator (OPEN/WORK_ORDER_CREATED/RESOLVED)

- [ ] Create `DefectDetailModal.tsx`
  - Full defect details
  - Evaluation trace (rule that generated it)
  - Photos/attachments
  - Edit notes (manual defects only)

**Tests:**
- [ ] Defects grouped correctly by severity
- [ ] Detail modal shows all defect info
- [ ] Manual defects can be edited

**Deliverables:**
- Clear visual display of all defects
- Easy to identify critical issues
- Est. 2-3 days

---

### Milestone 3: Inspection Finalization
**Goal:** Inspector signs and locks inspection, making it immutable

**Backend Tasks:**
- [ ] Add `POST /api/inspections/{id}/finalize/` endpoint
  - Accept signature data (base64 image or signature JSON)
  - Set `finalized_at = now()`
  - Set `status = 'COMPLETED'`
  - Validate all required steps completed
  - Return error if validation fails

- [ ] Add immutability enforcement
  - Prevent step_data updates after finalization
  - Raise ValidationError in model.save()
  - Add database trigger (optional)

**Frontend Tasks:**
- [ ] Create `InspectionFinalize.tsx`
  - "Finalize Inspection" button
  - Signature capture canvas
  - Inspector name confirmation
  - Timestamp display

- [ ] Create `SignatureCapture.tsx`
  - HTML5 canvas for signature
  - Clear/redo functionality
  - Base64 export

- [ ] Create `FinalizeConfirmModal.tsx`
  - Confirmation dialog
  - Warning about immutability
  - Display defect summary
  - Require signature before submitting

**Tests:**
- [ ] Finalize endpoint validates completion
- [ ] Finalized inspections reject updates
- [ ] Signature data persisted correctly
- [ ] Frontend blocks edits after finalization

**Deliverables:**
- Inspections can be finalized with signature
- Immutability enforced backend + frontend
- Clear audit trail
- Est. 3-4 days

---

### Milestone 4: Work Order Creation from Defects
**Goal:** Select defects and create work order with scheduling/priority

**Backend Tasks:**
- [ ] Add `POST /api/work-orders/from-inspection/` endpoint
  - Accept inspection_run_id + defect_ids[]
  - Create WorkOrder
  - Set source='INSPECTION'
  - Link defects to work order
  - Update defect statuses to 'WORK_ORDER_CREATED'
  - Return created work order

- [ ] Add defect linking
  - Option 1: ManyToMany field on WorkOrder
  - Option 2: JSON field with defect_ids
  - Option 3: Separate WorkOrderDefect junction table
  - **Recommendation:** ManyToMany for queryability

**Frontend Tasks:**
- [ ] Create `DefectToWorkOrderModal.tsx`
  - Triggered from inspection review page
  - Lists all OPEN defects
  - Multi-select checkboxes
  - Selected count indicator

- [ ] Create `WorkOrderScheduling.tsx`
  - Title (auto-generated from defects)
  - Description (editable)
  - Priority selector (LOW/NORMAL/HIGH/EMERGENCY)
  - Scheduled date picker
  - Assigned technician (optional)

- [ ] Add "Create Work Order" button to review page
  - Only visible if defects exist
  - Only enabled if inspection finalized
  - Opens DefectToWorkOrderModal

**Tests:**
- [ ] Work order creation endpoint works
- [ ] Defect statuses update correctly
- [ ] Multiple defects can be linked
- [ ] Cannot create WO from non-finalized inspection

**Deliverables:**
- Seamless defect → work order flow
- Work orders properly linked to source inspection
- Est. 3-4 days

---

### Milestone 5: Work Order List & Detail Pages
**Goal:** View and manage work orders created from inspections

**Backend Tasks:**
- [ ] Enhance `GET /api/work-orders/` endpoint
  - Add filtering by status, priority, customer
  - Add sorting by scheduled_date, priority
  - Include asset info in response
  - Include linked defects count

- [ ] Enhance `GET /api/work-orders/{id}/` endpoint
  - Expand asset details
  - Expand customer details
  - Expand linked defects
  - Expand source inspection

**Frontend Tasks:**
- [ ] Create `WorkOrdersListPage.tsx`
  - Table with columns: WO#, Customer, Asset, Priority, Status, Date
  - Filter by status (DRAFT/PENDING/IN_PROGRESS/COMPLETED)
  - Filter by priority
  - Search by WO# or customer
  - Click row → navigate to detail

- [ ] Create `WorkOrderDetailPage.tsx`
  - Header: WO#, status, priority badges
  - Asset info with link
  - Customer info with link
  - Linked defects list with severity
  - Link to source inspection
  - Status timeline (future: audit log)
  - Actions: Start, Complete, Cancel

**Tests:**
- [ ] List page displays work orders correctly
- [ ] Filters work as expected
- [ ] Detail page shows all work order info
- [ ] Links to assets/customers/inspections work

**Deliverables:**
- Complete work order management UI
- Easy navigation between related entities
- Est. 3-4 days

---

### Milestone 6: Defect Status Tracking
**Goal:** Update defect status as work progresses, close the loop

**Backend Tasks:**
- [ ] Add `PATCH /api/defects/{id}/status/` endpoint
  - Accept new status (OPEN/WORK_ORDER_CREATED/RESOLVED)
  - Validate status transitions
  - Add status change audit log (future)

- [ ] Add WorkOrder completion signal
  - When WO status → COMPLETED
  - Update linked defects → RESOLVED
  - Trigger notification (future)

**Frontend Tasks:**
- [ ] Update `InspectionDefectsList.tsx`
  - Show current status with badge
  - Link to work order if exists
  - Disable "Create WO" if already linked

- [ ] Update `DefectDetailModal.tsx`
  - Show status history (future)
  - Link to work order
  - "Mark Resolved" button (manual defects)

**Tests:**
- [ ] Status transitions validated
- [ ] WO completion updates defects
- [ ] UI reflects status correctly

**Deliverables:**
- Complete defect lifecycle tracking
- Automatic status updates
- Est. 2 days

---

### Milestone 7: Integration Testing & Polish
**Goal:** End-to-end testing and UX refinements

**Tasks:**
- [ ] **End-to-End Tests:**
  - Complete inspection → Finalize → Create WO
  - Multi-defect work order creation
  - Work order completion → defect resolution
  - Immutability enforcement

- [ ] **UX Polish:**
  - Loading states for all async operations
  - Error handling with user-friendly messages
  - Success toasts for actions
  - Keyboard shortcuts (ESC to close modals)
  - Responsive design for review pages

- [ ] **Performance:**
  - Optimize defect queries (select_related, prefetch_related)
  - Add pagination to work order list
  - Cache inspection reviews

- [ ] **Documentation:**
  - Update user workflows in docs/
  - API documentation for new endpoints
  - Component documentation
  - Phase 2 completion summary

**Tests:**
- [ ] All 175+ existing tests still pass
- [ ] New integration tests cover workflows
- [ ] Manual QA testing completed

**Deliverables:**
- Production-ready inspection → WO workflow
- Comprehensive documentation
- Est. 2-3 days

---

## Technical Specifications

### New Backend Endpoints

```python
# Inspection Review
GET    /api/inspections/{id}/review/
POST   /api/inspections/{id}/finalize/
GET    /api/inspections/{id}/defects/

# Defect Management
PATCH  /api/defects/{id}/status/
GET    /api/defects/?severity=CRITICAL&status=OPEN

# Work Order Creation
POST   /api/work-orders/from-inspection/
GET    /api/work-orders/
GET    /api/work-orders/{id}/
PATCH  /api/work-orders/{id}/status/
```

### New Database Fields

```python
# InspectionRun (existing model, add fields)
class InspectionRun(BaseModel):
    # ... existing fields ...
    inspector_signature = models.JSONField(null=True)
    # {
    #   'signature_data': 'base64_image_string',
    #   'signed_at': '2026-03-14T10:30:00Z',
    #   'signed_by': 'John Ramirez',
    #   'ip_address': '192.168.1.100'
    # }

# WorkOrder (existing model, add fields)
class WorkOrder(BaseModel):
    # ... existing fields ...
    linked_defects = models.ManyToManyField(
        'inspections.InspectionDefect',
        related_name='work_orders',
        blank=True
    )
```

### Component Contracts

```typescript
// InspectionReviewPage.tsx
interface InspectionReviewPageProps {
  inspectionId: string;
  onNavigateToWorkOrder?: (workOrderId: string) => void;
}

// DefectToWorkOrderModal.tsx
interface DefectToWorkOrderModalProps {
  inspectionId: string;
  defects: InspectionDefect[];
  onWorkOrderCreated: (workOrderId: string) => void;
  onClose: () => void;
}

// WorkOrderDetailPage.tsx
interface WorkOrderDetailPageProps {
  workOrderId: string;
  onNavigateToInspection?: (inspectionId: string) => void;
  onNavigateToAsset?: (assetType: string, assetId: string) => void;
}
```

---

## Data Contract Compliance

### Seed Data Updates Needed
```python
# apps/organization/management/commands/seed_config.py

# Add work order test data
WORK_ORDER_DATA = {
    'from_inspection': {
        'title': 'Repair Critical Defects from ANSI A92.2 Inspection',
        'priority': 'HIGH',
        'status': 'PENDING',
        'scheduled_date': '2026-03-20',
        'description': 'Repair hydraulic leak and structural crack found during inspection.',
    },
}

# Add finalized inspections to seed data
INSPECTION_RUN_DATA = {
    'finalized': {
        'status': 'COMPLETED',
        'finalized_at': '2026-03-14T10:30:00Z',
        'inspector_signature': {
            'signed_by': f"{SeedConfig.EMPLOYEES[0]['first_name']} {SeedConfig.EMPLOYEES[0]['last_name']}",
            'signed_at': '2026-03-14T10:30:00Z',
        },
    },
}
```

### Test Config Updates
```python
# tests/config.py - All new data from seed_config

INSPECTION_RUN_DATA = {
    'finalized': SeedConfig.INSPECTION_RUN_DATA['finalized'],
}

WORK_ORDER_DATA = {
    'from_inspection': SeedConfig.WORK_ORDER_DATA['from_inspection'],
}
```

---

## Risk Mitigation

### Risk 1: Immutability Enforcement
**Risk:** Finalized inspections could be accidentally edited
**Mitigation:**
- Database constraint (trigger) if possible
- Model-level validation in save()
- API-level checks before accepting updates
- Frontend disables edit buttons
- Comprehensive tests for all scenarios

### Risk 2: Defect → Work Order Complexity
**Risk:** Complex many-to-many relationships could cause bugs
**Mitigation:**
- Start with simple 1:1 (one defect → one WO)
- Add multi-select in Milestone 4 after validation
- Thorough integration tests
- Clear error messages for edge cases

### Risk 3: Signature Capture Cross-Browser
**Risk:** HTML5 canvas signature may not work on all devices
**Mitigation:**
- Use proven library (e.g., react-signature-canvas)
- Fallback to text signature if canvas fails
- Test on Chrome, Firefox, Safari, Edge
- Mobile testing on iOS/Android

### Risk 4: Performance with Large Inspections
**Risk:** Inspections with 100+ steps could be slow to load
**Mitigation:**
- Lazy load step details
- Pagination for step list
- Database indexes on frequently queried fields
- Caching for finalized inspections (immutable)

---

## Testing Strategy

### Unit Tests (Target: 50+ new tests)
- [ ] InspectionRun finalization logic
- [ ] Defect status transitions
- [ ] Work order creation from defects
- [ ] Signature validation
- [ ] Immutability enforcement

### Integration Tests (Target: 15+ tests)
- [ ] Complete inspection → finalize → create WO
- [ ] Multi-defect work order
- [ ] Work order completion → defect resolution
- [ ] Defect status lifecycle

### Frontend Tests (Target: 30+ component tests)
- [ ] InspectionReviewPage renders correctly
- [ ] SignatureCapture works
- [ ] DefectToWorkOrderModal validates input
- [ ] WorkOrdersListPage filters/sorts
- [ ] Navigation between related entities

### Manual QA Checklist
- [ ] Inspector can complete full workflow
- [ ] Finalized inspections cannot be edited
- [ ] Work orders created with correct data
- [ ] Defect statuses update correctly
- [ ] All links/navigation work
- [ ] Error messages are clear
- [ ] Loading states display properly
- [ ] Mobile responsive (bonus)

---

## Success Metrics

### Code Quality
- ✅ All tests passing (target: 225+ total tests)
- ✅ No hardcoded values (all from seed config)
- ✅ TypeScript strict mode passing
- ✅ ESLint/Prettier compliance
- ✅ Zero console errors/warnings

### User Experience
- ✅ < 2 seconds to load inspection review
- ✅ < 1 second to finalize inspection
- ✅ < 3 seconds to create work order
- ✅ Clear visual feedback for all actions
- ✅ Accessible (keyboard navigation works)

### Documentation
- ✅ Phase 2 completion summary written
- ✅ API endpoints documented
- ✅ Component architecture documented
- ✅ User workflow diagrams updated
- ✅ Seed data includes Phase 2 scenarios

---

## Timeline Estimate

### Week 1 (Days 1-5)
- Milestone 1: Inspection Review Page (2-3 days)
- Milestone 2: Defect List & Details (2-3 days)

### Week 2 (Days 6-10)
- Milestone 3: Inspection Finalization (3-4 days)
- Milestone 4: Work Order Creation (start, 1-2 days)

### Week 3 (Days 11-15)
- Milestone 4: Work Order Creation (complete, 1-2 days)
- Milestone 5: Work Order List & Detail (3-4 days)

### Week 4 (Days 16-20, if needed)
- Milestone 6: Defect Status Tracking (2 days)
- Milestone 7: Integration Testing & Polish (2-3 days)

**Total Estimate:** 15-20 days (3-4 weeks)

---

## Dependencies

### External Libraries (Frontend)
- `react-signature-canvas` - Signature capture (5.3 KB)
- `date-fns` - Date formatting (already installed)
- `@tanstack/react-query` - Already in use

### Internal Dependencies
- ✅ Phase 1 complete (inspection execution)
- ✅ InspectionRun/InspectionDefect models exist
- ✅ WorkOrder model exists
- ✅ Rule evaluation working
- ⏳ Backend API endpoints need expansion

---

## Post-Phase 2 Capabilities

Once Phase 2 is complete, users will be able to:

1. **Inspectors:**
   - Execute inspections (Phase 1) ✅
   - Review completed inspections
   - Sign and finalize inspections
   - See all defects found
   - Create work orders from defects

2. **Service Managers:**
   - View all work orders
   - See which WOs came from inspections
   - Track defect resolution
   - Schedule repairs based on severity

3. **System:**
   - Enforce inspection immutability
   - Track complete defect lifecycle
   - Link inspections → defects → work orders
   - Provide audit trail for compliance

---

## Next Steps (Phase 3 Preview)

Phase 3 will focus on **Work Order Execution**:
- Work order scheduling/assignment
- Technician mobile interface
- Parts tracking
- Labor hour tracking
- Work order completion with photos
- Meter updates (odometer/engine hours)
- Invoice generation (future)

But first, let's nail Phase 2! 🎯

---

## Notes & Considerations

### Design Philosophy
- **No corners cut** - Follow Phase 1 quality standards
- **Config-driven** - All test data from seed_config
- **Defensive coding** - Validate everything
- **User-focused** - Clear feedback, no jargon

### Communication Plan
- Daily standup (if team)
- Demo after each milestone
- Code review before merge
- User feedback sessions

### Rollout Strategy
- Deploy to staging after Milestone 3
- User acceptance testing
- Fix critical bugs before proceeding
- Production deployment after Milestone 7

---

**Version:** 1.0
**Author:** System Analysis
**Date:** 2026-03-14
**Status:** Ready for Review & Approval
