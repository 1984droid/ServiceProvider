# ServiceProvider - Data Contract

Complete data model specification for the ServiceProvider application.

## Architecture Overview

**Single-Tenant Django 6.0 Application**
- UUID primary keys, PostgreSQL 18+, Python 3.14+
- RESTful API via Django REST Framework
- JWT Authentication with role-based access control

## Core Principles

1. **Single Tenant** - One company instance per deployment
2. **UUID Keys** - All models use UUID primary keys
3. **Audit Trail** - All models include created_at/updated_at timestamps
4. **Capability-Based Operations** - Assets use JSON capabilities array for inspection/maintenance routing
5. **Polymorphic Asset References** - Work orders/inspections reference Vehicle or Equipment via asset_type/asset_id
6. **Template-Driven Inspections** - JSON templates with automated validation and defect generation
7. **Secure by Default** - All API endpoints require authentication and role-based permissions

---

## Module 0: Authentication (`apps/authentication`)

### Authentication System
**Technology:** JWT (JSON Web Tokens) via `djangorestframework-simplejwt`

**Token Strategy:**
- **Access Token:** 15-minute lifetime, contains user identity + permissions
- **Refresh Token:** 7-day lifetime, rotates on use, can be blacklisted
- **Storage:** Tokens stored client-side, refresh tokens tracked in database

**Endpoints:**
- `POST /api/auth/login/` - Obtain access + refresh tokens
- `POST /api/auth/logout/` - Blacklist refresh token
- `POST /api/auth/refresh/` - Rotate tokens
- `GET /api/auth/me/` - Get current user profile with permissions
- `PATCH /api/auth/me/` - Update user profile
- `POST /api/auth/change-password/` - Change password
- `POST /api/auth/register/` - Create user (admin only)
- `GET /api/auth/users/` - List users (admin only)

---

### Roles and Permissions

**7 Predefined Roles (Django Groups):**

1. **SUPER_ADMIN** - Full system access (all permissions)
2. **ADMIN** - Manage customers, assets, organization (32 permissions)
3. **INSPECTOR** - Perform inspections, view work orders (13 permissions)
4. **SERVICE_TECH** - Manage work orders, update assets (11 permissions)
5. **DISPATCHER** - Schedule inspections and work orders (15 permissions)
6. **CUSTOMER_SERVICE** - Manage customers, view reports (12 permissions)
7. **VIEWER** - Read-only access (10 permissions)

**Permission Strategy:**
- **Django Model Permissions:** Auto-generated `view`, `add`, `change`, `delete` per model
- **Custom Business Permissions:** Defined in `apps/authentication/permissions.py`
  - `CanEditOwnInspection` - Inspectors can only edit their own inspections
  - `CannotEditFinalizedInspection` - Completed inspections immutable (super admin only)
  - `CanViewDepartmentWorkOrders` - Department-based access filtering

**API Security:**
- All endpoints require `Authorization: Bearer <access_token>` header
- Permissions checked per request via DRF permission classes
- Object-level permissions for sensitive operations (inspection ownership, finalized state)

---

### User Model Integration

**Django User Model:**
- Standard `django.contrib.auth.User` model
- OneToOne relationship with `Employee` model (optional)
- Users can exist without employee record (system users, admins)
- Employees can exist without user (non-system staff)

**User Profile Response (`/api/auth/me/`):**
```json
{
  "id": 1,
  "username": "john.inspector",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "employee": {
    "id": "uuid",
    "employee_number": "EMP001",
    "full_name": "John Doe",
    "department": "Inspection",
    "department_code": "INSP",
    "title": "Senior Inspector"
  },
  "roles": ["INSPECTOR"],
  "permissions": [
    "inspections.view_inspectionrun",
    "inspections.add_inspectionrun",
    "inspections.change_inspectionrun",
    ...
  ],
  "last_login": "2026-03-12T10:30:00Z",
  "date_joined": "2025-01-15T09:00:00Z"
}
```

---

## Module 1: Organization (`apps/organization`)

### Company (Single-Tenant)
**Purpose:** Company information - only one record allowed

**Core Fields:**
- `name` (required), `dba_name`, `phone`, `email`, `website`
- Address: `address_line1`, `address_line2`, `city`, `state`, `zip_code`
- Tax/DOT: `tax_id`, `usdot_number`
- `logo` (ImageField), `settings` (JSONField)

**Constraints:** Only one company record can exist (enforced in save())

---

### Department
**Purpose:** Organizational departments for employee grouping

**Core Fields:**
- `name` (required, unique), `code` (required, unique, e.g., "SRV")
- `description`, `manager` FK(Employee)
- `is_active`, `allows_floating` (default: True)

