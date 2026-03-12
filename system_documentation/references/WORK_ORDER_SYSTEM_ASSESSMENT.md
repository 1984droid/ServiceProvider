# Work Order System - Comprehensive State Assessment

**Date:** 2026-02-08
**Version:** v2.2 (v2.3 vocabulary imported)
**Status:** Core Implementation Complete, Missing Financial/Cost Layer

---

## Executive Summary

### Current State: **70% Complete**

**✅ What's Excellent:**
- Structured vocabulary (682 nouns, 89 verbs, 69 locations) - NO FREE TEXT CHAOS
- Inspection→Work Order integration with proposal workflow
- Asset linkage and tenant isolation
- Smart suggestion system (nouns suggest verbs/locations)

**❌ Critical Gaps:**
- **NO COST/PRICING MODEL** - Can't track labor costs, parts costs, billing
- **NO MAINTENANCE PROGRAM LINKAGE** - Work orders don't tie to scheduled maintenance
- **NO PARTS INVENTORY INTEGRATION** - Can't link parts to nouns for cost tracking
- **NO INTERNAL VS CUSTOMER COSTING** - Can't separate shop cost from customer billing

**Recommendation:** Before implementing leasing system, add financial layer to work orders. Leasing companies need cost visibility and compliance tracking.

---

## Architecture Assessment

### Data Model State

#### ✅ **Excellent: Core Structure**

```
WorkOrder (TenantOwnedModel)
  ├── asset (FK → Asset)                     ✅ Solid asset linkage
  ├── status (OPEN/IN_PROGRESS/COMPLETE)     ✅ Basic workflow
  ├── summary, description                   ✅ Text fields
  └── items (reverse FK)
      └── WorkOrderItem
            ├── verb (FK)                    ✅ Structured action
            ├── noun_item (FK)               ✅ Structured noun (682 options)
            ├── service_location (FK)        ✅ Structured location (69 options)
            ├── quantity                     ✅ Decimal quantity
            ├── notes                        ✅ Free text
            └── related_defect (FK)          ✅ Inspection integration
```

**Strengths:**
- **Structured vocabulary** prevents free-text chaos
- **Tenant isolation** via TenantOwnedModel
- **Asset-centric** model (work orders belong to assets)
- **Inspection integration** (defects → proposals → work orders)

#### ❌ **Critical Missing: Financial Layer**

**What's Missing:**
```
WorkOrderItem should have:
  ├── unit_cost (labor rate or part cost)
  ├── total_cost (quantity * unit_cost)
  ├── customer_price (billable amount)
  ├── cost_type (INTERNAL_SHOP_COST vs CUSTOMER_BILLABLE)
  └── margin (customer_price - total_cost)

WorkOrder should have:
  ├── estimated_total_cost
  ├── actual_total_cost (sum of items)
  ├── customer_total_price (sum of billable items)
  ├── internal_cost (sum of internal items)
  └── labor_hours_estimated / labor_hours_actual
```

**Impact:**
- ❌ Can't track shop labor costs vs customer billing
- ❌ Can't analyze profitability by asset
- ❌ Can't track warranty work (internal cost, no customer charge)
- ❌ Can't generate customer invoices
- ❌ **Leasing companies can't see maintenance costs** (critical for residual value)

#### ⚠️ **Missing: Maintenance Program Integration**

**What's Missing:**
```
WorkOrder should optionally link to:
  ├── maintenance_program (FK → MaintenanceProgram)
  ├── scheduled_date (when maintenance was scheduled)
  ├── is_preventive_maintenance (bool)
  └── meter_reading_at_service (odometer/engine hours)

This would enable:
  - "Was maintenance done on time?" (compliance tracking)
  - "Which work orders are PM vs reactive?" (analytics)
  - "Track cost per PM program" (e.g., cost of all 15k PM services)
```

**Impact:**
- ❌ Can't track scheduled maintenance compliance
- ❌ Can't analyze PM vs reactive repair costs
- ❌ **Leasing companies can't verify PM compliance** (critical for lease terms)

#### ⚠️ **Missing: Parts Inventory Integration**

**What's Missing:**
```
Part model (new):
  ├── noun_item (FK)  # Link to work order vocabulary
  ├── part_number
  ├── description
  ├── unit_cost (what shop pays)
  ├── unit_price (what customer pays)
  ├── quantity_on_hand
  ├── vendor
  └── is_serialized (track individual units)

WorkOrderItem should have:
  ├── part (FK → Part)  # If noun_item is a PART type
  └── serial_number (if part is serialized)
```

