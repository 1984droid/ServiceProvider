# ServiceProvider - Data Contract

Complete data model specification for the ServiceProvider application.

## Architecture Overview

**Single-Tenant Django 6.0 Application**
- UUID primary keys across all models
- PostgreSQL 18+ database
- Python 3.14+
- RESTful API via Django REST Framework

---

## Core Principles

1. **Single Tenant** - One company instance per deployment
2. **UUID Keys** - All models use UUID primary keys
3. **Audit Trail** - All models include created_at/updated_at timestamps
4. **Capability-Based Operations** - Assets use JSON capabilities array for inspection/maintenance routing
5. **Polymorphic Asset References** - Work orders and inspections reference either Vehicle or Equipment via asset_type/asset_id
6. **Template-Driven Inspections** - Inspections use JSON templates with automated validation and defect generation

---

## Module 1: Organization (`apps/organization`)

### Company (Single-Tenant)
**Purpose:** Store company information - only one record allowed

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| name | CharField(255) | Required | Legal company name |
| dba_name | CharField(255) | Optional | Doing Business As name |
| phone | CharField(20) | Optional | Phone number |
| email | EmailField | Optional | Email address |
| website | URLField | Optional | Company website |
| address_line1 | CharField(255) | Optional | Street address |
| address_line2 | CharField(255) | Optional | Suite/unit/etc |
| city | CharField(100) | Optional | City |
| state | CharField(2) | Optional | State code |
| zip_code | CharField(20) | Optional | ZIP/postal code |
| tax_id | CharField(20) | Optional | EIN or Tax ID |
| usdot_number | CharField(20) | Optional | USDOT number |
| logo | ImageField | Optional | Company logo |
| settings | JSONField | Default: {} | Company-wide settings |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Validation:**
- Only one company record can exist (enforced in save())
- String representation: `dba_name` or falls back to `name`

**API Endpoints:**
- `GET /api/company/` - List companies
- `GET /api/company/current/` - Get current company
- `POST /api/company/` - Create company (only if none exists)
- `PUT /api/company/{id}/` - Update company

---

### Department
**Purpose:** Organizational departments for employee grouping

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| name | CharField(100) | Required, Unique | Department name |
| code | CharField(20) | Required, Unique | Short code (e.g., "SRV", "INSP") |
| description | TextField | Optional | Department description |
| manager | FK(Employee) | Optional | Department manager/supervisor |
| is_active | Boolean | Default: True | Whether department is active |
| allows_floating | Boolean | Default: True | Allow floating employees |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Relationships:**
- `base_employees` - Employees with this as base department (reverse FK)
- `floating_employees` - Employees who can float here (reverse M2M)
- `work_orders` - Work orders assigned to this department (reverse M2M)

**Properties:**
- `employee_count` - Count of active base employees
- `total_employee_count` - Count of base + floating active employees

**API Endpoints:**
- `GET /api/departments/` - List departments
- `GET /api/departments/{id}/employees/` - Get all employees in department
- `POST /api/departments/` - Create department

---

### Employee
**Purpose:** Staff members with department assignments

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| user | FK(User) | Optional | Django user for system access |
| employee_number | CharField(20) | Required, Unique | Employee ID/number |
| first_name | CharField(100) | Required | First name |
| last_name | CharField(100) | Required | Last name |
| email | EmailField | Optional | Email address |
| phone | CharField(20) | Optional | Phone number |
| base_department | FK(Department) | Required | Primary/home department |
| floating_departments | M2M(Department) | Optional | Additional departments |
| title | CharField(100) | Optional | Job title |
| hire_date | DateField | Optional | Date of hire |
| termination_date | DateField | Optional | Termination date |
| is_active | Boolean | Default: True | Active status |
| certifications | JSONField | Default: [] | List of certifications |
| skills | JSONField | Default: [] | List of skills |
| settings | JSONField | Default: {} | Employee settings |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Validation:**
- `termination_date` cannot be before `hire_date`
- Terminated employees must be `is_active=False`

**Properties:**
- `full_name` - Returns `{first_name} {last_name}`
- `all_departments` - List of base + floating departments

**Methods:**
- `can_work_in_department(department)` - Check if employee can work in department