**Relationships:**
- `base_employees` - Employees with this as base department
- `floating_employees` - Employees who can float here (M2M)
- `work_orders` - Work orders assigned to this department (M2M)

**Properties:** `employee_count`, `total_employee_count`

---

### Employee
**Purpose:** Staff members with department assignments

**Core Fields:**
- `user` FK(User), `employee_number` (required, unique)
- `first_name`, `last_name`, `email`, `phone`
- `base_department` FK(Department, required)
- `floating_departments` M2M(Department)
- `title`, `hire_date`, `termination_date`, `is_active`
- `certifications` (JSONField), `skills` (JSONField), `settings` (JSONField)

**Validation:**
- `termination_date` cannot be before `hire_date`
- Terminated employees must be `is_active=False`

**Properties:** `full_name`, `all_departments`
**Methods:** `can_work_in_department(department)`

---

## Module 2: Customers (`apps/customers`)

### Customer
**Purpose:** Service customers - fleet owners/operators

**Core Fields:**
- `name` (required), `account_number`, `email`, `phone`
- Address: `address`, `city`, `state`, `zip_code`
- DOT: `usdot_number` (indexed), `mc_number`
- `is_active`, `primary_contact` FK(Contact)
- `tags` (JSONField), `settings` (JSONField)

**Relationships:** `contacts`, `vehicles`, `equipment`

---

### Contact
**Purpose:** Contact persons for customers

**Core Fields:**
- `customer` FK(Customer, required)
- `first_name`, `last_name`, `email`, `phone`, `title`
- `is_primary`, `receive_invoices`, `receive_reports`, `receive_alerts`
- `notes`

**Properties:** `full_name`, `is_primary`

---

### USDOTProfile
**Purpose:** USDOT/FMCSA data cache for customers (OneToOne)

**Core Fields:**
- `customer` OneToOne(Customer), `usdot_number`, `mc_number`
- `legal_name`, `dba_name`
- Physical: `physical_address`, `physical_city`, `physical_state`, `physical_zip`
- Mailing: `mailing_address`, `mailing_city`, `mailing_state`, `mailing_zip`
- `phone`, `email`, `safety_rating`
- `total_power_units`, `total_drivers`

---

## Module 3: Assets (`apps/assets`)

### Vehicle
**Purpose:** Customer vehicles (trucks, vans, trailers)

**Core Fields:**
- `customer` FK(Customer, required)
- `vin` (17 chars, required, unique), `unit_number`
- `year` (1900-2100), `make`, `model`
- `body_type` - CharField with choices: `AERIAL`, etc. (only types we have inspection templates for)
- `license_plate`, `license_state`
- `odometer_miles` (≥0), `engine_hours` (≥0)
- `is_active`
- `capabilities` (JSONField) - **For inspection/maintenance impact only**
- `notes`

**Capabilities (VIN-Driven):**
Minimal set - only if affects inspection/maintenance:
- `AIR_BRAKES` - From VIN decode abs field
- `HYDRAULIC_BRAKES` - From VIN decode abs field
- `FOUR_WHEEL_DRIVE` - From VIN decode if available

**Body Type:**
- Controlled choices, only added when we have inspection templates
- Currently: `AERIAL` (for ANSI A92.2 aerial devices)
- Future: REFUSE, SWEEPER, SCHOOL_BUS, DUMP, TANK, TOW

**Relationships:** OneToOne `vin_decode`, OneToMany `equipment` (mounted)

---

### Equipment
**Purpose:** Work equipment mounted on vehicles (aerial devices, cranes, etc.)

**Core Fields:**
- `customer` FK(Customer, required)
- `serial_number` (required, unique), `asset_number`
- `manufacturer`, `model`, `year`, `equipment_type`
- `mounted_on_vehicle` FK(Vehicle, optional, SET_NULL)
- `is_active`
- `capabilities` (JSONField) - **For inspection/maintenance impact only**
- `equipment_data` (JSONField) - **Detailed specs populated during inspection setup**
- `notes`

**Capabilities (Inspection-Driven):**
Only capabilities that affect inspections/maintenance:
- `DIELECTRIC` - Requires annual dielectric testing (ANSI/ASTM)
- `HYDRAULIC` - Requires hydraulic system inspection
- `PNEUMATIC` - Requires air system inspection
- `ELECTRIC` - Requires electrical system inspection
- `PTO_DRIVEN` - Requires PTO system inspection
- `ENGINE_DRIVEN` - Requires engine maintenance (oil, filters)