**Impact:**
- ❌ Can't auto-populate costs from parts inventory
- ❌ Can't track inventory usage
- ❌ Can't generate parts purchase orders
- ❌ Manual entry of every cost (error-prone)

---

## Integration Assessment

### 1. ✅ Assets Integration (EXCELLENT)

**Current State:**
```python
# apps/work_orders/models.py:155-159
asset = models.ForeignKey(
    'assets.Asset',
    on_delete=models.CASCADE,
    related_name='work_orders'
)
```

**What Works:**
- ✅ Every work order belongs to an asset
- ✅ Cascade delete (if asset deleted, work orders deleted)
- ✅ Can query `asset.work_orders.all()` for history
- ✅ Permissions enforced via `asset__owned_by_organization`

**What's Missing:**
- ⚠️ No linkage to asset capabilities (e.g., "insulated aerial device" should suggest specific nouns)
- ⚠️ No asset subtype filtering (e.g., "aerial device work orders" only show relevant nouns)

**Recommendation:** LOW PRIORITY - Current linkage is sufficient for MVP.

---

### 2. ✅ Inspections Integration (EXCELLENT)

**Current State:**
```python
# apps/work_orders/models.py:229-236
related_defect = models.ForeignKey(
    'inspections.InspectionDefect',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='work_order_items',
    help_text="Defect that prompted this work item"
)
```

**What Works:**
- ✅ WorkOrderItem can link to InspectionDefect
- ✅ WorkOrderLineProposal auto-generated from defects via `DefectWorkOrderService`
- ✅ Proposal workflow: `pending → approved → promoted` to WorkOrderItem
- ✅ Defect severity maps to proposal priority
- ✅ 46 seed mappings for ANSI A92.2-2021 defects

**Data Flow:**
```
InspectionDefect detected
  ↓
DefectWorkOrderService.create_proposals_from_defect()
  ↓
Lookup InspectionDefectWorkOrderMap (defect_id → suggested lines)
  ↓
Create WorkOrderLineProposal (staging)
  ↓
Service Writer reviews at /api/work-order-line-proposals/?status=pending
  ↓
Approve → WorkOrderItem created
  ↓
Technician executes work
```

**What's Missing:**
- ⚠️ No "close the loop" - can't mark defect as RESOLVED when work order completed
- ⚠️ No "defect re-check" workflow after repair

**Recommendation:** MEDIUM PRIORITY - Add defect resolution tracking.

---

### 3. ❌ Maintenance Programs Integration (MISSING)

**Current State:** **NO INTEGRATION**

**What Exists:**
- ✅ MaintenanceProgram model with time/meter-based intervals (apps/assets/models.py:852)
- ✅ MaintenanceTask catalog (13 tasks)
- ✅ 7 maintenance programs imported (tractor 15k PM, forklift 250hr PM, etc.)

**What's Missing:**
```python
# Should add to WorkOrder model:
maintenance_program = models.ForeignKey(
    'assets.MaintenanceProgram',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='work_orders',
    help_text="Scheduled maintenance program this work order fulfills"
)
is_preventive_maintenance = models.BooleanField(default=False)
scheduled_date = models.DateField(null=True, blank=True)
meter_reading_at_service = models.IntegerField(
    null=True,
    blank=True,
    help_text="Odometer/engine hours at time of service"
)
```

**Use Cases Blocked:**
- ❌ Can't track "Was 15k PM done on time?"
- ❌ Can't calculate "Days overdue for scheduled maintenance"
- ❌ Can't analyze "PM cost vs reactive repair cost"
- ❌ **Leasing companies can't verify maintenance compliance** (CRITICAL)

**Recommendation:** **HIGH PRIORITY** - Essential for leasing compliance monitoring.

**Implementation Complexity:** LOW (2-3 days)
- Add 3 fields to WorkOrder model
- Add API endpoints to filter by maintenance_program
- Update UI to show "scheduled maintenance" work orders

---

### 4. ❌ Cost/Financial Integration (MISSING)

**Current State:** **NO COST TRACKING**

**What's Missing:**

#### A) Labor Costing
```python
# Should add to WorkOrderItem or WorkOrder:
labor_hours = models.DecimalField(max_digits=5, decimal_places=2)
labor_rate = models.DecimalField(max_digits=8, decimal_places=2)
labor_cost = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    help_text="labor_hours * labor_rate"
)
```

