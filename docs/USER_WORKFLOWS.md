# User Workflows

Complete workflow documentation for NEW_BUILD_STARTER inspection and work order system.

**Version:** 2.0 (Phase 5 Complete)
**Last Updated:** 2026-03-12

---

## Table of Contents

1. [Inspection Workflows](#inspection-workflows)
2. [Defect Management Workflows](#defect-management-workflows)
3. [Work Order Workflows](#work-order-workflows)
4. [Complete End-to-End Workflows](#complete-end-to-end-workflows)
5. [Common Patterns](#common-patterns)

---

## Inspection Workflows

### Workflow 1: Create and Execute Inspection

**Actors:** Field Inspector, System

**Steps:**

1. **Create Inspection**
   ```http
   POST /api/inspections/
   ```
   - Select customer and asset (vehicle or equipment)
   - Choose inspection template (e.g., "ansi_a92_2_2021_annual_aerial_vehicle")
   - Set inspector name and start time
   - Provide template snapshot
   - Status: DRAFT

2. **Execute Inspection**
   ```http
   PATCH /api/inspections/{id}/
   ```
   - Update status to IN_PROGRESS
   - Record step responses in `step_data`
   - Add photos and measurements to defect_details
   - Save progress incrementally (system allows partial saves)

3. **Complete Inspection**
   ```http
   PATCH /api/inspections/{id}/
   ```
   - Update status to COMPLETED
   - Set `finalized_at` timestamp
   - Add inspector signature (optional)
   - **System locks inspection** - step_data, template_snapshot, and status become immutable

4. **Evaluate Defect Rules** (Automatic or Manual)
   ```http
   POST /api/inspections/{id}/evaluate_rules/
   ```
   - System analyzes step_data against rule conditions
   - Creates InspectionDefect records for failures
   - Uses defect_identity hash to prevent duplicates

**Business Rules:**
- Inspections can be saved at any time during IN_PROGRESS status
- Once finalized_at is set, inspection becomes immutable for audit compliance
- Status progression is one-way: DRAFT → IN_PROGRESS → COMPLETED
- Rule evaluation can be triggered multiple times on DRAFT/IN_PROGRESS inspections
- Re-evaluation updates existing defects rather than creating duplicates (idempotency)

**Example:**
```json
// Step 1: Create inspection
{
  "customer": "acme-uuid",
  "asset_type": "VEHICLE",
  "asset_id": "truck-t101-uuid",
  "template_key": "ansi_a92_2_2021_annual_aerial_vehicle",
  "started_at": "2025-01-15T08:00:00Z",
  "inspector_name": "John Smith",
  "template_snapshot": { "procedure": {...} }
}

// Step 2: Execute - record responses
{
  "status": "IN_PROGRESS",
  "step_data": {
    "visual_inspection.hydraulic_leaks": {
      "response": "FAIL",
      "notes": "Hydraulic leak at boom cylinder",
      "photos": ["photo_uuid_1"]
    },
    "visual_inspection.structural_damage": {
      "response": "PASS",
      "notes": "No structural damage observed"
    }
  }
}

// Step 3: Complete and finalize
{
  "status": "COMPLETED",
  "finalized_at": "2025-01-15T10:30:00Z",
  "inspector_signature": {
    "signature_data": "base64_image",
    "signed_at": "2025-01-15T10:30:00Z",
    "signed_by": "John Smith",
    "ip_address": "192.168.1.100"
  }
}
```

---

### Workflow 2: Review Inspection Results

**Actors:** Shop Manager, Service Advisor

**Steps:**

1. **List Completed Inspections**
   ```http
   GET /api/inspections/?status=COMPLETED&customer={uuid}
   ```
   - View all completed inspections for a customer
   - Sort by finalized_at to see most recent first

2. **View Inspection Detail**
   ```http
   GET /api/inspections/{id}/
   ```
   - Review all step responses
   - Check defect_count and critical_defect_count
   - View inspector signature and notes

3. **View Associated Defects**
   ```http
   GET /api/inspections/{id}/defects/
   ```
   - Filter by severity (CRITICAL, MAJOR, MINOR, ADVISORY)
   - Check defect status (OPEN, WORK_ORDER_CREATED, RESOLVED)
   - Review defect details, photos, and measurements

**Business Rules:**
- Completed inspections show defect counts in list view
- Critical defects are highlighted for immediate attention
- Inspection data is immutable once finalized (audit trail)

---

## Defect Management Workflows

### Workflow 3: Manual Defect Creation

**Actors:** Inspector, Shop Manager

**Steps:**

1. **Create Manual Defect**
   ```http
   POST /api/defects/
   ```
   - Link to inspection_run
   - Generate defect_identity (SHA256 hash)
   - Set severity (CRITICAL, MAJOR, MINOR, ADVISORY)
   - Provide title, description, and details
   - Status defaults to OPEN

2. **Update Defect Details**
   ```http
   PATCH /api/defects/{id}/
   ```
   - Add photos or measurements
   - Update description with more details
   - Adjust severity if needed

**Business Rules:**
- Manual defects are for edge cases not caught by rules
- defect_identity must be unique (64-character SHA256 hash)
- Manual defects follow the same workflow as rule-generated defects

**Example:**
```json
{
  "inspection_run": "inspection-uuid",
  "defect_identity": "a1b2c3d4e5f6...",  // SHA256 hash
  "module_key": "visual_inspection",
  "step_key": "paint_condition",
  "severity": "MINOR",
  "title": "Paint Chipping on Boom",
  "description": "Minor paint chipping observed on boom extension, no structural concern",
  "defect_details": {
    "location": "Boom extension section 2",
    "photos": []
  }
}
```

---

### Workflow 4: Track Defect Resolution

**Actors:** Service Advisor, Shop Manager

**Steps:**

1. **View Open Defects**
   ```http
   GET /api/defects/?status=OPEN&severity=CRITICAL
   ```
   - Filter by severity to prioritize critical issues
   - View defects that need work orders

2. **Check Defect Work Orders**
   ```http
   GET /api/defects/{id}/
   ```
   - View linked work orders
   - Check work order status and progress

3. **Verify Resolution**
   - Work order completion automatically updates defect status to RESOLVED
   - Review defect_details for resolution notes

**Business Rules:**
- Defect status flow: OPEN → WORK_ORDER_CREATED → RESOLVED
- Status updates are bidirectional with work orders via signals
- Defects can be linked to multiple work orders (many-to-many)

---

## Work Order Workflows

### Workflow 5: Auto-Generate Work Orders from Inspection

**Actors:** Service Advisor, Shop Manager, System

**Steps:**

1. **Generate Work Orders**
   ```http
   POST /api/work-orders/generate_from_defects/
   ```
   - Specify inspection_run_id
   - Set min_severity (default: MAJOR)
   - Enable group_by_location to consolidate related defects
   - Set auto_approve=false for approval workflow

2. **Review Generated Work Orders**
   ```http
   GET /api/work-orders/?source_type=INSPECTION_DEFECT&approval_status=PENDING_APPROVAL
   ```
   - View all pending work orders
   - Check defect count and priority
   - Review estimated scope

3. **Approve Work Orders**
   ```http
   POST /api/work-orders/{id}/approve/
   ```
   - Approve work orders for scheduling
   - Add approval notes
   - System updates approval_status to APPROVED

4. **Assign Work**
   ```http
   PATCH /api/work-orders/{id}/
   ```
   - Assign to employee (assigned_to)
   - Set department
   - Set due_date
   - Update status to PENDING (ready for scheduling)

**Business Rules:**
- Only processes OPEN defects
- Groups defects by service_location if enabled
- Maps severity to priority:
  - CRITICAL → EMERGENCY
  - MAJOR → HIGH
  - MINOR → NORMAL
  - ADVISORY → LOW
- Prevents duplicate work orders using defect_identity
- Uses vocabulary mapping (verb + noun + service_location) for task structure
- Default approval_status is PENDING_APPROVAL

**Example Request:**
```json
{
  "inspection_run_id": "inspection-uuid",
  "min_severity": "MAJOR",
  "group_by_location": true,
  "auto_approve": false
}
```

**Example Response:**
```json
{
  "work_orders_created": 3,
  "defects_processed": 5,
  "defects_skipped": 2,
  "work_orders": [
    {
      "id": "wo-uuid-1",
      "work_order_number": "WO-2025-00123",
      "title": "Repair Hydraulic System",
      "defect_count": 2,
      "priority": "HIGH"
    }
  ]
}
```

---

### Workflow 6: Manual Work Order Creation

**Actors:** Service Advisor, Shop Manager

**Steps:**

1. **Create Work Order**
   ```http
   POST /api/work-orders/
   ```
   - Select customer and asset
   - Set title, description
   - Define task using vocabulary (verb, noun, service_location)
   - Set priority and due_date
   - Set approval_status to APPROVED (skip approval for routine maintenance)
   - Source_type: MANUAL

2. **Assign and Schedule**
   ```http
   PATCH /api/work-orders/{id}/
   ```
   - Assign to employee
   - Set department
   - Update status to PENDING

**Business Rules:**
- Manual work orders bypass defect workflow
- Used for scheduled maintenance, customer requests, PM schedules
- approval_status can be set directly to APPROVED

**Example:**
```json
{
  "customer": "customer-uuid",
  "asset_type": "VEHICLE",
  "asset_id": "vehicle-uuid",
  "title": "Replace Engine Oil",
  "description": "Routine oil change - 5W-40 synthetic, 15 quarts",
  "priority": "NORMAL",
  "due_date": "2025-01-25",
  "approval_status": "APPROVED",
  "verb": "Replace",
  "noun": "Engine Oil",
  "service_location": "Engine",
  "source_type": "MANUAL"
}
```

---

### Workflow 7: Complete Work Order with Meter Updates

**Actors:** Technician, Shop Manager

**Steps:**

1. **Start Work**
   ```http
   PATCH /api/work-orders/{id}/
   ```
   - Update status to IN_PROGRESS
   - Record odometer_at_service and/or engine_hours_at_service

2. **Complete Work**
   ```http
   PATCH /api/work-orders/{id}/
   ```
   - Update status to COMPLETED
   - Set completed_at timestamp
   - Record final meter readings
   - Enter labor_hours, parts_cost, labor_cost
   - Add completion notes

3. **System Actions** (Automatic via signals)
   - Updates linked defects to RESOLVED status
   - Updates asset meters (odometer_miles, engine_hours) if readings are higher
   - Prevents meter rollback (only updates if new value > current value)

**Business Rules:**
- Meter updates only occur on COMPLETED status
- System only increases meters, never decreases (rollback prevention)
- Updates are idempotent (safe to save multiple times)
- Handles both Vehicle (odometer + engine hours) and Equipment (engine hours only)
- Errors updating meters don't block work order completion

**Example Completion:**
```json
{
  "status": "COMPLETED",
  "completed_at": "2025-01-18T14:30:00Z",
  "odometer_at_service": 46500,
  "engine_hours_at_service": 2150,
  "labor_hours": 3.5,
  "parts_cost": 285.50,
  "labor_cost": 350.00,
  "notes": "Replaced cylinder seals, pressure tested hydraulic system at 3000 PSI, no leaks detected"
}
```

**Asset Update (Automatic):**
- Vehicle odometer_miles: 45000 → 46500
- Vehicle engine_hours: 2100 → 2150

---

### Workflow 8: Work Order Approval Process

**Actors:** Service Advisor, Shop Manager, Customer

**Steps:**

1. **Review Pending Work Orders**
   ```http
   GET /api/work-orders/?approval_status=PENDING_APPROVAL
   ```
   - View work orders awaiting approval
   - Filter by customer or priority

2. **Approve Work Order**
   ```http
   POST /api/work-orders/{id}/approve/
   ```
   - Add approval notes
   - System updates approval_status to APPROVED
   - Work order becomes available for scheduling

3. **Reject Work Order** (if customer declines)
   ```http
   POST /api/work-orders/{id}/reject/
   ```
   - Provide rejection reason
   - System updates approval_status to REJECTED
   - Linked defects remain in WORK_ORDER_CREATED status

**Business Rules:**
- Only PENDING_APPROVAL work orders can be approved/rejected
- Approval is separate from work order status
- REJECTED work orders are not deleted (audit trail)
- Customer can change mind later - manually update approval_status

---

### Workflow 9: Cancel Work Order

**Actors:** Service Advisor, Shop Manager

**Steps:**

1. **Cancel Work Order**
   ```http
   PATCH /api/work-orders/{id}/
   ```
   - Update status to CANCELLED
   - Provide reason in notes

2. **System Actions** (Automatic via signals)
   - Updates linked defects status back to OPEN
   - Allows defects to be included in future work orders

**Business Rules:**
- Cancelled work orders remain in system (audit trail)
- Defects revert to OPEN status for re-processing
- Can cancel at any stage before COMPLETED

---

## Complete End-to-End Workflows

### Workflow 10: Inspection to Repair - Complete Flow

**Actors:** Inspector, Service Advisor, Shop Manager, Technician

**Complete End-to-End Process:**

```
1. Inspector performs inspection
   POST /api/inspections/
   PATCH /api/inspections/{id}/ (record responses)
   PATCH /api/inspections/{id}/ (finalize)

2. System evaluates rules
   POST /api/inspections/{id}/evaluate_rules/
   → Creates 3 defects: 2 MAJOR, 1 MINOR

3. Service Advisor generates work orders
   POST /api/work-orders/generate_from_defects/
   {
     "inspection_run_id": "uuid",
     "min_severity": "MAJOR",
     "group_by_location": true
   }
   → Creates 1 work order (2 MAJOR defects grouped by location)
   → Skips 1 MINOR defect (below threshold)

4. Shop Manager approves work order
   POST /api/work-orders/{wo-uuid}/approve/
   → approval_status: PENDING_APPROVAL → APPROVED

5. Shop Manager assigns work
   PATCH /api/work-orders/{wo-uuid}/
   {
     "assigned_to": "technician-uuid",
     "department": "hydraulics-dept-uuid",
     "due_date": "2025-01-20",
     "status": "PENDING"
   }

6. Technician starts work
   PATCH /api/work-orders/{wo-uuid}/
   {
     "status": "IN_PROGRESS",
     "odometer_at_service": 46500
   }

7. Technician completes work
   PATCH /api/work-orders/{wo-uuid}/
   {
     "status": "COMPLETED",
     "completed_at": "2025-01-18T14:30:00Z",
     "odometer_at_service": 46500,
     "engine_hours_at_service": 2150,
     "labor_hours": 3.5,
     "parts_cost": 285.50,
     "labor_cost": 350.00,
     "notes": "Replaced seals, tested under pressure"
   }

8. System automatically:
   - Updates 2 linked defects: WORK_ORDER_CREATED → RESOLVED
   - Updates vehicle meters:
     * odometer_miles: 45000 → 46500
     * engine_hours: 2100 → 2150
```

**Result:**
- Inspection: COMPLETED (immutable)
- Defects: 2 RESOLVED, 1 OPEN (below severity threshold)
- Work Order: COMPLETED
- Asset: Meters updated automatically

**Timeline:**
- Day 1: Inspection performed and finalized
- Day 1: Work orders generated and approved
- Day 2-3: Work scheduled and performed
- Day 3: Work completed, defects resolved

---

### Workflow 11: Multiple Inspections → Consolidated Work Order

**Scenario:** Customer brings multiple trucks for inspection, several have same issue

**Steps:**

1. **Perform Multiple Inspections**
   - Inspect Truck A → Find hydraulic leak (MAJOR)
   - Inspect Truck B → Find hydraulic leak (MAJOR)
   - Inspect Truck C → No defects

2. **Generate Work Orders Separately**
   ```http
   POST /api/work-orders/generate_from_defects/
   ```
   - Truck A → Work Order WO-001 (Repair Hydraulic Leak)
   - Truck B → Work Order WO-002 (Repair Hydraulic Leak)

3. **Batch Approval**
   ```http
   POST /api/work-orders/{wo-001-uuid}/approve/
   POST /api/work-orders/{wo-002-uuid}/approve/
   ```

4. **Assign to Same Technician**
   ```http
   PATCH /api/work-orders/{wo-001-uuid}/
   PATCH /api/work-orders/{wo-002-uuid}/
   ```
   - Same technician can work on both
   - Schedule back-to-back

**Business Rules:**
- Work orders are asset-specific (cannot merge across assets)
- Can batch approve for efficiency
- Filter by customer + defect type to find similar issues

---

## Common Patterns

### Pattern 1: Filter and Search

**Find Critical Defects Awaiting Work Orders:**
```http
GET /api/defects/?severity=CRITICAL&status=OPEN
```

**Find Overdue Work Orders:**
```http
GET /api/work-orders/?status=PENDING&due_date__lt=2025-01-15
```

**Find All Work for Specific Asset:**
```http
GET /api/work-orders/?asset_id={uuid}
GET /api/inspections/?asset_id={uuid}
```

---

### Pattern 2: Audit Trail

**View Complete History for Asset:**

1. Get all inspections:
   ```http
   GET /api/inspections/?asset_id={uuid}&ordering=-finalized_at
   ```

2. Get all defects from inspections:
   ```http
   GET /api/defects/?inspection_run={inspection-uuid}
   ```

3. Get all work orders:
   ```http
   GET /api/work-orders/?asset_id={uuid}&ordering=-created_at
   ```

**Business Rules:**
- Inspections are immutable once finalized (audit compliance)
- All status changes tracked via updated_at timestamps
- Work orders linked to source defects (traceability)

---

### Pattern 3: Dashboard Metrics

**Shop Dashboard Queries:**

```http
# Open critical defects
GET /api/defects/?status=OPEN&severity=CRITICAL

# Work orders pending approval
GET /api/work-orders/?approval_status=PENDING_APPROVAL

# Work in progress
GET /api/work-orders/?status=IN_PROGRESS

# Completed this week
GET /api/work-orders/?status=COMPLETED&completed_at__gte=2025-01-08

# Inspections today
GET /api/inspections/?finalized_at__gte=2025-01-15&finalized_at__lt=2025-01-16
```

---

### Pattern 4: Error Handling

**Common Validation Errors:**

1. **Immutable Inspection Modification:**
   ```
   Error: Cannot modify step_data after inspection is finalized
   Solution: Inspections locked after finalized_at is set
   ```

2. **Duplicate Defect Identity:**
   ```
   Error: Defect with this identity already exists
   Solution: System prevents duplicates via unique SHA256 hash
   ```

3. **Invalid Status Progression:**
   ```
   Error: Cannot change status from IN_PROGRESS to DRAFT
   Solution: Status only moves forward: DRAFT → IN_PROGRESS → COMPLETED
   ```

4. **Meter Rollback Attempt:**
   ```
   Warning: New odometer reading (45000) is less than current (46500), not updating
   Solution: System prevents meter rollback, silently skips update
   ```

---

### Pattern 5: Idempotency

**Safe Re-submission:**

- **Rule Evaluation:** Can evaluate rules multiple times, system updates existing defects rather than creating duplicates
- **Work Order Generation:** defect_identity prevents duplicate work orders for same defect
- **Meter Updates:** System only increases meters, repeated saves don't cause issues
- **Defect Status Sync:** Bidirectional updates are idempotent via signals

---

## Best Practices

### For Inspectors

1. Save progress frequently during inspection (system allows incremental saves)
2. Finalize only when inspection is complete and reviewed
3. Add detailed notes and photos to defects
4. Use inspector signature for formal inspections

### For Service Advisors

1. Review all defects before generating work orders
2. Use min_severity to control which defects create work orders
3. Enable group_by_location to consolidate related work
4. Add approval notes for audit trail
5. Communicate with customers before approving high-priority work

### For Shop Managers

1. Monitor PENDING_APPROVAL work orders daily
2. Assign work orders to appropriate departments
3. Set realistic due_dates based on parts availability and schedule
4. Review CRITICAL defects immediately
5. Track work order completion rates

### For Technicians

1. Update status to IN_PROGRESS when starting work
2. Record accurate meter readings (odometer, engine hours)
3. Document work performed in notes
4. Include parts used and labor hours for accurate costing
5. Add photos of completed repairs

---

**Version:** 2.0 (Phase 5 Complete)
**Last Updated:** 2026-03-12
**See Also:**
- [API Reference](API_REFERENCE.md)
- [Admin Interface Guide](ADMIN_GUIDE.md)
- [Performance Optimization](PERFORMANCE_OPTIMIZATION.md)