**Equipment Data Example:**
```json
{
  "placard": {
    "max_platform_height": 45,
    "max_working_height": 50,
    "platform_capacity": 500
  },
  "dielectric": {
    "insulation_rating_kv": 46,
    "last_test_date": "2024-01-15",
    "next_test_due": "2025-01-15",
    "test_certificate_number": "DT-2024-001"
  },
  "hydraulic": {
    "hydraulic_fluid_type": "AW-32",
    "reservoir_capacity_gallons": 15,
    "last_service_date": "2024-06-01"
  }
}
```

---

### VINDecodeData
**Purpose:** Cached VIN decode results from NHTSA vPIC API (OneToOne with Vehicle)

**Core Fields:**
- `vehicle` OneToOne(Vehicle), `vin` (17 chars)
- Decoded: `model_year`, `make`, `model`, `manufacturer`
- Classification: `vehicle_type`, `body_class`
- Engine: `engine_model`, `engine_configuration`, `engine_cylinders`, `displacement_liters`
- Fuel: `fuel_type_primary`, `fuel_type_secondary`
- Weight: `gvwr` (class), `gvwr_min_lbs`, `gvwr_max_lbs`
- Safety: `abs` (brake system type), `airbag_locations`
- Plant: `plant_city`, `plant_state`, `plant_country`
- Status: `error_code`, `error_text`, `decoded_at`
- `raw_response` (JSONField) - Full NHTSA response

**Key Uses:**
- Automatic vehicle classification (Class 2-8 trucks, trailers, buses)
- Brake system type → `AIR_BRAKES` or `HYDRAULIC_BRAKES` capability
- "Incomplete Vehicle" flag → indicates aftermarket body (garbage truck, sweeper, etc.)

---

## Module 4: Inspections (`apps/inspections`)

### InspectionRun
**Purpose:** Execution of an inspection template on an asset

**Core Fields:**
- `customer` FK(Customer, required)
- `asset_type` ('VEHICLE' or 'EQUIPMENT'), `asset_id` (UUID)
- `template_key` (required), `program_key`
- `status` (DRAFT/IN_PROGRESS/COMPLETED)
- `started_at` (required), `finalized_at`
- `inspector_name`, `inspector_signature` (JSONField)
- `template_snapshot` (JSONField, required) - **Immutable template copy**
- `step_data` (JSONField) - Collected inspection data
- `notes`
- `inspection_outcome` (PASS/PASS_WITH_REPAIRS/FAIL) - **Auto-calculated at finalization**
- `outcome_summary` (JSONField) - Detailed outcome breakdown with defect counts

**Validation:**
- Asset customer must match inspection customer
- Status cannot go backwards (COMPLETED → DRAFT)
- After finalization, `step_data`, `template_snapshot`, and `status` are immutable

**Properties:** `asset`, `is_finalized`, `defect_count`, `critical_defect_count`

**Outcome Calculation (Auto-computed at finalization):**
The system automatically determines inspection outcome based on defects:
- **FAIL**: Any CRITICAL severity defects OR blocking step failures (blocking_fail: true)
- **PASS_WITH_REPAIRS**: Any MAJOR severity defects (but no CRITICAL)
- **PASS**: Only MINOR/ADVISORY defects or no defects

The `outcome_summary` JSON contains:
```json
{
  "total_defects": 5,
  "defects_by_severity": {
    "CRITICAL": 0,
    "MAJOR": 2,
    "MINOR": 3,
    "ADVISORY": 0
  },
  "blocking_failures": [],
  "critical_defects_found": false,
  "major_defects_found": true,
  "equipment_safe_for_operation": true,
  "requires_immediate_action": false,
  "requires_repairs": true
}
```

---

### InspectionDefect
**Purpose:** Defect/finding - created from auto-rules OR manual capture during inspection

**Core Fields:**
- `inspection_run` FK(InspectionRun, required)
- `module_key` (optional, legacy), `step_key` (required), `rule_id`
- `defect_identity` (64 chars, unique) - SHA256 hash for idempotency
- `severity` (CRITICAL/MAJOR/MINOR/ADVISORY)
- `status` (OPEN/WORK_ORDER_CREATED/RESOLVED)
- `title` (required), `description`
- `defect_details` (JSONField) - Structured data (actual/expected values)
- `evaluation_trace` (JSONField) - Complete rule evaluation audit trail

**Defect Creation Sources:**
1. **Auto-generated from rules** (`auto_defect_on` in template) - System evaluates conditions
2. **Manual capture** (`ADD_DEFECT_ITEMS` mode) - Inspector documents structured defects