#### B) Parts Costing
```python
# WorkOrderItem currently has no cost fields!
# Should add:
unit_cost = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    null=True,
    blank=True,
    help_text="Cost per unit (from Part inventory or manual entry)"
)
total_cost = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    help_text="quantity * unit_cost"
)
```

#### C) Customer Billing
```python
# Should add to WorkOrderItem:
unit_price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    null=True,
    blank=True,
    help_text="Customer price per unit (markup over cost)"
)
total_price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    help_text="quantity * unit_price (billable to customer)"
)
is_billable = models.BooleanField(
    default=True,
    help_text="False for warranty work, internal shop use, etc."
)
```

#### D) Cost Type Classification
```python
# Should add to WorkOrderItem:
COST_TYPE_CHOICES = [
    ('INTERNAL_SHOP', 'Internal Shop Cost'),
    ('CUSTOMER_BILLABLE', 'Customer Billable'),
    ('WARRANTY', 'Warranty (No Charge)'),
    ('INTERNAL_CAPITAL', 'Internal Capital Expense'),
]
cost_type = models.CharField(
    max_length=30,
    choices=COST_TYPE_CHOICES,
    default='CUSTOMER_BILLABLE'
)
```

**Use Cases Blocked:**
- ❌ Can't generate customer invoices
- ❌ Can't track shop profitability
- ❌ Can't separate warranty work from billable work
- ❌ Can't track internal shop expenses (tools, consumables)
- ❌ Can't analyze cost per asset
- ❌ **Leasing companies can't see maintenance costs** (CRITICAL)

**Recommendation:** **CRITICAL PRIORITY** - Must add before leasing system.

**Implementation Complexity:** MEDIUM (1-2 weeks)
- Design cost model (internal vs customer pricing)
- Add fields to WorkOrderItem
- Create Part model for inventory linkage
- Add cost computation logic
- Update API serializers
- Build costing UI

---

### 5. ⚠️ Workflow State Machine (INCOMPLETE)

**Current State:**
```python
STATUS_CHOICES = [
    ('OPEN', 'Open'),
    ('IN_PROGRESS', 'In Progress'),
    ('COMPLETE', 'Complete'),
    ('VOIDED', 'Voided'),
]
```

**What's Missing:**
- No `assigned_to` (which technician?)
- No `started_at`, `completed_at` timestamps
- No `estimated_completion_date`
- No `priority` (urgent vs routine)
- No `approval_required` flag (customer authorization for expensive repairs)

**Recommendation:** MEDIUM PRIORITY - Add as needed for operations.

---

## Data Vocabulary Assessment

### ✅ Structured Vocabulary (EXCELLENT)

**Imported Data (v2.3):**
- ✅ 21 noun categories (Brakes & Air, Equipment & Hydraulics, etc.)
- ✅ 682 nouns with smart suggestions
- ✅ 89 verbs (inspect, replace, torque, adjust, diagnose, etc.)
- ✅ 9 location categories (Chassis, Power Systems, Aerial Device, etc.)
- ✅ 69 service locations (boom, bucket, LF, RF, cab_interior, etc.)

**Smart Suggestions:**
```python
# NounItem has pipe-delimited suggestion fields:
suggested_verbs_top = "inspect|replace|adjust"
suggested_verbs_more = "clean|lubricate"
suggested_locations = "LF|RF|LR|RR"
```

**Example:**
- Noun: "Brake Pad"
- Suggested verbs: "inspect", "replace"
- Suggested locations: "LF", "RF", "LR", "RR"
- UI can pre-populate dropdowns based on noun selection

**Strengths:**
- ✅ Prevents free-text chaos (no typos, consistent naming)
- ✅ Enables powerful reporting (count by noun, verb, location)
- ✅ Smart UI (suggest verbs/locations based on noun)
- ✅ Multi-tenant (same vocabulary across all tenants)