**Relationships:**
- `managed_departments` - Departments where this employee is manager (reverse FK)
- `assigned_work_orders` - Work orders assigned to this employee (reverse M2M)

**API Endpoints:**
- `GET /api/employees/` - List employees
- `GET /api/employees/active/` - Get active employees only
- `GET /api/employees/{id}/can_work_in/?department_id={id}` - Check department access
- `POST /api/employees/` - Create employee

---

## Module 2: Customers (`apps/customers`)

### Customer
**Purpose:** Service customers - fleet owners/operators

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| name | CharField(255) | Required | Customer name |
| account_number | CharField(50) | Optional | Account number |
| email | EmailField | Optional | Email address |
| phone | CharField(20) | Optional | Phone number |
| address | CharField(255) | Optional | Street address |
| city | CharField(100) | Optional | City |
| state | CharField(2) | Optional | State code |
| zip_code | CharField(20) | Optional | ZIP code |
| usdot_number | CharField(20) | Optional, Indexed | USDOT number |
| mc_number | CharField(20) | Optional | MC number |
| is_active | Boolean | Default: True | Active status |
| primary_contact | FK(Contact) | Optional | Primary contact person |
| tags | JSONField | Default: {} | Customer tags/metadata |
| settings | JSONField | Default: {} | Customer settings |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Relationships:**
- `contacts` - Contact persons (reverse FK)
- `vehicles` - Customer vehicles (reverse FK)
- `equipment` - Customer equipment (reverse FK)

---

### Contact
**Purpose:** Contact persons for customers

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| customer | FK(Customer) | Required | Parent customer |
| first_name | CharField(100) | Required | First name |
| last_name | CharField(100) | Required | Last name |
| email | EmailField | Optional | Email address |
| phone | CharField(20) | Optional | Phone number |
| title | CharField(100) | Optional | Job title |
| is_primary | Boolean | Default: False | Is primary contact |
| receive_invoices | Boolean | Default: False | Receive invoices |
| receive_reports | Boolean | Default: False | Receive reports |
| receive_alerts | Boolean | Default: False | Receive alerts |
| notes | TextField | Optional | Additional notes |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Properties:**
- `full_name` - Returns `{first_name} {last_name}`
- `is_primary` - Matches customer.primary_contact

---

### USDOTProfile
**Purpose:** USDOT/FMCSA data cache for customers

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| customer | OneToOne(Customer) | Required | Parent customer |
| usdot_number | CharField(20) | Required | USDOT number |
| mc_number | CharField(20) | Optional | MC number |
| legal_name | CharField(255) | Optional | Legal business name |
| dba_name | CharField(255) | Optional | DBA name |
| physical_address | CharField(500) | Optional | Physical address |
| physical_city | CharField(100) | Optional | City |
| physical_state | CharField(2) | Optional | State |
| physical_zip | CharField(20) | Optional | ZIP code |
| mailing_address | CharField(500) | Optional | Mailing address |
| mailing_city | CharField(100) | Optional | Mailing city |
| mailing_state | CharField(2) | Optional | Mailing state |
| mailing_zip | CharField(20) | Optional | Mailing ZIP |
| phone | CharField(20) | Optional | Phone number |
| email | EmailField | Optional | Email address |
| safety_rating | CharField(50) | Optional | Safety rating |
| total_power_units | Integer | Optional | Total power units |
| total_drivers | Integer | Optional | Total drivers |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

---

## Module 3: Assets (`apps/assets`)

### Vehicle
**Purpose:** Customer vehicles (trucks, vans, etc.)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| customer | FK(Customer) | Required | Owner |
| vin | CharField(17) | Required, Unique, 17 chars | Vehicle VIN |
| unit_number | CharField(50) | Optional | Fleet unit number |
| year | Integer | Optional | Model year (1900-2100) |
| make | CharField(100) | Optional | Manufacturer |
| model | CharField(100) | Optional | Model name |
| license_plate | CharField(20) | Optional | License plate |
| license_state | CharField(2) | Optional | License state |
| odometer_miles | Decimal | Optional, ≥0 | Odometer reading |
| engine_hours | Decimal | Optional, ≥0 | Engine hours |
| is_active | Boolean | Default: True | Active status |
| capabilities | JSONField | Default: [] | **Capabilities for template routing** |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Validation:**
- VIN must be exactly 17 characters
- `odometer_miles` and `engine_hours` must be ≥ 0
- `year` must be between 1900 and 2100