**Manual Defect Schema (8 fields):**
When step has `defect_schema_ref` and `ui.mode: "ADD_DEFECT_ITEMS"`:
```json
{
  "defect_id": "uuid",
  "title": "Structural bolt wear detected",
  "severity": "SERVICE_REQUIRED",
  "description": "Excessive wear on pedestal mounting bolts...",
  "component": "Pedestal Mounting Bolts to Chassis",
  "location": "Driver side pedestal",
  "photo_evidence": ["photo1.jpg", "photo2.jpg"],
  "corrective_action": "Replace all pedestal mounting bolts...",
  "standard_reference": "ANSI A92.2-2021 Section 8.2.4(13)"
}
```

**Photo Requirements:**
- Photos conditionally required based on severity
- `SERVICE_REQUIRED` and `UNSAFE_OUT_OF_SERVICE` severities require photos
- Photos stored in `defect_details.photos` array

**Idempotency:**
```python
# Auto-generated defects
defect_identity = SHA256(run_id + module_key + step_key + rule_id)

# Manual defects
defect_identity = SHA256(run_id + module_key + step_key + "manual_" + defect_id)
```
Re-running evaluation updates existing defects rather than creating duplicates.

**Rule Assertions (14 types):**
- **Numeric:** EQUALS, GT, LT, GTE, LTE, IN_RANGE
- **String:** EQUALS, CONTAINS
- **Boolean:** TRUE, FALSE
- **Enum:** EQUALS, IN
- **Existence:** EXISTS, NOT_EXISTS

**Severity Mapping (Template → Database):**
- `UNSAFE_OUT_OF_SERVICE` → `CRITICAL`
- `SERVICE_REQUIRED` → `MAJOR`
- `DEGRADED_PERFORMANCE` → `MAJOR`
- `MINOR_ISSUE` → `MINOR`
- `MINOR` → `MINOR`
- `SAFE` → `ADVISORY`
- `ADVISORY_NOTICE` → `ADVISORY`

---

## Module 5: Work Orders (`apps/work_orders`)

### WorkOrder
**Purpose:** Maintenance/repair work orders