**What's Missing:**
- ⚠️ No cost data in vocabulary (nouns don't have default costs)
- ⚠️ No asset subtype filtering (show only relevant nouns for this asset type)

**Recommendation:** LOW PRIORITY - Vocabulary is solid foundation.

---

## API Endpoints Assessment

### ✅ Vocabulary Endpoints (READ-ONLY)

```
GET /api/noun-categories/          ✅ List noun categories
GET /api/noun-items/                ✅ List nouns, filter by category/type, search
GET /api/verbs/                     ✅ List verbs, filter by category
GET /api/service-locations/         ✅ List locations, filter by category/quick_pick
GET /api/location-categories/       ✅ List location categories
```

**Status:** Production-ready, performant, well-designed.

### ✅ Work Order Endpoints (CRUD)

```
GET    /api/work-orders/            ✅ List (filtered by tenant + org permissions)
POST   /api/work-orders/            ✅ Create
GET    /api/work-orders/{id}/       ✅ Retrieve
PATCH  /api/work-orders/{id}/       ✅ Update
DELETE /api/work-orders/{id}/       ✅ Delete

GET    /api/work-order-items/       ✅ List
POST   /api/work-order-items/       ✅ Create
GET    /api/work-order-items/{id}/  ✅ Retrieve
PATCH  /api/work-order-items/{id}/  ✅ Update
DELETE /api/work-order-items/{id}/  ✅ Delete
```

**Permissions:**
- ✅ OrganizationPermissionMixin enforces asset ownership
- ✅ Work orders for unowned assets visible to all internal staff
- ✅ Tenant isolation via TenantFilteredModelMixin

**Status:** Production-ready.

### ✅ Proposal Workflow Endpoints (NEW v2.2)

```
GET  /api/work-order-line-proposals/                       ✅ List, filter by status/priority
POST /api/work-order-line-proposals/{id}/approve/          ✅ Approve + promote to WO item
POST /api/work-order-line-proposals/{id}/reject/           ✅ Reject
POST /api/work-order-line-proposals/bulk_approve/          ✅ Bulk approve
POST /api/work-order-line-proposals/bulk_reject/           ✅ Bulk reject
PATCH /api/work-order-line-proposals/{id}/update_proposal/ ✅ Edit before approval
```

**Status:** Production-ready, comprehensive workflow.

### ❌ Missing Endpoints

**Cost/Financial:**
- ❌ `GET /api/work-orders/{id}/cost-summary/` - Total cost breakdown
- ❌ `GET /api/work-orders/by-asset/{asset_id}/cost-history/` - Cost trends
- ❌ `POST /api/work-orders/{id}/generate-invoice/` - Customer invoice

**Maintenance Program:**
- ❌ `GET /api/work-orders/?maintenance_program={key}` - Filter by PM program
- ❌ `GET /api/assets/{id}/maintenance-compliance/` - PM compliance status

**Reporting:**
- ❌ `GET /api/reports/work-orders/cost-by-noun/` - Cost analysis by part
- ❌ `GET /api/reports/work-orders/pm-vs-reactive/` - PM vs reactive cost split

---

## Permissions & Multi-Tenancy Assessment

### ✅ Tenant Isolation (EXCELLENT)

**WorkOrder:**
```python
class WorkOrder(TenantOwnedModel):
    # Inherits tenant_root from TenantOwnedModel
    # All queries auto-filtered by request.tenant
```

**WorkOrderItem:**
```python
class WorkOrderItem(TenantOwnedModel):
    # Auto-sets tenant_root from work_order on save
    # Validates tenant_root matches work_order tenant
```

**Status:** Solid multi-tenant design, no cross-tenant leaks possible.

### ✅ Organization Permissions (GOOD)

**WorkOrder:**
```python
class WorkOrderViewSet(OrganizationPermissionMixin, ...):
    permission_entity = 'work_orders'
    organization_field = 'asset__owned_by_organization'
    allow_null_org = True  # Unowned assets visible to all internal staff
```

**Behavior:**
- ✅ Users only see work orders for assets their org owns
- ✅ Internal staff see all work orders (including unowned assets)
- ✅ Proper permission checks via membership.has_permission('work_orders:read')

**What's Missing:**
- ⚠️ No `serviced_by` filtering - can't query "work orders we performed for other orgs"
- ⚠️ No cross-tenant sharing (e.g., repair shop seeing customer's work orders)

**Recommendation:** CRITICAL for leasing - Add SharingContract support.

---

## Performance & Scalability Assessment

### Database Indexes

**WorkOrder:**
```python
indexes = [
    models.Index(fields=['tenant_root', 'status']),
    models.Index(fields=['asset', '-created_at']),
]
```
✅ Good coverage for common queries.

**WorkOrderItem:**
```python
indexes = [
    models.Index(fields=['work_order']),
    models.Index(fields=['tenant_root', 'verb']),
    models.Index(fields=['related_defect']),
]
```
✅ Good coverage.

**Missing Indexes:**
- ⚠️ No index on `WorkOrder.created_by` (for "my work orders" queries)
- ⚠️ No index on `WorkOrderLineProposal.status` (for pending proposals)

**Recommendation:** Add as queries slow down.

### Query Optimization

**Current:**
```python
# apps/work_orders/api_views.py:34
queryset = WorkOrder.objects.select_related('asset', 'asset__owned_by_organization').all()
```
✅ Proper select_related to avoid N+1 queries.

**Potential Issues at Scale:**
- ⚠️ WorkOrderItem list endpoint doesn't prefetch noun/verb/location
- ⚠️ No pagination defaults (could return thousands of records)

**Recommendation:** Add prefetch_related and pagination.

---

## Testing Status

### Unit Tests: ⚠️ PARTIAL

**What Exists:**
- ✅ 32 vocabulary model tests (apps/work_orders/tests/test_vocabulary_models.py)
- ⚠️ Old test files exist but may be outdated:
  - `test_v2_2_models.py` (22KB)
  - `test_v2_2_api.py` (25KB)
  - `test_v2_2_services.py` (22KB)

**What's Missing:**
- ❌ No tests for WorkOrderLineProposal workflow
- ❌ No tests for DefectWorkOrderService
- ❌ No tests for proposal approve/reject
- ❌ No tests for permissions enforcement

**Recommendation:** HIGH PRIORITY - Add comprehensive test suite.

### Integration Tests: ❌ MISSING

**Critical Flows to Test:**
- ❌ End-to-end: Inspection defect → proposal → work order item
- ❌ Proposal approval/rejection workflow
- ❌ Bulk proposal generation
- ❌ Permission enforcement (org boundaries, tenant isolation)

**Recommendation:** CRITICAL - Add before production.

---

## Critical Gaps Summary

### 1. ❌ NO COST/FINANCIAL LAYER (CRITICAL)

**Impact:** Can't track costs, can't bill customers, can't analyze profitability.

**What's Needed:**
```python
# WorkOrderItem additions:
unit_cost           # Cost per unit (from Part or manual entry)
total_cost          # quantity * unit_cost
unit_price          # Customer price per unit
total_price         # quantity * unit_price
is_billable         # False for warranty/internal work
cost_type           # INTERNAL_SHOP vs CUSTOMER_BILLABLE vs WARRANTY

# WorkOrder additions:
labor_hours_estimated
labor_hours_actual
labor_rate
total_labor_cost
total_parts_cost
total_cost          # labor + parts
total_customer_price
margin              # price - cost
```

**Effort:** 1-2 weeks (model changes + API + UI)

**Priority:** **CRITICAL** - Required for leasing system.

---

### 2. ❌ NO MAINTENANCE PROGRAM INTEGRATION (HIGH PRIORITY)

**Impact:** Can't track scheduled maintenance compliance, can't prove PM was done on time.

**What's Needed:**
```python
# WorkOrder additions:
maintenance_program (FK → MaintenanceProgram)
is_preventive_maintenance (bool)
scheduled_date (DateField)
meter_reading_at_service (IntegerField)
```

**Effort:** 2-3 days (model changes + API)

**Priority:** **HIGH** - Essential for leasing compliance monitoring.

---

### 3. ❌ NO PARTS INVENTORY INTEGRATION (MEDIUM PRIORITY)

**Impact:** Can't auto-populate costs, can't track inventory, manual entry error-prone.

**What's Needed:**
```python
# New model:
class Part(models.Model):
    noun_item (FK → NounItem)    # Link to work order vocabulary
    part_number
    description
    unit_cost                    # What shop pays
    unit_price                   # What customer pays
    quantity_on_hand
    vendor
    is_serialized

# WorkOrderItem addition:
part (FK → Part)
serial_number (if serialized)
```

**Effort:** 1 week (new model + inventory management)

**Priority:** **MEDIUM** - Can defer for MVP, but critical for scale.

---

### 4. ⚠️ NO CROSS-TENANT SHARING (LEASING BLOCKER)

**Impact:** Leasing companies can't see customer work orders, repair shops can't share data.

**What's Needed:**
- SharingContract model (from leasing assessment)
- Permission checks for cross-tenant reads
- API filtering by sharing contracts

**Effort:** 2-3 weeks (part of leasing Phase 0)

**Priority:** **CRITICAL** - Required for leasing system.

---

## Recommendations for Leasing System

### Before Implementing Leasing:

#### 1. **Add Financial Layer** (1-2 weeks) - CRITICAL
Without costs, leasing companies can't assess maintenance expenses.

**Minimum Viable Fields:**
```python
WorkOrderItem:
  - total_cost (what work actually cost)
  - is_billable (separate internal vs customer costs)
  - cost_type (INTERNAL_SHOP vs CUSTOMER_BILLABLE)
```

**Why:** Leasing companies need to see "How much was spent on maintenance?"

#### 2. **Add Maintenance Program Link** (2-3 days) - CRITICAL
Without PM tracking, leasing companies can't verify compliance.

**Minimum Viable Fields:**
```python
WorkOrder:
  - maintenance_program (FK)
  - scheduled_date
  - meter_reading_at_service
```

**Why:** Leasing compliance requires "Was 15k PM done on time?"

#### 3. **Add Work Order Completion Timestamps** (1 day) - HIGH
Leasing companies need to know WHEN work was done.

**Minimum Viable Fields:**
```python
WorkOrder:
  - started_at
  - completed_at
```

**Why:** "Asset was out of service for X days" is important for leasing.

---

### Leasing System Dependencies:

**Work Order Data Needed by Leasing:**
- ✅ Asset linkage (have)
- ✅ Structured vocabulary (have)
- ✅ Inspection defect linkage (have)
- ❌ **Cost data** (MISSING - CRITICAL)
- ❌ **Maintenance program linkage** (MISSING - CRITICAL)
- ❌ **Service provider identity** (have via serviced_by_tenant, but no verification)
- ⚠️ **Completion timestamps** (MISSING - HIGH)

**Leasing Compliance Queries:**
```sql
-- Can we answer these questions? NO!

-- 1. "Total maintenance cost for this asset in past 12 months?"
-- ❌ NO - No cost fields on WorkOrderItem

-- 2. "Was scheduled 15k PM done on time?"
-- ❌ NO - No maintenance_program FK on WorkOrder

-- 3. "Who performed the work?"
-- ✅ YES - serviced_by_tenant field exists (but not exposed in API)

-- 4. "When was work completed?"
-- ⚠️ PARTIAL - Have created_at, but no completed_at timestamp

-- 5. "Was work done by verified provider?"
-- ⚠️ PARTIAL - Have serviced_by_tenant, but no verification flag
```

---

## Suggested Implementation Roadmap

### Phase 1: Financial Layer (1-2 weeks) - CRITICAL
**Goal:** Track costs for leasing visibility

**Tasks:**
1. Add cost fields to WorkOrderItem:
   - `unit_cost`, `total_cost`, `unit_price`, `total_price`
   - `is_billable`, `cost_type`
2. Add labor cost fields to WorkOrder:
   - `labor_hours_estimated`, `labor_hours_actual`, `labor_rate`
3. Add cost computation logic (calculate totals)
4. Update API serializers to include cost fields
5. Add permission checks (only show costs to authorized users)
6. Write tests (cost calculation, permission enforcement)

**Deliverable:** Work orders track costs, leasing companies can query expenses.

---

### Phase 2: Maintenance Program Integration (2-3 days) - CRITICAL
**Goal:** Link work orders to scheduled maintenance

**Tasks:**
1. Add fields to WorkOrder:
   - `maintenance_program` (FK)
   - `is_preventive_maintenance` (bool)
   - `scheduled_date`, `meter_reading_at_service`
2. Update API to filter by maintenance_program
3. Add "scheduled maintenance" indicator in UI
4. Write tests (PM work orders, compliance queries)

**Deliverable:** Can track "Was PM done on time?" for leasing compliance.

---

### Phase 3: Workflow Timestamps (1 day) - HIGH
**Goal:** Track when work started/completed

**Tasks:**
1. Add fields to WorkOrder:
   - `started_at`, `completed_at`
2. Auto-set timestamps on status changes
3. Update API serializers
4. Write tests

**Deliverable:** Leasing can see "Asset was out of service for X days."

---

### Phase 4: Provider Verification (3 days) - MEDIUM
**Goal:** Track which repair shops are "verified"

**Tasks:**
1. Add to Tenant model:
   - `is_verified_provider` (bool)
   - `verified_at`, `certifications` (JSONField)
2. Expose `serviced_by_tenant` in WorkOrder API
3. Add verified badge in UI

**Deliverable:** Leasing can filter "work by verified providers only."

---

### Phase 5: Parts Inventory (1 week) - DEFER
**Goal:** Link parts to nouns for auto-cost population

**Tasks:**
1. Create Part model
2. Link Part.noun_item to NounItem
3. Add Part.unit_cost, Part.unit_price
4. Auto-populate WorkOrderItem costs from Part
5. Build parts inventory management UI

**Deliverable:** Cost entry is automatic, not manual.

---

### Phase 6: Cross-Tenant Sharing (Leasing Phase 0)
**Goal:** Enable leasing companies to see customer work orders

**Tasks:**
- Implement SharingContract model
- Add permission checks for cross-tenant reads
- Build leasing dashboard

**Deliverable:** Leasing companies have read-only visibility.

---

## Difficulty Assessment: Changing Existing Structure

### ✅ Easy Changes (1-3 days each):
- Add fields to existing models (WorkOrder, WorkOrderItem)
- Add timestamps (started_at, completed_at)
- Add maintenance_program FK
- Add provider verification flag to Tenant
- Expose serviced_by_tenant in API

**Why Easy:** Additive changes, no breaking changes, no data migration complexity.

---

### ⚠️ Medium Difficulty (1 week each):
- Add cost/pricing fields (need design decision on internal vs customer pricing)
- Create Part model + inventory management
- Add cost computation logic (handle edge cases like warranty work)
- Permission system for cost visibility (who can see costs?)

**Why Medium:** Design decisions needed, some business logic complexity.

---

### ❌ Hard Changes (2-3 weeks each):
- Refactor WorkOrderItem to support both labor + parts (currently mixed)
- Add accounting system integration (QuickBooks, Xero, etc.)
- Build customer invoicing system
- Add work order templates for common jobs
- Predictive maintenance based on historical work orders

**Why Hard:** Major architectural changes, external integrations, complex business logic.

---

## Breaking Changes Risk Assessment

### ✅ LOW RISK: Adding fields to existing models
**Examples:**
- Add `unit_cost` to WorkOrderItem
- Add `maintenance_program` FK to WorkOrder
- Add `started_at`, `completed_at` timestamps

**Risk:** None - nullable fields, backward compatible, no data migration needed.

---

### ⚠️ MEDIUM RISK: Changing model relationships
**Examples:**
- Change NounItem.category from CharField → FK (already done in v2.2!)
- Add Part model and link to WorkOrderItem

**Risk:** Requires data migration, but existing data can coexist.

**Mitigation:** Make new fields nullable, gradual migration.

---

### ❌ HIGH RISK: Changing core data structures
**Examples:**
- Split WorkOrderItem into WorkOrderLabor + WorkOrderPart (separate tables)
- Change WorkOrder status workflow (add new required statuses)
- Remove or rename existing fields

**Risk:** Breaking changes, requires full data migration, API changes, UI changes.

**Mitigation:** Don't do this! Extend, don't replace.

---

## Conclusion

### Current State: **70% Complete**

**Excellent Foundation:**
- ✅ Structured vocabulary (no free-text chaos)
- ✅ Inspection integration (defects → work orders)
- ✅ Tenant isolation (multi-tenant safe)
- ✅ Asset linkage (work orders belong to assets)
- ✅ Permissions (org-based access control)

**Critical Gaps:**
- ❌ **NO COST TRACKING** (can't track expenses, can't bill customers)
- ❌ **NO MAINTENANCE PROGRAM LINK** (can't track PM compliance)
- ❌ **NO PARTS INVENTORY** (can't auto-populate costs)
- ❌ **NO CROSS-TENANT SHARING** (leasing blocker)

### Recommendation for Leasing System:

**Before implementing leasing, complete:**
1. **Financial Layer** (1-2 weeks) - Add cost fields to WorkOrderItem
2. **Maintenance Program Integration** (2-3 days) - Link work orders to PM schedules
3. **Workflow Timestamps** (1 day) - Track started_at, completed_at

**Total Time:** 2-2.5 weeks

**Why:** Leasing companies need to see:
- "How much was spent on maintenance?" (requires costs)
- "Was scheduled PM done on time?" (requires PM linkage)
- "When was work completed?" (requires timestamps)

Without these, leasing compliance monitoring is not viable.

---

**Prepared by:** Claude (Architecture Assessment Agent)
**Next Step:** Product decision - prioritize financial layer before leasing, or build leasing with limited cost visibility?