**Capability-Based Template Routing:**
The `capabilities` JSON array dictates what inspection templates apply:
```json
["UTILITY_TRUCK", "INSULATED_BOOM", "DIELECTRIC"]
```

**Examples:**
- `["AERIAL_DEVICE"]` - Basic aerial lift requiring ANSI A92.2 periodic inspection
- `["AERIAL_DEVICE", "INSULATING_SYSTEM"]` - Insulated aerial device requiring dielectric testing
- `["CRANE", "MOBILE"]` - Mobile crane requiring ASME B30.5 inspection

**Equipment Data:**
The `equipment_data` field stores detailed specifications populated during inspection setup:
```json
{
  "placard": {
    "rated_capacity": 500,
    "max_working_height": 45,
    "max_horizontal_reach": 35
  },
  "dielectric": {
    "insulation_class": "Class A",
    "rated_voltage": 46000,
    "test_voltage": 69000
  }
}
```

---

### Equipment
**Purpose:** Customer equipment (aerial lifts, trailers, etc.)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| customer | FK(Customer) | Required | Owner |
| serial_number | CharField(100) | Required, Unique | Serial number |
| asset_number | CharField(50) | Optional | Asset/fleet number |
| manufacturer | CharField(100) | Optional | Manufacturer |
| model | CharField(100) | Optional | Model name |
| year | Integer | Optional | Model year |
| equipment_type | CharField(100) | Optional | Equipment type |
| is_active | Boolean | Default: True | Active status |
| capabilities | JSONField | Default: [] | **Capabilities for template routing** |
| equipment_data | JSONField | Default: {} | **Detailed specs/placard data** |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Capability-Based Template Routing:**
The `capabilities` JSON array dictates what inspection templates apply:
```json
["AERIAL_DEVICE", "INSULATING_SYSTEM", "BARE_HAND_WORK_UNIT"]
```

**Examples:**
- `["AERIAL_DEVICE"]` - Basic aerial lift requiring ANSI A92.2 periodic inspection
- `["AERIAL_DEVICE", "INSULATING_SYSTEM"]` - Insulated aerial device requiring dielectric testing
- `["CRANE", "MOBILE"]` - Mobile crane requiring ASME B30.5 inspection

**Equipment Data:**
The `equipment_data` field stores detailed specifications populated during inspection setup:
```json
{
  "placard": {
    "rated_capacity": 500,
    "max_working_height": 45,
    "max_horizontal_reach": 35
  },
  "dielectric": {
    "insulation_class": "Class A",
    "rated_voltage": 46000,
    "test_voltage": 69000
  }
}
```

---

### VINDecodeData
**Purpose:** Cached VIN decode results from NHTSA

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| vehicle | OneToOne(Vehicle) | Required | Parent vehicle |
| vin | CharField(17) | Required | VIN |
| model_year | Integer | Optional | Decoded year |
| make | CharField(100) | Optional | Decoded make |
| model | CharField(100) | Optional | Decoded model |
| manufacturer | CharField(255) | Optional | Manufacturer |
| vehicle_type | CharField(100) | Optional | Vehicle type |
| body_class | CharField(100) | Optional | Body class |
| engine_model | CharField(100) | Optional | Engine model |
| engine_cylinders | Integer | Optional | Cylinder count |
| displacement_liters | Decimal | Optional | Engine displacement |
| fuel_type_primary | CharField(50) | Optional | Fuel type |
| gvwr | CharField(50) | Optional | GVWR class |
| gvwr_min_lbs | Integer | Optional | Min GVWR (lbs) |
| gvwr_max_lbs | Integer | Optional | Max GVWR (lbs) |
| error_code | CharField(10) | Optional | Error code if decode failed |
| raw_response | JSONField | Optional | Full NHTSA response |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

---

## Module 4: Inspections (`apps/inspections`)

