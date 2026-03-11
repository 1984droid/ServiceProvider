# Service Provider Application - Data Contract

**Version:** 1.0
**Date:** 2025-01-XX
**Purpose:** Define the core data model, relationships, constraints, and business rules for single-tenant service provider application.

---

## Core Principles

1. **Single-tenant** - No tenant isolation, all data belongs to the service provider
2. **Customer-centric** - Customer → Assets → Services flow
3. **Contact-based communication** - NO contact info on Customer, use Contact model
4. **Dual asset types** - Vehicle (VIN) and Equipment (Serial Number) as separate models
5. **Inspection-driven work** - Inspections generate work orders via defects
6. **Immutable audit trail** - Finalized inspections cannot be edited

---

## Entity Relationship Overview

```
Customer (1) ──────┬────── (N) Contact
                   │
                   ├────── (N) Vehicle
                   │          └── (N) Equipment (mounted_on)
                   │
                   └────── (N) Equipment (standalone)

Vehicle/Equipment ─── (N) InspectionRun
                         └── (N) InspectionDefect
                                └── (1) WorkOrder

Customer ──────────────── (N) WorkOrder
Vehicle/Equipment ──────── (N) WorkOrder
```

---

## Entity Specifications

### 1. Customer

**Purpose:** Business entity that owns assets and receives services.

**Key Fields:**
- `id` (UUID, PK)
- `name` (string, required, indexed) - DBA name
- `legal_name` (string, optional)
- `is_active` (boolean, default=True, indexed)
- `address_*` (physical location fields)
- `usdot_number` (string, optional, indexed, unique if provided)
- `mc_number` (string, optional, indexed, unique if provided)
- `notes` (text)
- `created_at`, `updated_at` (timestamps)

**Constraints:**
- Name required and non-empty
- USDOT/MC numbers must be unique across customers if provided
- Cannot delete customer with active assets

**Business Rules:**
- Customer can be deactivated but NOT deleted if they have assets or work orders
- NO contact information on Customer model (use Contact)
- Address is physical location, NOT mailing address (use Contact for correspondence)

---

### 2. Contact

**Purpose:** Person at customer organization with communication preferences.

**Key Fields:**
- `id` (UUID, PK)
- `customer_id` (UUID, FK → Customer, required, indexed)
- `first_name`, `last_name` (string, required)
- `title` (string, optional)
- `email` (email, optional, indexed)
- `phone`, `phone_extension`, `mobile` (string, optional)
- `is_active` (boolean, default=True, indexed)
- `is_primary` (boolean, default=False, indexed)
- `receive_invoices` (boolean, default=False)
- `receive_estimates` (boolean, default=False)
- `receive_service_updates` (boolean, default=False)
- `receive_inspection_reports` (boolean, default=False)
- `notes` (text)
- `created_at`, `updated_at` (timestamps)

**Constraints:**
- Customer FK required (cascade delete)
- At least one of email/phone/mobile should be provided (soft constraint)
- Only ONE primary contact per customer (enforced on save)

**Business Rules:**
- Setting `is_primary=True` automatically unsets other primary contacts for that customer
- Deactivating a contact does NOT deactivate the customer
- Contact can be deleted if not linked to any correspondence records
- Correspondence routing based on `receive_*` flags

**Correspondence Routing:**
```
Invoices          → receive_invoices=True
Estimates/Quotes  → receive_estimates=True
Service Updates   → receive_service_updates=True
Inspection Reports→ receive_inspection_reports=True
```

---

### 3. Vehicle

**Purpose:** VIN-based asset (trucks, tractors, trailers, vans).

**Key Fields:**
- `id` (UUID, PK)
- `customer_id` (UUID, FK → Customer, required, indexed)
- `vin` (string(17), required, unique, indexed)
- `unit_number` (string, optional, indexed)
- `year`, `make`, `model`, `vehicle_type` (strings, optional)
- `is_active` (boolean, default=True, indexed)
- `odometer_miles` (integer, nullable)
- `engine_hours` (integer, nullable)
- `vin_decode_data` (JSON, nullable) - NHTSA vPIC raw response
- `vin_decode_date` (datetime, nullable)
- `notes` (text)
- `created_at`, `updated_at` (timestamps)

**Constraints:**
- VIN must be exactly 17 characters (validated)
- VIN must be unique across all vehicles
- Customer FK required (protect on delete - cannot delete customer with vehicles)
- Odometer/engine hours cannot be negative