**Core Fields:**
- `work_order_number` (unique, auto: WO-YYYY-#####)
- `customer` FK(Customer, required)
- `asset_type` ('VEHICLE' or 'EQUIPMENT'), `asset_id` (UUID)
- `departments` M2M(Department), `assigned_employees` M2M(Employee)
- `status` (DRAFT/OPEN/IN_PROGRESS/COMPLETED/CANCELLED)
- `priority` (LOW/MEDIUM/HIGH/URGENT)
- `source` (INSPECTION/CUSTOMER_REQUEST/PM_SCHEDULE/BREAKDOWN)
- `source_inspection_run` FK(InspectionRun, optional)
- `description` (required), `scheduled_date`
- `started_at`, `completed_at`
- `total_cost`, `labor_hours`
- `notes`

**Validation:**
- Asset customer must match work order customer
- If source is INSPECTION, source_inspection_run must be for same asset
- Cannot reopen COMPLETED or CANCELLED work orders
- `completed_at` cannot be before `started_at`

**Properties:** `asset`, `defect_count`, `is_completed`, `is_cancelled`

---

### WorkOrderDefect
**Purpose:** Junction table linking work orders to inspection defects (M2M)

**Core Fields:**
- `work_order` FK(WorkOrder, required)
- `defect` FK(InspectionDefect, required)
- `linked_at` (auto)

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
    │    ├─> VINDecodeData (1)
    │    └─> Equipment (*) [mounted_on_vehicle]
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

## Database Constraints

### Unique Constraints
- Company: Only one record (enforced in model)
- Department: name, code
- Employee: employee_number
- Vehicle: vin
- Equipment: serial_number
- InspectionDefect: defect_identity
- WorkOrder: work_order_number
- WorkOrderDefect: (work_order, defect)

### Foreign Key Cascades
- **CASCADE:** Contacts, Assets, InspectionRuns, InspectionDefects, WorkOrderDefects
- **SET_NULL:** Department.manager, Equipment.mounted_on_vehicle, WorkOrder.source_inspection_run
- **PROTECT:** Employee.base_department

### Performance Indexes
- Customer: usdot_number, is_active
- Vehicle: customer + is_active, vin, body_type
- Equipment: customer + is_active, serial_number
- Employee: base_department + is_active, employee_number
- InspectionRun: customer + status, asset_type + asset_id
- WorkOrder: customer + status, asset_type + asset_id, scheduled_date

---

## Frontend Architecture

### Technology Stack

**Framework:**
- React 19.2.4 (latest stable)
- Vite 8.0.0 (build tool + dev server)
- TypeScript 5.9.3 (strict mode)

**State Management:**
- TanStack Query v5.90+ (server state)
- Zustand (client state)

**UI & Styling:**
- Tailwind CSS v4.2.1 (utility-first CSS)
- CSS Variables (runtime theming)
- Atomic Design Pattern (component structure)

**Data Fetching:**
- Axios (HTTP client with interceptors)
- JWT token auto-refresh
- Request/response interceptors

**Testing:**
- Playwright (E2E testing)
- Page Object Model pattern

**Forms & Validation:**
- TanStack Form v0.2+
- React Hook Form
- Zod (schema validation)

**Routing:**
- TanStack Router v1.166+ (type-safe routing)

**Tables:**
- TanStack Table v8.21+ (data grids)

### Project Structure

```
frontend/
├── src/
│   ├── api/              # API client layer
│   ├── components/
│   │   ├── ui/           # Atoms (Button, Input, Badge, Card)
│   │   ├── layout/       # Layout components
│   │   ├── forms/        # Reusable form components
│   │   └── domain/       # Business-specific components
│   ├── features/         # Feature modules
│   │   ├── auth/
│   │   ├── inspections/
│   │   ├── customers/
│   │   ├── assets/
│   │   ├── work-orders/
│   │   └── organization/
│   ├── hooks/            # Custom React hooks
│   ├── store/            # Zustand stores
│   ├── lib/              # Utilities (axios, queryClient)
│   ├── config/           # Configuration (API, theme)
│   └── styles/           # Global styles + themes
└── e2e/                  # Playwright tests
```

### Authentication Flow

1. User submits credentials to `POST /api/auth/login/`
2. Backend returns JWT tokens (access + refresh)
3. Tokens stored in localStorage
4. Axios interceptor injects access token in all requests
5. On 401 response, interceptor auto-refreshes using refresh token
6. New tokens stored, original request retried
7. On refresh failure, user redirected to login

### API Integration

**Base Configuration:**
- Base URL: `/api` (proxied in dev, direct in production)
- Timeout: 30 seconds
- Headers: `Content-Type: application/json`, `Authorization: Bearer <token>`

**Endpoints Configuration:** `frontend/src/config/api.ts`
- Centralized endpoint definitions
- Type-safe endpoint builders
- Environment variable support

**API Clients:** `frontend/src/api/*.api.ts`
- One file per domain (auth, customers, inspections, etc.)
- TypeScript interfaces for requests/responses
- Reusable CRUD operations

### Theme System

**CSS Variables:** `frontend/src/styles/themes/`
- `default.css` - Light theme
- `dark.css` - Dark theme
- Custom themes easily added

**Runtime Switching:**
```typescript
import { loadTheme } from '@/config/theme';
loadTheme('dark');
```

**Customization:**
All theme variables use RGB triplets for Tailwind compatibility:
```css
--color-primary: 59 130 246;  /* Used as rgb(var(--color-primary)) */
```

### Component Patterns

**Atomic Design:**
- **Atoms:** Basic elements (Button, Input, Label)
- **Molecules:** Simple combinations (FormField)
- **Organisms:** Complex components (LoginForm, DataTable)
- **Templates:** Page layouts (DashboardLayout)
- **Pages:** Complete views (LoginPage, InspectionListPage)

**Reusability Principle:**
- Create new components only when existing ones can't be reused
- Extend base components with props/variants
- Maintain consistent look and feel

### Data Management

**No Hardcoded Data:**
- All data fetched from Django API
- Use `python manage.py seed_data` for test data
- Mock data only in Playwright tests

**Seed Data Includes:**
- 1 Company, 4 Departments, 6 Employees
- 6 Users (admin, inspector1/2, service1/2, support1)
- 3 Customers with contacts
- Multiple Vehicles, Trailers, Equipment

### Testing Strategy

**E2E Tests (Playwright):**
- Located in `frontend/e2e/`
- Page Object Model pattern
- Test fixtures for auth state
- Run with: `npm run test:e2e`

**Test Coverage:**
- Authentication flows (login, logout, token refresh)
- Protected route access
- User permission validation
- CRUD operations per feature

---

## Version History

- **v1.0** - Initial models: Customers, Assets, Inspections, Work Orders
- **v1.1** - Added Organization module: Company, Departments, Employees
- **v1.2** - Added multi-department/employee support to Work Orders
- **v1.3** - Simplified capabilities, added body_type to Vehicle, VIN-driven classification
- **v2.0** - Added Authentication module with JWT and RBAC
- **v2.1** - Added Frontend architecture with React 19, TanStack suite, theme system

---

**Last Updated:** March 12, 2026