### InspectionRun
**Purpose:** Execution of an inspection template on an asset

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| customer | FK(Customer) | Required | Customer |
| asset_type | CharField(20) | Required | 'VEHICLE' or 'EQUIPMENT' |
| asset_id | UUID | Required | Vehicle or Equipment ID |
| template_key | CharField(100) | Required | Template identifier |
| program_key | CharField(100) | Optional | Program identifier |
| status | CharField(20) | Required | DRAFT/IN_PROGRESS/COMPLETED |
| started_at | DateTime | Required | Start timestamp |
| finalized_at | DateTime | Optional | Finalization timestamp |
| inspector_name | CharField(200) | Optional | Inspector name |
| inspector_signature | JSONField | Optional | Digital signature data |
| template_snapshot | JSONField | Required | **Immutable template copy** |
| step_data | JSONField | Default: {} | Collected inspection data |
| notes | TextField | Optional | Inspector notes |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Validation:**
- Asset customer must match inspection customer
- Status cannot go backwards (COMPLETED → DRAFT)
- `template_snapshot` must be a dict with 'modules' key
- After finalization, `step_data`, `template_snapshot`, and `status` are immutable

**Properties:**
- `asset` - Returns actual Vehicle or Equipment instance
- `is_finalized` - True if finalized_at is set
- `defect_count` - Count of associated defects
- `critical_defect_count` - Count of CRITICAL defects

---

### InspectionDefect
**Purpose:** Defect/finding from inspection

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| inspection_run | FK(InspectionRun) | Required | Parent inspection |
| module_key | CharField(100) | Required | Template module |
| step_key | CharField(100) | Required | Template step |
| rule_id | CharField(100) | Required | Rule that failed |
| defect_identity | CharField(64) | Required, Unique | SHA256 hash for idempotency |
| severity | CharField(20) | Required | CRITICAL/MAJOR/MINOR/ADVISORY |
| status | CharField(20) | Required | OPEN/ACKNOWLEDGED/RESOLVED |
| title | CharField(255) | Required | Defect title |
| description | TextField | Optional | Description |
| defect_details | JSONField | Optional | Structured defect data |
| evaluation_trace | JSONField | Default: {} | Rule evaluation trace |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Validation:**
- `defect_identity` must be exactly 64 characters (SHA256 hex)
- `defect_details` must be a dict if provided

**Idempotency:**
`defect_identity = SHA256(run_id + module_key + step_key + rule_id)`

---

## Module 5: Work Orders (`apps/work_orders`)

### WorkOrder
**Purpose:** Maintenance/repair work orders

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| work_order_number | CharField(50) | Unique, Auto | Format: WO-YYYY-##### |
| customer | FK(Customer) | Required | Customer |
| asset_type | CharField(20) | Required | 'VEHICLE' or 'EQUIPMENT' |
| asset_id | UUID | Required | Vehicle or Equipment ID |
| departments | M2M(Department) | Optional | **Departments involved** |
| assigned_employees | M2M(Employee) | Optional | **Assigned employees** |
| status | CharField(20) | Required | DRAFT/OPEN/IN_PROGRESS/COMPLETED/CANCELLED |
| priority | CharField(20) | Required | LOW/MEDIUM/HIGH/URGENT |
| source | CharField(30) | Required | INSPECTION/CUSTOMER_REQUEST/PM_SCHEDULE/BREAKDOWN |
| source_inspection_run | FK(InspectionRun) | Optional | Source inspection if applicable |
| description | TextField | Required | Work description |
| scheduled_date | DateField | Optional | Scheduled date |
| assigned_to | CharField(200) | Optional | **Legacy field** (use assigned_employees) |
| started_at | DateTime | Optional | Work start time |
| completed_at | DateTime | Optional | Work completion time |
| total_cost | Decimal | Optional | Total cost |
| labor_hours | Decimal | Optional | Labor hours |
| notes | TextField | Optional | Additional notes |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Validation:**
- Asset customer must match work order customer
- If source is INSPECTION, source_inspection_run must be for same asset
- Cannot reopen COMPLETED or CANCELLED work orders
- `completed_at` cannot be before `started_at`
- `scheduled_date` cannot be in past for DRAFT status

**Auto-Generation:**
- `work_order_number` is auto-generated: `WO-2025-00123`

**Multi-Department Support:**
Work orders can involve multiple departments (e.g., Service + Parts):
```python
work_order.departments.add(service_dept, parts_dept)
work_order.assigned_employees.add(tech1, tech2)
```