**Business Rules:**
- VIN is primary identifier (cannot be changed after creation)
- Unit number is customer-assigned, can be changed
- Meters (odometer/engine_hours) can only increase (validate on update)
- Deactivating vehicle does NOT delete inspection/work order history
- Cannot delete vehicle with associated inspections or work orders

**VIN Decode Integration:**
- `vin_decode_data` stores complete NHTSA response as JSON
- `year`, `make`, `model` can be populated from decode or manual entry
- Decode can be re-run to refresh data

---

### 4. Equipment

**Purpose:** Serial number-based asset (aerial devices, cranes, generators, test equipment).

**Key Fields:**
- `id` (UUID, PK)
- `customer_id` (UUID, FK → Customer, required, indexed)
- `serial_number` (string, required, unique, indexed)
- `asset_number` (string, optional, indexed)
- `equipment_type` (string, optional, indexed)
- `manufacturer`, `model` (string, optional)
- `year` (integer, nullable)
- `is_active` (boolean, default=True, indexed)
- `engine_hours` (integer, nullable)
- `cycles` (integer, nullable)
- `mounted_on_vehicle_id` (UUID, FK → Vehicle, nullable, indexed)
- `mount_date` (date, nullable)
- `notes` (text)
- `created_at`, `updated_at` (timestamps)

**Constraints:**
- Serial number must be unique across all equipment
- Customer FK required (protect on delete)
- If `mounted_on_vehicle_id` set, must reference valid active vehicle
- Meters cannot be negative

**Business Rules:**
- Serial number is primary identifier (cannot be changed)
- Asset number is customer-assigned, can be changed
- Equipment can be mounted on vehicle OR standalone
- Mounting relationship can change over time (equipment moved between vehicles)
- If mounted vehicle is deactivated, equipment mount relationship should be reviewed
- Cannot delete equipment with associated inspections or work orders

**Mounting Relationship:**
```
Equipment.mounted_on_vehicle_id → Vehicle.id (nullable)
Equipment.mount_date → Date when mounted

Examples:
- Aerial device mounted on truck chassis
- Crane mounted on truck
- Generator mounted on trailer
- Test equipment (standalone, no mount)
```

---

### 5. InspectionRun

**Purpose:** Instance of an inspection performed on an asset.

**Key Fields:**
- `id` (UUID, PK)
- `asset_type` (enum: 'VEHICLE' | 'EQUIPMENT', required)
- `asset_id` (UUID, required, indexed) - Polymorphic reference
- `customer_id` (UUID, FK → Customer, required, indexed) - Denormalized for queries
- `template_key` (string, FK → InspectionTemplate, required)
- `program_key` (string, optional) - Which inspection program this fulfills
- `status` (enum: 'DRAFT' | 'IN_PROGRESS' | 'COMPLETED', required, indexed)
- `started_at` (datetime, required)
- `finalized_at` (datetime, nullable, indexed)
- `inspector_name` (string, optional)
- `inspector_signature` (JSON, nullable) - Signature capture data
- `template_snapshot` (JSON, required) - Copy of template at execution time
- `step_data` (JSON, required) - Collected inspection data
- `notes` (text)
- `created_at`, `updated_at` (timestamps)

**Constraints:**
- `asset_type` + `asset_id` must reference valid Vehicle or Equipment
- Template snapshot required (immutability)
- Once `finalized_at` is set, run becomes immutable
- Status must progress: DRAFT → IN_PROGRESS → COMPLETED

**Business Rules:**
- DRAFT: Created, no steps executed
- IN_PROGRESS: At least one step submitted
- COMPLETED: All required steps submitted, inspection finalized
- After finalization (finalized_at set), NO changes allowed to step_data
- Customer is denormalized from asset for fast queries
- Template snapshot preserves exact inspection definition at time of execution

**Immutability Rules:**
```
IF finalized_at IS NOT NULL:
  - step_data CANNOT be modified
  - status CANNOT change
  - template_snapshot CANNOT change
  - Only notes/metadata can be updated
```

---

### 6. InspectionDefect

**Purpose:** Defect/finding identified during inspection.

