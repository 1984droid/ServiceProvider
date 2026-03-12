# Inspection and Work Order Flows - Detailed Guide

Complete documentation of how inspections are performed, how defects are identified, and how work orders are created.

---

## Table of Contents

1. [Overview](#overview)
2. [Data Sources and Foundation](#data-sources-and-foundation)
3. [Inspection Flow - Detailed](#inspection-flow---detailed)
4. [Work Order Flow - Detailed](#work-order-flow---detailed)
5. [Integration Points](#integration-points)
6. [Data Journey Examples](#data-journey-examples)

---

## Overview

### The Complete Journey

```
Customer → Vehicle/Equipment → Inspection → Defects → Work Orders → Completion
   ↓            ↓                   ↓           ↓            ↓            ↓
Database    Database            Template    Analysis    Scheduling    Tracking
```

### Key Principles

1. **Equipment Data is Foundational** - Everything starts with clean asset records
2. **Tags Drive Applicability** - Equipment tags determine which inspections apply
3. **Inspections are Immutable** - Once finalized, inspection data cannot change
4. **Defects are Idempotent** - Re-running rules doesn't create duplicates
5. **Work Orders Link Back** - Always traceable to source (inspection, customer request, etc.)

---

## Data Sources and Foundation

### 1. Customer Data (Origin)

**Created First:** Customer and Contact records establish the business relationship.

```
Customer: ABC Trucking
├── primary_contact: Jane Smith (Fleet Manager)
├── contacts: [Jane Smith, John Doe (Maintenance), Bill Jones (Billing)]
├── address: Physical location for service
└── usdot_number: 999888 (if applicable)
```

**Data Source:** User entry via:
- Manual creation in admin or API
- USDOT lookup (pre-fills from FMCSA data)
- Import from spreadsheet/legacy system

**Used For:**
- Identifying who owns the assets
- Routing inspection reports
- Billing and invoicing
- Contact for scheduling

---

### 2. Asset Data (Vehicle/Equipment)

**Created Next:** Assets are registered to customers with basic information.

#### Vehicle Creation Flow

```
Vehicle: Ford F-350 Bucket Truck
├── customer: ABC Trucking
├── vin: 1FDUF5GT8KED12345
├── unit_number: T-101
├── year/make/model: 2020 Ford F-350
├── license_plate: ABC1234
├── tags: ['BUCKET_TRUCK', 'INSULATED_BOOM']
└── odometer_miles: 45000
```

**Data Source:**
- **Manual Entry:** User types in VIN, unit number, basic info
- **VIN Decode (NHTSA vPIC API):** Automatically fills year, make, model, engine specs
  - API Call: `GET https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{VIN}?format=json`
  - Creates `VINDecodeData` record with structured data
  - User can copy relevant fields to Vehicle record
- **Import:** Bulk vehicle import from customer's fleet list

**VIN Decode Data Structure:**
```json
VINDecodeData (1:1 with Vehicle)
{
  "vin": "1FDUF5GT8KED12345",
  "model_year": 2020,
  "make": "Ford",
  "model": "F-350 Super Duty",
  "manufacturer": "FORD MOTOR COMPANY",
  "vehicle_type": "Truck",
  "body_class": "Cab & Chassis",
  "engine_model": "Power Stroke 6.7L",
  "engine_cylinders": 8,
  "displacement_liters": 6.7,
  "fuel_type_primary": "Diesel",
  "gvwr_min_lbs": 10001,
  "gvwr_max_lbs": 14000,
  "plant_city": "Louisville",
  "plant_state": "KY",
  "decoded_at": "2025-01-15T10:00:00Z",
  "raw_response": { ... complete NHTSA response ... }
}
```

#### Equipment Creation Flow

```
Equipment: Terex HyPower 40 Aerial Device
├── customer: ABC Trucking
├── serial_number: SN-123456-ABC
├── asset_number: A-501 (customer's internal tracking)
├── equipment_type: AERIAL_DEVICE
├── manufacturer: Terex
├── model: HyPower 40
├── year: 2018
├── mounted_on_vehicle: T-101 (VIN: 1FDUF5GT8KED12345)
├── tags: ['AERIAL_DEVICE', 'INSULATED_BOOM', 'DIELECTRIC']
└── equipment_data: {} (populated later)
```

**Data Source:**
- **Manual Entry:** User types serial number, manufacturer, model
- **Nameplate Photo Recognition (Future):** OCR from equipment nameplate photo
- **Import:** From customer's equipment inventory

**Equipment Tags:** Determine inspection applicability
- `AERIAL_DEVICE` → ANSI A92.2 inspection required
- `INSULATED_BOOM` → Dielectric test data required
- `DIELECTRIC` → Same as INSULATED_BOOM
- `CRANE` → ASME B30.5 crane inspection
- `DIGGER_DERRICK` → Combined aerial + auger inspections

---

### 3. Equipment Data Collection (On-Demand)

**Triggered When:** User starts an inspection on equipment with specific tags.

#### The Tag-Based Data Collection Flow

**Step 1: User Initiates Inspection**
```
User: "I want to inspect Equipment A-501"
System: Checks equipment.tags → ['AERIAL_DEVICE', 'INSULATED_BOOM', 'DIELECTRIC']
System: Checks equipment.equipment_data → {} (empty or incomplete)
System: "Before we can inspect this equipment, we need placard and dielectric data"
```

**Step 2: System Determines Required Forms**

```python
def get_required_forms(equipment):
    """
    Based on equipment tags, determine what data needs to be collected.
    """
    required_forms = []

    if 'AERIAL_DEVICE' in equipment.tags:
        if not equipment.equipment_data.get('placard'):
            required_forms.append({
                'form_id': 'placard',
                'title': 'Placard Information',
                'fields': [
                    {'name': 'max_platform_height', 'type': 'number', 'unit': 'ft'},
                    {'name': 'max_working_height', 'type': 'number', 'unit': 'ft'},
                    {'name': 'platform_capacity', 'type': 'number', 'unit': 'lbs'},
                    {'name': 'max_wind_speed', 'type': 'number', 'unit': 'mph'},
                ]
            })

    if 'INSULATED_BOOM' in equipment.tags or 'DIELECTRIC' in equipment.tags:
        if not equipment.equipment_data.get('dielectric'):
            required_forms.append({
                'form_id': 'dielectric',
                'title': 'Dielectric Test Information',
                'fields': [
                    {'name': 'insulation_rating_kv', 'type': 'number', 'unit': 'kV'},
                    {'name': 'last_test_date', 'type': 'date'},
                    {'name': 'next_test_due', 'type': 'date'},
                    {'name': 'test_certificate_number', 'type': 'string'},
                ]
            })

    return required_forms
```

**Step 3: User Fills Equipment Data Forms**

**Placard Form (from equipment nameplate):**
```
Equipment Placard Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This information is found on the equipment's placard/nameplate.

Max Platform Height:     [40] ft
Max Working Height:      [46] ft
Platform Capacity:       [500] lbs
Max Horizontal Reach:    [35] ft
Max Wind Speed:          [28] mph

[Save to Equipment Record]
```

**Dielectric Form (from test certificate):**
```
Dielectric Test Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Required for insulated equipment working near energized lines.

Insulation Rating:       [46] kV
Last Test Date:          [2024-06-15] (YYYY-MM-DD)
Next Test Due:           [2025-06-15] (YYYY-MM-DD)
Test Certificate #:      [DT-2024-1234]
Test Voltage:            [69] kV (calculated: rating × 1.5)

[Save to Equipment Record]
```

**Step 4: Data Saved to Equipment**

```python
# API Call: POST /api/equipment/{id}/update_data/
equipment.equipment_data = {
    "placard": {
        "max_platform_height": 40,
        "max_working_height": 46,
        "platform_capacity": 500,
        "max_horizontal_reach": 35,
        "max_wind_speed": 28,
        "unit_system": "imperial"
    },
    "dielectric": {
        "insulation_rating_kv": 46,
        "last_test_date": "2024-06-15",
        "next_test_due": "2025-06-15",
        "test_certificate_number": "DT-2024-1234",
        "test_voltage_kv": 69
    },
    "last_updated": "2025-01-15T14:30:00Z",
    "updated_by": "user_abc123"
}
equipment.save()
```

**This data is now available for ALL future inspections** - no need to re-enter unless it changes.

---

## Inspection Flow - Detailed

### Overview of Inspection Process

```
Start → Select Asset → Check Data → Run Inspection → Submit Steps → Auto-Rules → Defects → Finalize
```

### Step-by-Step Inspection Flow

#### Step 1: Inspection Initiation

**User Action:** "Start inspection on equipment A-501"

**System Actions:**
```python
# 1. Validate asset exists and is active
equipment = Equipment.objects.get(id=equipment_id, is_active=True)
customer = equipment.customer

# 2. Check equipment data completeness
required_forms = get_required_forms(equipment)
if required_forms:
    return {"status": "data_required", "forms": required_forms}

# 3. Determine applicable inspection template
template = determine_inspection_template(equipment)
# Based on tags: AERIAL_DEVICE → ansi_a92_2_periodic template

# 4. Create InspectionRun (DRAFT status)
inspection_run = InspectionRun.objects.create(
    asset_type='EQUIPMENT',
    asset_id=equipment.id,
    customer_id=customer.id,  # Denormalized for queries
    template_key='ansi_a92_2_periodic',
    program_key='ANSI_A92_2',
    status='DRAFT',
    started_at=timezone.now(),
    template_snapshot=template.to_dict(),  # Immutable copy
    step_data={},
    inspector_name=request.user.get_full_name()
)
```

**InspectionRun Created:**
```json
{
  "id": "uuid-inspection-1",
  "asset_type": "EQUIPMENT",
  "asset_id": "uuid-equipment-a501",
  "customer_id": "uuid-abc-trucking",
  "template_key": "ansi_a92_2_periodic",
  "program_key": "ANSI_A92_2",
  "status": "DRAFT",
  "started_at": "2025-01-15T15:00:00Z",
  "finalized_at": null,
  "inspector_name": "John Doe",
  "template_snapshot": {
    "modules": [
      {
        "key": "visual_inspection",
        "title": "Visual Inspection",
        "steps": [
          {
            "key": "boom_condition",
            "title": "Boom Structure Condition",
            "type": "condition_check",
            "required": true
          },
          {
            "key": "hydraulic_leaks",
            "title": "Check for Hydraulic Leaks",
            "type": "pass_fail",
            "required": true
          }
        ]
      },
      {
        "key": "function_tests",
        "title": "Function Tests",
        "steps": [...]
      }
    ]
  },
  "step_data": {},
  "notes": ""
}
```

#### Step 2: Inspector Performs Inspection

**User Interface Shows:** Step-by-step checklist from template

**Module 1: Visual Inspection**

**Step 1: Boom Structure Condition**
```
Inspect the boom structure for:
- Cracks, bends, or deformations
- Corrosion or rust
- Missing or loose fasteners
- Damaged welds

Condition: [⚪ Good] [⚪ Fair] [⚪ Poor] [⚪ Critical]
Photos: [Add Photo]
Notes: [Optional text field]

[Submit Step]
```

**User submits:** "Good" with a photo

**API Call:**
```http
POST /api/inspections/{id}/submit-step/

{
  "module_key": "visual_inspection",
  "step_key": "boom_condition",
  "response": {
    "condition": "good",
    "photos": ["photo_uuid_1"],
    "notes": "Boom structure in excellent condition, no visible wear"
  }
}
```

**System Updates InspectionRun:**
```python
inspection_run.step_data['visual_inspection']['boom_condition'] = {
    "condition": "good",
    "photos": ["photo_uuid_1"],
    "notes": "Boom structure in excellent condition, no visible wear",
    "submitted_at": "2025-01-15T15:05:00Z",
    "submitted_by": "John Doe"
}
inspection_run.status = 'IN_PROGRESS'  # First step submitted
inspection_run.save()
```

**Step 2: Check for Hydraulic Leaks**
```
Inspect hydraulic system for leaks at:
- Cylinder seals
- Hose connections
- Pump and valves
- Reservoir

Result: [⚪ Pass] [⚪ Fail]
If FAIL, describe location: [Text field]
Photos: [Add Photo]

[Submit Step]
```

**User submits:** "Fail" - leak found at boom cylinder

**API Call:**
```http
POST /api/inspections/{id}/submit-step/

{
  "module_key": "visual_inspection",
  "step_key": "hydraulic_leaks",
  "response": {
    "result": "fail",
    "location": "Primary boom cylinder - rod seal",
    "severity": "minor",
    "photos": ["photo_uuid_2", "photo_uuid_3"],
    "notes": "Small leak at rod seal, approximately 2 drops per cycle"
  }
}
```

**System Actions:**
1. **Updates step_data**
2. **Triggers auto-rule evaluation**
3. **Creates defect if rule matches**

#### Step 3: Auto-Rule Evaluation

**Rule Engine Checks:**
```python
def evaluate_rules_for_step(inspection_run, module_key, step_key, response):
    """
    After each step submission, evaluate if any defect rules are triggered.
    """
    rules = InspectionRule.objects.filter(
        template_key=inspection_run.template_key,
        module_key=module_key,
        step_key=step_key
    )

    for rule in rules:
        if rule.evaluate(response):
            # Rule matched - create defect
            create_defect(
                inspection_run=inspection_run,
                rule=rule,
                module_key=module_key,
                step_key=step_key,
                response=response
            )
```

**Example Rule:**
```json
{
  "rule_id": "hydraulic_leak_fail",
  "template_key": "ansi_a92_2_periodic",
  "module_key": "visual_inspection",
  "step_key": "hydraulic_leaks",
  "condition": "response.result == 'fail'",
  "defect": {
    "severity": "MAJOR",
    "title": "Hydraulic Leak Detected",
    "description": "Hydraulic leak found during inspection. Location: {response.location}",
    "recommended_action": "Repair or replace leaking component before next use"
  }
}
```

**Rule Matches → Defect Created:**
```python
# Compute stable defect identity (for idempotency)
defect_identity = hashlib.sha256(
    f"{inspection_run.id}{module_key}{step_key}{rule.rule_id}".encode()
).hexdigest()

# Create or update defect
defect, created = InspectionDefect.objects.get_or_create(
    defect_identity=defect_identity,
    defaults={
        'inspection_run_id': inspection_run.id,
        'module_key': module_key,
        'step_key': step_key,
        'rule_id': rule.rule_id,
        'severity': 'MAJOR',
        'title': 'Hydraulic Leak Detected',
        'description': f'Hydraulic leak found during inspection. Location: {response["location"]}',
        'defect_details': {
            'location': response['location'],
            'severity_assessment': response.get('severity'),
            'photos': response.get('photos', []),
            'notes': response.get('notes')
        },
        'evaluation_trace': {
            'rule_id': rule.rule_id,
            'rule_condition': rule.condition,
            'evaluated_at': timezone.now(),
            'response_data': response
        },
        'status': 'OPEN'
    }
)
```

**Defect Record Created:**
```json
{
  "id": "uuid-defect-1",
  "inspection_run_id": "uuid-inspection-1",
  "defect_identity": "sha256_hash_here",
  "module_key": "visual_inspection",
  "step_key": "hydraulic_leaks",
  "rule_id": "hydraulic_leak_fail",
  "severity": "MAJOR",
  "title": "Hydraulic Leak Detected",
  "description": "Hydraulic leak found during inspection. Location: Primary boom cylinder - rod seal",
  "defect_details": {
    "location": "Primary boom cylinder - rod seal",
    "severity_assessment": "minor",
    "photos": ["photo_uuid_2", "photo_uuid_3"],
    "notes": "Small leak at rod seal, approximately 2 drops per cycle"
  },
  "evaluation_trace": {
    "rule_id": "hydraulic_leak_fail",
    "rule_condition": "response.result == 'fail'",
    "evaluated_at": "2025-01-15T15:10:00Z",
    "response_data": { ... }
  },
  "status": "OPEN",
  "created_at": "2025-01-15T15:10:00Z"
}
```

#### Step 4: Inspector Continues Through All Steps

Inspector completes all required steps in all modules:
- Visual Inspection (5 steps)
- Function Tests (8 steps)
- Load Test (3 steps)
- Dielectric Test (4 steps - uses equipment_data.dielectric)

**Each step:**
1. User submits response
2. step_data updated
3. Rules evaluated
4. Defects created as needed

#### Step 5: Inspection Finalization

**User Action:** "Finalize Inspection"

**System Validation:**
```python
def can_finalize(inspection_run):
    """Check if inspection can be finalized."""
    template = inspection_run.template_snapshot
    step_data = inspection_run.step_data

    # Check all required steps are completed
    for module in template['modules']:
        for step in module['steps']:
            if step.get('required'):
                step_response = step_data.get(module['key'], {}).get(step['key'])
                if not step_response:
                    return False, f"Required step not completed: {step['title']}"

    return True, "All required steps completed"

can_finalize, message = can_finalize(inspection_run)
if not can_finalize:
    return {"error": message}
```

**Finalization Actions:**
```python
# Set finalized timestamp
inspection_run.finalized_at = timezone.now()
inspection_run.status = 'COMPLETED'

# Capture inspector signature
inspection_run.inspector_signature = {
    "signature_data": signature_image_base64,
    "signed_at": timezone.now(),
    "signed_by": request.user.get_full_name(),
    "ip_address": request.META.get('REMOTE_ADDR')
}

inspection_run.save()

# Inspection is now IMMUTABLE
# step_data cannot be changed
# template_snapshot cannot be changed
# Only notes and defect status can be updated
```

**Inspection Complete:**
```json
{
  "id": "uuid-inspection-1",
  "status": "COMPLETED",
  "started_at": "2025-01-15T15:00:00Z",
  "finalized_at": "2025-01-15T16:30:00Z",
  "inspector_signature": {
    "signature_data": "base64_image_data",
    "signed_at": "2025-01-15T16:30:00Z",
    "signed_by": "John Doe",
    "ip_address": "192.168.1.100"
  },
  "step_data": { ... all completed steps ... },
  "defects_count": 3
}
```

---

## Work Order Flow - Detailed

### Overview of Work Order Process

```
Inspection Defects → Review → Select → Create Work Order → Schedule → Execute → Complete
```

### Step-by-Step Work Order Flow

#### Step 1: Review Inspection Defects

**User Action:** Views completed inspection

**API Call:**
```http
GET /api/inspections/{id}/defects/
```

**Response:**
```json
{
  "inspection_id": "uuid-inspection-1",
  "defects": [
    {
      "id": "uuid-defect-1",
      "severity": "MAJOR",
      "title": "Hydraulic Leak Detected",
      "description": "Hydraulic leak found during inspection. Location: Primary boom cylinder - rod seal",
      "status": "OPEN",
      "module": "visual_inspection",
      "step": "hydraulic_leaks"
    },
    {
      "id": "uuid-defect-2",
      "severity": "MINOR",
      "title": "Worn Platform Decking",
      "description": "Platform deck shows wear, replacement recommended within 6 months",
      "status": "OPEN",
      "module": "visual_inspection",
      "step": "platform_condition"
    },
    {
      "id": "uuid-defect-3",
      "severity": "ADVISORY",
      "title": "Dielectric Test Due Soon",
      "description": "Next dielectric test due in 30 days",
      "status": "OPEN",
      "module": "dielectric_test",
      "step": "test_certificate_check"
    }
  ]
}
```

#### Step 2: User Decides Which Defects Need Work Orders

**Business Rules:**
- **CRITICAL defects:** Must create work order immediately, equipment out of service
- **MAJOR defects:** Should create work order, schedule repair
- **MINOR defects:** Optional work order, or add to PM schedule
- **ADVISORY defects:** Informational, typically no work order

**User Selects:** Defects 1 and 2 (MAJOR and MINOR) for work order

#### Step 3: Create Work Order from Defects

**API Call:**
```http
POST /api/work-orders/from-inspection/

{
  "inspection_run_id": "uuid-inspection-1",
  "defect_ids": ["uuid-defect-1", "uuid-defect-2"],
  "priority": "HIGH",
  "description": "Repair hydraulic leak and replace platform decking per inspection findings",
  "scheduled_date": "2025-01-20",
  "assigned_to": "Tech-Mike-Johnson",
  "notes": "Customer requested repair before next job on 1/22"
}
```

**System Actions:**
```python
def create_work_order_from_inspection(data):
    """Create work order linked to inspection defects."""

    # 1. Validate inspection and defects
    inspection = InspectionRun.objects.get(id=data['inspection_run_id'])
    defects = InspectionDefect.objects.filter(
        id__in=data['defect_ids'],
        inspection_run_id=inspection.id
    )

    # 2. Get asset and customer info
    equipment = Equipment.objects.get(id=inspection.asset_id)
    customer = equipment.customer

    # 3. Generate work order number
    work_order_number = generate_work_order_number()  # e.g., "WO-2025-00123"

    # 4. Create work order
    work_order = WorkOrder.objects.create(
        work_order_number=work_order_number,
        customer_id=customer.id,
        asset_type='EQUIPMENT',
        asset_id=equipment.id,
        status='SCHEDULED',
        priority=data['priority'],
        source='INSPECTION',
        source_inspection_run_id=inspection.id,
        description=data['description'],
        scheduled_date=data['scheduled_date'],
        assigned_to=data['assigned_to'],
        notes=data['notes']
    )

    # 5. Link defects to work order (many-to-many)
    work_order.defects.set(defects)

    # 6. Update defect statuses
    defects.update(status='WORK_ORDER_CREATED')

    # 7. Send notifications
    notify_assigned_technician(work_order)
    notify_customer_contact(work_order, customer)

    return work_order
```

**Work Order Created:**
```json
{
  "id": "uuid-workorder-1",
  "work_order_number": "WO-2025-00123",
  "customer_id": "uuid-abc-trucking",
  "customer_name": "ABC Trucking",
  "asset_type": "EQUIPMENT",
  "asset_id": "uuid-equipment-a501",
  "asset_description": "Terex HyPower 40 - SN: SN-123456-ABC - Unit: A-501",
  "status": "SCHEDULED",
  "priority": "HIGH",
  "source": "INSPECTION",
  "source_inspection_run_id": "uuid-inspection-1",
  "description": "Repair hydraulic leak and replace platform decking per inspection findings",
  "scheduled_date": "2025-01-20",
  "assigned_to": "Tech-Mike-Johnson",
  "assigned_to_name": "Mike Johnson",
  "notes": "Customer requested repair before next job on 1/22",
  "defects": [
    {
      "id": "uuid-defect-1",
      "severity": "MAJOR",
      "title": "Hydraulic Leak Detected",
      "status": "WORK_ORDER_CREATED"
    },
    {
      "id": "uuid-defect-2",
      "severity": "MINOR",
      "title": "Worn Platform Decking",
      "status": "WORK_ORDER_CREATED"
    }
  ],
  "created_at": "2025-01-15T17:00:00Z",
  "started_at": null,
  "completed_at": null
}
```

#### Step 4: Technician Starts Work

**API Call:**
```http
PATCH /api/work-orders/{id}/start/

{
  "odometer_at_service": 45120,
  "notes": "Beginning repairs - hydraulic cylinder seal replacement"
}
```

**System Updates:**
```python
work_order.status = 'IN_PROGRESS'
work_order.started_at = timezone.now()
work_order.odometer_at_service = 45120
work_order.notes += f"\n[{timezone.now()}] Beginning repairs - hydraulic cylinder seal replacement"
work_order.save()
```

#### Step 5: Work Completion

**API Call:**
```http
PATCH /api/work-orders/{id}/complete/

{
  "odometer_at_service": 45125,
  "engine_hours_at_service": 2105,
  "completion_notes": "Replaced boom cylinder rod seal. Replaced platform decking with new aluminum tread plate. Function tested - no leaks. Equipment ready for service.",
  "parts_used": [
    {"part_number": "CYL-SEAL-40", "description": "Boom Cylinder Rod Seal", "quantity": 1},
    {"part_number": "DECK-ALU-4X8", "description": "Aluminum Tread Plate 4x8", "quantity": 2}
  ],
  "labor_hours": 4.5
}
```

**System Actions:**
```python
# 1. Update work order
work_order.status = 'COMPLETED'
work_order.completed_at = timezone.now()
work_order.odometer_at_service = data['odometer_at_service']
work_order.engine_hours_at_service = data['engine_hours_at_service']
work_order.notes += f"\n[{timezone.now()}] {data['completion_notes']}"

# 2. Update equipment meters
equipment = work_order.asset
equipment.odometer_miles = data['odometer_at_service']
equipment.engine_hours = data['engine_hours_at_service']
equipment.save(update_fields=['odometer_miles', 'engine_hours', 'updated_at'])

# 3. Update linked defects
work_order.defects.all().update(status='RESOLVED')

# 4. Save parts and labor (separate models, not shown here)
for part in data['parts_used']:
    WorkOrderPart.objects.create(
        work_order=work_order,
        part_number=part['part_number'],
        description=part['description'],
        quantity=part['quantity']
    )

WorkOrderLabor.objects.create(
    work_order=work_order,
    hours=data['labor_hours'],
    technician=work_order.assigned_to
)

work_order.save()

# 5. Send completion notifications
notify_customer_completion(work_order)
notify_fleet_manager(work_order)
```

**Work Order Completed:**
```json
{
  "id": "uuid-workorder-1",
  "work_order_number": "WO-2025-00123",
  "status": "COMPLETED",
  "priority": "HIGH",
  "source": "INSPECTION",
  "source_inspection_run_id": "uuid-inspection-1",
  "scheduled_date": "2025-01-20",
  "started_at": "2025-01-20T08:00:00Z",
  "completed_at": "2025-01-20T13:30:00Z",
  "assigned_to": "Tech-Mike-Johnson",
  "odometer_at_service": 45125,
  "engine_hours_at_service": 2105,
  "completion_notes": "Replaced boom cylinder rod seal. Replaced platform decking with new aluminum tread plate. Function tested - no leaks. Equipment ready for service.",
  "parts_used": [...],
  "labor_hours": 4.5,
  "defects": [
    {
      "id": "uuid-defect-1",
      "status": "RESOLVED"
    },
    {
      "id": "uuid-defect-2",
      "status": "RESOLVED"
    }
  ]
}
```

---

## Integration Points

### Where Data Flows Between Systems

```
Customer/Assets → Inspection → Defects → Work Orders → Completion → Asset Updates
     ↓              ↓            ↓           ↓             ↓             ↓
  Database       Template      Rules      Scheduling   Tracking    Meter Updates
```

### Key Integration Points

#### 1. Equipment Data → Inspection Template Selection

```python
def select_inspection_template(equipment):
    """
    Equipment tags determine which inspection template applies.
    """
    templates = []

    if 'AERIAL_DEVICE' in equipment.tags:
        templates.append('ansi_a92_2_periodic')

    if 'CRANE' in equipment.tags:
        templates.append('asme_b30_5_crane_periodic')

    if 'DIGGER_DERRICK' in equipment.tags:
        templates.extend(['ansi_a92_2_periodic', 'auger_inspection'])

    return templates
```

#### 2. Equipment Data → Inspection Step Evaluation

```python
def evaluate_step(equipment, step_key, response):
    """
    Equipment data used during step evaluation.
    """
    if step_key == 'dielectric_test_due':
        # Check equipment_data for test dates
        dielectric = equipment.equipment_data.get('dielectric', {})
        next_test_due = dielectric.get('next_test_due')

        if next_test_due:
            days_until_due = (parse_date(next_test_due) - timezone.now().date()).days

            if days_until_due < 30:
                return {
                    'result': 'warning',
                    'message': f'Dielectric test due in {days_until_due} days'
                }

    if step_key == 'load_test':
        # Use equipment_data for capacity limits
        placard = equipment.equipment_data.get('placard', {})
        max_capacity = placard.get('platform_capacity', 0)

        test_load = response.get('test_load')
        if test_load > max_capacity:
            return {
                'result': 'fail',
                'message': f'Test load {test_load} exceeds placard capacity {max_capacity}'
            }
```

#### 3. Inspection Step Response → Defect Generation

```python
def generate_defects_from_response(inspection_run, module_key, step_key, response):
    """
    Step responses trigger defect creation via rules.
    """
    # Get applicable rules
    rules = InspectionRule.objects.filter(
        template_key=inspection_run.template_key,
        module_key=module_key,
        step_key=step_key
    )

    defects_created = []

    for rule in rules:
        # Evaluate rule condition against response
        if evaluate_condition(rule.condition, response):
            # Create defect
            defect = create_defect_from_rule(
                inspection_run=inspection_run,
                rule=rule,
                module_key=module_key,
                step_key=step_key,
                response=response
            )
            defects_created.append(defect)

    return defects_created
```

#### 4. Defects → Work Order Creation

```python
# User selects which defects to address
selected_defects = InspectionDefect.objects.filter(
    id__in=selected_defect_ids,
    status='OPEN'
)

# Create work order
work_order = WorkOrder.objects.create(
    source='INSPECTION',
    source_inspection_run=inspection_run,
    customer=inspection_run.customer,
    asset_type=inspection_run.asset_type,
    asset_id=inspection_run.asset_id,
    description=generate_description_from_defects(selected_defects),
    priority=calculate_priority(selected_defects)  # Based on severity
)

# Link defects
work_order.defects.set(selected_defects)

# Update defect status
selected_defects.update(status='WORK_ORDER_CREATED')
```

#### 5. Work Order Completion → Asset Meter Updates

```python
def complete_work_order(work_order, completion_data):
    """
    When work order completes, update asset meters.
    """
    # Update work order
    work_order.status = 'COMPLETED'
    work_order.completed_at = timezone.now()
    work_order.odometer_at_service = completion_data['odometer']
    work_order.save()

    # Update asset meters
    if work_order.asset_type == 'VEHICLE':
        vehicle = Vehicle.objects.get(id=work_order.asset_id)
        vehicle.odometer_miles = completion_data['odometer']
        vehicle.save()

    elif work_order.asset_type == 'EQUIPMENT':
        equipment = Equipment.objects.get(id=work_order.asset_id)
        equipment.engine_hours = completion_data['engine_hours']
        equipment.save()

    # Mark defects as resolved
    work_order.defects.all().update(status='RESOLVED')
```

---

## Data Journey Examples

### Example 1: Complete Flow - New Equipment Inspection

**Timeline:**

**Day 1 - Asset Onboarding:**
```
09:00 - Customer "ABC Trucking" created in system
09:15 - Contact "Jane Smith" added as primary contact
09:30 - Vehicle "T-101" (Ford F-350) added with VIN decode
09:45 - Equipment "A-501" (Terex aerial device) added
        - Serial: SN-123456-ABC
        - Tags: ['AERIAL_DEVICE', 'INSULATED_BOOM', 'DIELECTRIC']
        - equipment_data: {} (empty)
```

**Day 2 - Inspection:**
```
08:00 - Inspector starts inspection on equipment A-501
08:01 - System checks equipment_data → empty
08:02 - System prompts for placard and dielectric data
08:05 - Inspector enters placard data from nameplate
08:10 - Inspector enters dielectric data from test certificate
08:15 - Equipment data saved, inspection begins
08:20 - Visual inspection module (8 steps)
09:00 - Function test module (12 steps)
09:45 - Load test module (4 steps)
10:15 - Dielectric test review (3 steps)
10:30 - Inspection finalized with signature

Defects Generated:
- MAJOR: Hydraulic leak at boom cylinder
- MINOR: Worn platform decking
- ADVISORY: Next dielectric test due in 30 days
```

**Day 2 - Work Order Creation:**
```
10:45 - Fleet manager reviews inspection results
10:50 - Selects MAJOR and MINOR defects for work order
10:55 - Work order WO-2025-00123 created
        - Priority: HIGH
        - Scheduled: Next Monday (5 days out)
        - Assigned: Tech Mike Johnson
11:00 - Email sent to technician and customer contact
```

**Day 7 - Work Order Execution:**
```
08:00 - Technician starts work order
08:15 - Parts ordered: cylinder seal, platform decking
10:30 - Seal replacement complete
12:00 - Platform decking replacement complete
12:30 - Function test - no leaks, all systems operational
12:45 - Work order marked complete
        - Labor: 4.5 hours
        - Odometer updated: 45,125 miles
        - Defects marked RESOLVED
13:00 - Completion notification sent to customer
```

### Example 2: Non-Inspection Work Order

**Scenario:** Customer calls with breakdown

```
Customer Call: "Our bucket truck T-101 won't start, need service ASAP"

12:00 - Service coordinator creates work order
        - Source: CUSTOMER_REQUEST (not INSPECTION)
        - Priority: URGENT
        - Asset: Vehicle T-101
        - Description: "Won't start - customer reports clicking noise"

12:05 - Work order assigned to available mobile technician
12:30 - Technician arrives on-site
13:00 - Diagnosis: Bad starter motor
13:30 - Parts ordered for same-day delivery
15:00 - Starter replacement complete
15:15 - Work order marked complete
        - No linked inspection
        - No defects
        - Just parts and labor
```

### Example 3: PM Schedule Work Order

**Scenario:** Scheduled preventive maintenance

```
System generates PM work orders automatically:

Equipment A-501 is due for:
- 6-month ANSI A92.2 periodic inspection
- Annual dielectric test
- 2000-hour hydraulic fluid change

01:00 AM - Automated job runs
01:05 - Creates work order WO-2025-00456
        - Source: PM_SCHEDULE
        - Priority: MEDIUM
        - Scheduled: Next available date
        - Description: "6-month periodic inspection and PM per schedule"

01:10 - Email sent to scheduling coordinator
09:00 - Coordinator reviews and assigns technician
09:15 - Customer contacted to schedule
```

---

## Summary

### Data Sources Recap

1. **Customer/Contact Data** - Manual entry or USDOT lookup
2. **Vehicle Data** - Manual entry + VIN decode (NHTSA API)
3. **Equipment Data (Basic)** - Manual entry from nameplate
4. **Equipment Data (Detailed)** - Collected during first inspection based on tags
5. **Inspection Templates** - Pre-defined in system, selected by equipment tags
6. **Inspection Responses** - Inspector input during inspection
7. **Defects** - Auto-generated by rules based on inspection responses
8. **Work Orders** - Created from defects, customer requests, or PM schedule

### Flow Integration Recap

```
Foundation Data (Customer, Vehicle, Equipment)
    ↓
Equipment Tags determine applicability
    ↓
Inspection Template selected
    ↓
Inspector completes steps
    ↓
Responses evaluated by rules
    ↓
Defects auto-generated
    ↓
User creates Work Orders from defects
    ↓
Technician executes work
    ↓
Completion updates asset meters and defect status
    ↓
Cycle repeats for next inspection
```

### Key Takeaways

✅ **Equipment data is collected progressively** - starts basic, adds detail when needed
✅ **Tags drive everything** - determine inspections, required data, rules
✅ **Inspections are immutable** - audit trail is preserved
✅ **Defects are idempotent** - re-running rules doesn't duplicate
✅ **Work orders are traceable** - always linked back to source
✅ **Asset meters are updated** - work completion updates odometer/hours
✅ **Everything is interconnected** - but properly decoupled for flexibility

---

**Version:** 1.0
**Last Updated:** 2025-01-XX