**Properties:**
- `asset` - Returns actual Vehicle or Equipment
- `defect_count` - Count of linked defects
- `is_completed` - True if status is COMPLETED
- `is_cancelled` - True if status is CANCELLED

---

### WorkOrderDefect
**Purpose:** Junction table linking work orders to inspection defects

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| work_order | FK(WorkOrder) | Required | Work order |
| defect | FK(InspectionDefect) | Required | Inspection defect |
| linked_at | DateTime | Auto | When linked |
| created_at | DateTime | Auto | Creation timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

**Validation:**
- Work order and defect must belong to same customer
- Work order and defect must be for same asset
- Unique constraint on (work_order, defect)

**Relationships:**
- One work order can address multiple defects
- One defect can be linked to multiple work orders (e.g., parts order + repair)

---

## Data Relationships

```
Organization:
Company (1)
  └─> Departments (*)
       ├─> Employees (*) [base_department]
       └─> Employees (*) [floating via M2M]

Customers:
Customer (*)
  ├─> Contacts (*)
  ├─> Vehicles (*)
  ├─> Equipment (*)
  └─> USDOTProfile (1)

Assets → Inspections → Work Orders:
Vehicle/Equipment
  ├─> InspectionRuns (*)
  │    └─> InspectionDefects (*)
  │         └─> WorkOrderDefects (*) ─> WorkOrders (*)
  └─> WorkOrders (*) [direct]

Work Order Assignments:
WorkOrder
  ├─> Departments (*) [M2M]
  └─> Employees (*) [M2M]
```

---

## Tag-Based Routing System

### Concept
Assets (Vehicles and Equipment) use JSON `tags` fields to dictate which inspection programs and maintenance schedules apply. This provides flexible, dynamic routing without hardcoded business logic.

### Example: Aerial Lift
```json
{
  "equipment_category": "AERIAL_LIFT",
  "inspection_programs": ["ANSI_A92_2", "OSHA_1910"],
  "insulation_class": "CLASS_A",
  "maintenance_schedule": "PM_QUARTERLY",
  "capacity": "60ft",
  "manufacturer_program": "GENIE_CERTIFIED"
}
```

### Example: Service Van
```json
{
  "vehicle_class": "LIGHT_DUTY_TRUCK",
  "inspection_programs": ["DOT_ANNUAL"],
  "maintenance_schedule": "PM_5000_MILES",
  "gvwr_class": "CLASS_2"
}
```

### Usage in Code
```python
# Get all equipment requiring ANSI A92.2 inspections
equipment = Equipment.objects.filter(
    tags__inspection_programs__contains='ANSI_A92_2',
    is_active=True
)

# Check if specific vehicle needs DOT annual
if 'DOT_ANNUAL' in vehicle.tags.get('inspection_programs', []):
    schedule_dot_inspection(vehicle)
```

---

## API Authentication

All API endpoints require authentication. Use Django REST Framework token authentication or session authentication.

**Headers:**
```
Authorization: Token <your-token>
```

---

## Database Constraints

### Unique Constraints
- Company: Only one record (enforced in model)
- Department: name, code
- Employee: employee_number
- Customer: (none - duplicates allowed)
- Vehicle: vin
- Equipment: serial_number
- InspectionDefect: defect_identity
- WorkOrder: work_order_number
- WorkOrderDefect: (work_order, defect)

### Foreign Key Cascades
- ON DELETE CASCADE: Contacts, Assets, InspectionRuns, InspectionDefects
- ON DELETE SET_NULL: Department.manager, WorkOrder.source_inspection_run
- ON DELETE PROTECT: Employee.base_department

---

## Indexes

### Performance Indexes
- Customer: usdot_number, is_active
- Vehicle: customer + is_active, vin
- Equipment: customer + is_active, serial_number
- Employee: base_department + is_active, employee_number
- InspectionRun: customer + status, asset_type + asset_id
- WorkOrder: customer + status, asset_type + asset_id, scheduled_date

---

## Version History

- **v1.0** - Initial models: Customers, Assets, Inspections, Work Orders
- **v1.1** - Added Organization module: Company, Departments, Employees
- **v1.2** - Added multi-department/employee support to Work Orders

---

**Last Updated:** March 11, 2025