**Key Fields:**
- `id` (UUID, PK)
- `inspection_run_id` (UUID, FK → InspectionRun, required, indexed)
- `defect_identity` (string, unique, indexed) - SHA256-based stable ID for idempotency
- `module_key` (string, required)
- `step_key` (string, required)
- `rule_id` (string, nullable) - Rule that generated this defect (auto-defects)
- `severity` (enum: 'CRITICAL' | 'MAJOR' | 'MINOR' | 'ADVISORY', required, indexed)
- `title` (string, required)
- `description` (text, required)
- `defect_details` (JSON, nullable) - Structured defect data
- `evaluation_trace` (JSON, nullable) - Audit trail of rule evaluation
- `status` (enum: 'OPEN' | 'WORK_ORDER_CREATED' | 'RESOLVED', default='OPEN', indexed)
- `created_at`, `updated_at` (timestamps)

**Constraints:**
- `defect_identity` must be unique (prevents duplicate defects)
- Inspection run FK required (cascade delete)
- Severity required

**Business Rules:**
- `defect_identity` computed as: `SHA256(run_id + module_key + step_key + rule_id)`
- This ensures idempotent defect generation (re-running rules doesn't duplicate)
- Auto-defects have `rule_id` set, manual defects have it NULL
- Status progression: OPEN → WORK_ORDER_CREATED → RESOLVED
- Defects can generate work orders (1 defect → 1 work order, or N defects → 1 work order)

**Severity Impact:**
```
CRITICAL: Equipment unsafe to operate, immediate action required
MAJOR:    Significant issue, schedule repair soon
MINOR:    Maintenance needed, not urgent
ADVISORY: Recommendation, informational
```

---

### 7. WorkOrder

**Purpose:** Service work to be performed on an asset.

**Key Fields:**
- `id` (UUID, PK)
- `work_order_number` (string, unique, indexed) - Human-readable ID
- `customer_id` (UUID, FK → Customer, required, indexed)
- `asset_type` (enum: 'VEHICLE' | 'EQUIPMENT', required)
- `asset_id` (UUID, required, indexed) - Polymorphic reference
- `status` (enum: 'DRAFT' | 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED', indexed)
- `priority` (enum: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT', default='MEDIUM')
- `source` (enum: 'INSPECTION' | 'CUSTOMER_REQUEST' | 'PM_SCHEDULE' | 'BREAKDOWN', required)
- `source_inspection_run_id` (UUID, FK → InspectionRun, nullable)
- `description` (text, required)
- `scheduled_date` (date, nullable)
- `started_at` (datetime, nullable)
- `completed_at` (datetime, nullable)
- `assigned_to` (string, nullable) - Technician name or ID
- `odometer_at_service` (integer, nullable)
- `engine_hours_at_service` (integer, nullable)
- `notes` (text)
- `created_at`, `updated_at` (timestamps)

**Constraints:**
- Work order number must be unique
- Customer FK required
- Asset type + asset ID must reference valid asset
- Status transitions must be valid
- If source='INSPECTION', source_inspection_run_id must be set

**Business Rules:**
- Work order number auto-generated (sequential or custom format)
- Status progression: DRAFT → SCHEDULED → IN_PROGRESS → COMPLETED
- Can be CANCELLED from any status
- Priority can be elevated but not lowered once IN_PROGRESS
- Meter readings (odometer/engine_hours) captured at service time
- Completing work order updates asset meters

**Source Types:**
```
INSPECTION:       Created from inspection defect(s)
CUSTOMER_REQUEST: Customer requested repair/service
PM_SCHEDULE:      Scheduled preventive maintenance
BREAKDOWN:        Emergency breakdown repair
```

**Inspection → Work Order Flow:**
```
1. Inspection finalized
2. Defects identified (CRITICAL/MAJOR severity)
3. User creates work order from defects
4. WorkOrder.source = 'INSPECTION'
5. WorkOrder.source_inspection_run_id = inspection.id
6. Link defects to work order (separate junction table or defect field)
7. Defect status → 'WORK_ORDER_CREATED'
```

---

## Relationship Rules

### Customer Relationships

**Customer can be deleted IF:**
- No active vehicles
- No active equipment
- No open work orders
- No unpaid invoices (future)

**Customer can be deactivated (soft delete) IF:**
- Has historical data (inspections, work orders)
- Has inactive assets

### Asset Relationships

**Vehicle/Equipment can be deleted IF:**
- No inspection runs
- No work orders
- No mounting relationships (for equipment)

**Vehicle/Equipment can be deactivated IF:**
- Has historical data
- Customer wants to retire asset but preserve history

### Equipment Mounting Rules

**Equipment can be mounted on Vehicle IF:**
- Equipment.customer_id = Vehicle.customer_id (same customer)
- Vehicle.is_active = True
- Equipment not already mounted elsewhere

**When Vehicle is deactivated:**
- Mounted equipment should remain linked (historical accuracy)
- Warning if equipment still active on inactive vehicle

### Inspection Relationships

**InspectionRun references:**
- Asset (Vehicle OR Equipment) via polymorphic `asset_type` + `asset_id`
- Customer (denormalized for fast queries)
- Template (via key, not FK)

**InspectionDefect references:**
- InspectionRun (required)
- WorkOrder (optional, set when work order created)

### Work Order Relationships

**WorkOrder references:**
- Customer (required)
- Asset (Vehicle OR Equipment) via polymorphic `asset_type` + `asset_id`
- InspectionRun (optional, if source='INSPECTION')

---

## Data Integrity Rules

### 1. Uniqueness Constraints

```
Customer.usdot_number      → Unique if not blank
Customer.mc_number         → Unique if not blank
Vehicle.vin                → Unique (always)
Equipment.serial_number    → Unique (always)
InspectionDefect.defect_identity → Unique (always)
WorkOrder.work_order_number → Unique (always)
```

### 2. Referential Integrity

```
Contact.customer_id        → Customer.id (CASCADE DELETE)
Vehicle.customer_id        → Customer.id (PROTECT)
Equipment.customer_id      → Customer.id (PROTECT)
Equipment.mounted_on_vehicle_id → Vehicle.id (SET NULL)
InspectionRun.asset_id     → Vehicle.id OR Equipment.id (PROTECT)
InspectionDefect.inspection_run_id → InspectionRun.id (CASCADE)
WorkOrder.customer_id      → Customer.id (PROTECT)
WorkOrder.asset_id         → Vehicle.id OR Equipment.id (PROTECT)
WorkOrder.source_inspection_run_id → InspectionRun.id (SET NULL)
```

### 3. Validation Rules

**Customer:**
- Name not empty after trim
- USDOT/MC numbers must be numeric if provided

**Contact:**
- At least one contact method (email OR phone OR mobile)
- Email format valid if provided
- Only one primary contact per customer

**Vehicle:**
- VIN exactly 17 alphanumeric characters
- Year between 1900 and current_year + 1
- Odometer/engine_hours >= 0

**Equipment:**
- Serial number not empty
- Meters >= 0
- If mounted_on_vehicle set, vehicle must be active

**InspectionRun:**
- Cannot modify if finalized_at is set
- Status transitions valid
- Asset must exist and belong to customer

**WorkOrder:**
- Cannot set completed_at without started_at
- Meter readings match asset type (odometer for vehicles, engine_hours for equipment)
- If source='INSPECTION', inspection run must exist

---

## API Expectations

### Customer API

```
POST   /api/customers/              Create customer
GET    /api/customers/              List customers (filter: is_active)
GET    /api/customers/{id}/         Get customer detail
PATCH  /api/customers/{id}/         Update customer
DELETE /api/customers/{id}/         Delete customer (with checks)
GET    /api/customers/{id}/contacts/ List customer contacts
GET    /api/customers/{id}/assets/   List customer assets
```

### Contact API

```
POST   /api/contacts/               Create contact
GET    /api/contacts/               List contacts (filter: customer_id, is_active)
GET    /api/contacts/{id}/          Get contact detail
PATCH  /api/contacts/{id}/          Update contact
DELETE /api/contacts/{id}/          Delete contact
```

### Vehicle API

```
POST   /api/vehicles/               Create vehicle
POST   /api/vehicles/decode-vin/    Decode VIN (utility endpoint)
GET    /api/vehicles/               List vehicles (filter: customer_id, is_active)
GET    /api/vehicles/{id}/          Get vehicle detail
PATCH  /api/vehicles/{id}/          Update vehicle
DELETE /api/vehicles/{id}/          Delete vehicle (with checks)
PATCH  /api/vehicles/{id}/meters/   Update odometer/engine_hours
```

### Equipment API

```
POST   /api/equipment/              Create equipment
GET    /api/equipment/              List equipment (filter: customer_id, is_active, equipment_type)
GET    /api/equipment/{id}/         Get equipment detail
PATCH  /api/equipment/{id}/         Update equipment
DELETE /api/equipment/{id}/         Delete equipment (with checks)
PATCH  /api/equipment/{id}/mount/   Mount on vehicle
PATCH  /api/equipment/{id}/unmount/ Unmount from vehicle
PATCH  /api/equipment/{id}/meters/  Update meters
```

### Inspection API

```
POST   /api/inspections/start/           Start new inspection
GET    /api/inspections/                 List inspections (filter: customer, asset, status)
GET    /api/inspections/{id}/            Get inspection detail
POST   /api/inspections/{id}/submit-step/ Submit inspection step
POST   /api/inspections/{id}/finalize/   Finalize inspection (immutable)
GET    /api/inspections/{id}/defects/    List defects for inspection
```

### Defect API

```
GET    /api/defects/                List defects (filter: severity, status)
GET    /api/defects/{id}/           Get defect detail
PATCH  /api/defects/{id}/status/    Update defect status
```

### Work Order API

```
POST   /api/work-orders/                    Create work order
POST   /api/work-orders/from-inspection/    Create from inspection defects
GET    /api/work-orders/                    List work orders (filter: customer, status, priority)
GET    /api/work-orders/{id}/               Get work order detail
PATCH  /api/work-orders/{id}/               Update work order
PATCH  /api/work-orders/{id}/start/         Start work order
PATCH  /api/work-orders/{id}/complete/      Complete work order
PATCH  /api/work-orders/{id}/cancel/        Cancel work order
```

---

## Polymorphic Asset References

**Problem:** InspectionRun and WorkOrder can link to Vehicle OR Equipment.

**Solution:** Use `asset_type` + `asset_id` pattern.

```python
# InspectionRun / WorkOrder fields:
asset_type = models.CharField(choices=['VEHICLE', 'EQUIPMENT'])
asset_id = models.UUIDField()

# Usage:
if obj.asset_type == 'VEHICLE':
    asset = Vehicle.objects.get(id=obj.asset_id)
elif obj.asset_type == 'EQUIPMENT':
    asset = Equipment.objects.get(id=obj.asset_id)
```

**Why not Django's GenericForeignKey?**
- More explicit and type-safe
- Easier to query and index
- Better for API contract clarity

---

## Inspection Immutability Pattern

**Goal:** Once inspection is finalized, data cannot be changed (audit compliance).

**Implementation:**

```python
class InspectionRun(models.Model):
    finalized_at = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if self.pk:  # Existing record
            old = InspectionRun.objects.get(pk=self.pk)
            if old.finalized_at:
                # Check if critical fields changed
                if (old.step_data != self.step_data or
                    old.template_snapshot != self.template_snapshot):
                    raise ValidationError("Cannot modify finalized inspection")
        super().save(*args, **kwargs)
```

**What CAN be changed after finalization:**
- `notes` (internal notes)
- Defect statuses (as work progresses)

**What CANNOT be changed:**
- `step_data` (inspection results)
- `template_snapshot` (inspection definition)
- `status` (stays COMPLETED)

---

## Idempotent Defect Generation

**Goal:** Re-running inspection rules doesn't create duplicate defects.

**Implementation:**

```python
defect_identity = SHA256(
    inspection_run_id +
    module_key +
    step_key +
    rule_id
)

# On defect creation:
defect, created = InspectionDefect.objects.get_or_create(
    defect_identity=computed_identity,
    defaults={
        'inspection_run_id': run.id,
        'severity': 'CRITICAL',
        ...
    }
)

if not created:
    # Defect already exists, update if needed
    defect.severity = new_severity
    defect.save()
```

**Benefits:**
- Running rules multiple times is safe
- Defects can be updated (severity, description) without duplication
- Audit trail preserved via `evaluation_trace`

---

## Work Order from Inspection Flow

**Scenario:** Inspection finds critical defects, create work order.

**Steps:**

1. **Inspection finalized:**
   ```
   POST /api/inspections/{id}/finalize/
   → InspectionRun.status = 'COMPLETED'
   → InspectionRun.finalized_at = now()
   ```

2. **User reviews defects:**
   ```
   GET /api/inspections/{id}/defects/
   → Returns list of InspectionDefect objects
   → Filter by severity: CRITICAL, MAJOR
   ```

3. **Create work order from defects:**
   ```
   POST /api/work-orders/from-inspection/
   {
     "inspection_run_id": "uuid",
     "defect_ids": ["uuid1", "uuid2"],
     "priority": "HIGH",
     "description": "Repair critical defects found in inspection",
     "scheduled_date": "2025-02-15"
   }

   → Creates WorkOrder
   → Sets WorkOrder.source = 'INSPECTION'
   → Sets WorkOrder.source_inspection_run_id
   → Updates defects: status = 'WORK_ORDER_CREATED'
   → Links defects to work order
   ```

4. **Work order execution:**
   ```
   PATCH /api/work-orders/{id}/start/
   → WorkOrder.status = 'IN_PROGRESS'
   → WorkOrder.started_at = now()

   PATCH /api/work-orders/{id}/complete/
   {
     "odometer_at_service": 125000,
     "notes": "Replaced brake pads"
   }
   → WorkOrder.status = 'COMPLETED'
   → WorkOrder.completed_at = now()
   → Updates asset meters
   → Updates linked defects: status = 'RESOLVED'
   ```

---

## Meter Management

**Goal:** Track asset operational meters (odometer, engine hours) over time.

**Approach:** Store current meter value on asset, capture snapshot on work orders.

### Vehicle Meters:
- `odometer_miles` (primary)
- `engine_hours` (secondary)

### Equipment Meters:
- `engine_hours` (primary)
- `cycles` (secondary)

### Rules:
- Meters can only increase (validate on update)
- Work orders capture meter reading at service time
- Completing work order updates asset's current meter value

```python
# Update vehicle meter
PATCH /api/vehicles/{id}/meters/
{
  "odometer_miles": 125500,
  "engine_hours": 8200
}

# Validation:
if new_value < current_value:
    raise ValidationError("Meter cannot decrease")

# On work order completion:
work_order.odometer_at_service = 125500
work_order.save()

vehicle.odometer_miles = work_order.odometer_at_service
vehicle.save()
```

---

## Future Extensions (Not in MVP)

### Phase 2 Additions:
- **Invoice** model (links to WorkOrder, Customer)
- **Payment** model (tracks customer payments)
- **Part** model (inventory for work orders)
- **Labor** model (time tracking)
- **Document** model (file uploads for inspections/work orders)

### Phase 3 Additions:
- **MaintenanceSchedule** model (PM scheduling)
- **Notification** model (email/SMS alerts)
- **User** model with roles (currently using Django's built-in User)

### Extensibility Pattern:

When adding new models, follow contract:
1. Define clear ownership (which entity owns this?)
2. Specify deletion behavior (CASCADE, PROTECT, SET_NULL)
3. Add indexes for foreign keys and filter fields
4. Document constraints and business rules
5. Update this contract document

---

## Testing Requirements

### Unit Tests Must Cover:

**Customer:**
- USDOT/MC uniqueness
- Cannot delete with active assets
- Address formatting

**Contact:**
- Only one primary per customer
- Email validation
- Correspondence routing

**Vehicle:**
- VIN uniqueness and format
- Meter increase validation
- VIN decode integration

**Equipment:**
- Serial number uniqueness
- Mounting relationship (same customer)
- Cannot mount on inactive vehicle

**InspectionRun:**
- Immutability after finalization
- Status transitions
- Asset polymorphic reference

**InspectionDefect:**
- Idempotent creation (defect_identity)
- Status progression
- Severity handling

**WorkOrder:**
- Creation from inspection
- Status progression
- Meter capture at service

### Integration Tests Must Cover:

- Complete inspection → defect → work order flow
- Equipment mounting/unmounting
- Customer deactivation with data preservation
- Work order completion updates asset meters

---

## Schema Migrations Strategy

**Principle:** Never break existing data or APIs.

### Adding Fields:
```python
# Good: Nullable or with default
new_field = models.CharField(max_length=100, blank=True, default='')

# Bad: Required field with no default
new_field = models.CharField(max_length=100)  # Breaks existing rows!
```

### Renaming Fields:
1. Add new field
2. Migrate data
3. Deprecate old field
4. Remove old field (next major version)

### Changing Constraints:
- Loosen constraints: Safe (nullable → required is NOT safe)
- Tighten constraints: Requires data validation first

---

## Conclusion

This data contract defines the core entities, relationships, and business rules for the service provider application. All development should respect these contracts to ensure data integrity and API stability.

**Key Takeaways:**
1. Customer has NO contact info → use Contact model
2. Vehicle (VIN) and Equipment (SN) are separate models
3. Inspections are immutable after finalization
4. Defects are idempotent (stable identity)
5. Work orders link back to inspections
6. Meters always increase, captured at service time

**When in doubt, refer to this contract.**

---

**Version History:**
- v1.0 (2025-01-XX): Initial data contract for clean rebuild
