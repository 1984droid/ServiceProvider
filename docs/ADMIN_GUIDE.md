# Admin Interface Guide

Complete guide for managing NEW_BUILD_STARTER through Django Admin interface.

**Version:** 2.0 (Phase 5 Complete)
**Last Updated:** 2026-03-12
**Admin URL:** http://localhost:8100/admin/

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Customer Management](#customer-management)
3. [Contact Management](#contact-management)
4. [Asset Management](#asset-management)
5. [Inspection Management](#inspection-management)
6. [Defect Management](#defect-management)
7. [Work Order Management](#work-order-management)
8. [Organization Management](#organization-management)
9. [Advanced Features](#advanced-features)
10. [Common Tasks](#common-tasks)

---

## Getting Started

### Accessing Admin

1. Navigate to http://localhost:8100/admin/
2. Log in with superuser credentials
3. Main dashboard shows all app modules

### Admin Structure

```
ServiceProvider Admin
├── Customers
│   ├── Customers
│   ├── Contacts
│   └── USDOT Profiles
├── Assets
│   ├── Vehicles
│   ├── Equipment
│   └── VIN Decode Data
├── Inspections
│   ├── Inspection Runs
│   └── Inspection Defects
├── Work Orders
│   ├── Work Orders
│   └── Work Order Defects (junction)
└── Organization
    ├── Departments
    └── Employees
```

---

## Customer Management

### Customer Admin Features

**Location:** Admin → Customers → Customers

**List View Customization:**
- **Display Fields:** name, city, state, usdot_number, mc_number, is_active, created_at
- **Filters:** is_active, state, has_usdot, has_mc, has_contacts
- **Search:** name, legal_name, city, usdot_number, mc_number
- **Ordering:** Default by name (ascending)

**Detail View:**
- **Sections:**
  - Basic Information (name, legal_name)
  - Address (address_line1, address_line2, city, state, postal_code, country)
  - USDOT/MC Numbers
  - Status (is_active)
  - Notes
  - Metadata (created_at, updated_at - read-only)

- **Inline Editors:**
  - **Contacts Inline:** Add/edit customer contacts directly from customer page
  - **USDOT Profile Inline:** View/edit USDOT profile

**Custom Actions:**
- **Activate Customers:** Bulk activate selected customers (sets is_active=True)
- **Deactivate Customers:** Bulk deactivate selected customers (sets is_active=False)
- **Export to CSV:** Export selected customers with all fields

**Validation:**
- USDOT number must be unique if provided
- MC number must be unique if provided
- State must be valid 2-letter code
- Postal code format validated based on country

### Common Customer Tasks

**Task 1: Create New Customer**

1. Click "Add Customer" button
2. Fill required fields:
   - Name (display name)
   - Legal Name (official business name)
   - Address
   - City, State, Postal Code
3. Optionally add USDOT/MC numbers
4. Click "Save and continue editing" to add contacts
5. Use Contacts Inline to add primary contact
6. Click "Save"

**Task 2: Set Primary Contact**

1. Open customer detail page
2. Scroll to Contacts inline section
3. Check "Is primary" for desired contact
4. Uncheck "Is primary" for other contacts (only one can be primary)
5. Click "Save"

**Task 3: Merge Duplicate Customers**

1. Identify duplicate customer
2. Update all related records (vehicles, equipment, inspections) to point to correct customer
3. Deactivate or delete duplicate customer
4. Note: No automatic merge function - manual process

**Task 4: Bulk Deactivate Customers**

1. Go to Customer list
2. Check boxes for customers to deactivate
3. Select "Deactivate Customers" from Actions dropdown
4. Click "Go"
5. Confirm action

---

## Contact Management

### Contact Admin Features

**Location:** Admin → Customers → Contacts

**List View:**
- **Display Fields:** full_name, customer_name, email, phone, is_primary, is_active
- **Filters:** is_active, is_automated, is_primary, customer
- **Search:** first_name, last_name, email, phone, customer__name
- **Ordering:** Default by last_name, first_name

**Detail View:**
- **Sections:**
  - Personal Info (first_name, last_name, title)
  - Contact Info (email, phone, phone_extension, mobile)
  - Preferences (receive_invoices, receive_estimates, receive_service_updates, receive_inspection_reports)
  - Status (is_primary, is_automated, is_active)
  - Notes

**Custom Actions:**
- **Make Primary:** Set selected contact as primary for their customer
- **Send Test Email:** Send test email to verify contact info (future feature)

**Validation:**
- Email must be unique per customer
- Phone format validated (US format preferred)
- Cannot have multiple primary contacts per customer

---

## Asset Management

### Vehicle Admin Features

**Location:** Admin → Assets → Vehicles

**List View:**
- **Display Fields:** unit_number, customer_name, year, make, model, vin, is_active
- **Filters:** is_active, customer, year, make, has_equipment
- **Search:** vin, unit_number, make, model, license_plate, customer__name
- **Ordering:** Default by unit_number

**Detail View:**
- **Sections:**
  - Customer Link
  - Vehicle Info (VIN, year, make, model, unit_number, license_plate)
  - Meters (odometer_miles, engine_hours)
  - Status (is_active)
  - Tags (multi-select: BUCKET_TRUCK, CRANE, FLATBED, etc.)
  - Notes

- **Inline Editors:**
  - **Equipment Inline:** View/edit mounted equipment
  - **VIN Decode Data Inline:** View VIN decode information (read-only)

**Custom Actions:**
- **Decode VINs:** Trigger VIN decode for selected vehicles (placeholder - NHTSA integration pending)
- **Export Vehicle List:** Export with customer, equipment count, tags

**Custom Admin Methods:**
- **Equipment Count:** Shows number of mounted equipment pieces
- **Last Inspection Date:** Shows most recent inspection finalized_at
- **Open Work Orders:** Count of active work orders

### Equipment Admin Features

**Location:** Admin → Assets → Equipment

**List View:**
- **Display Fields:** asset_number, serial_number, customer_name, equipment_type, manufacturer, model, mounted_on_unit, is_active
- **Filters:** is_active, customer, equipment_type, mounted (has mounted_on_vehicle)
- **Search:** serial_number, asset_number, manufacturer, model, customer__name
- **Ordering:** Default by asset_number

**Detail View:**
- **Sections:**
  - Customer Link
  - Equipment Info (serial_number, asset_number, equipment_type, manufacturer, model, year)
  - Mounting (mounted_on_vehicle link)
  - Meters (engine_hours)
  - Status (is_active)
  - Tags (AERIAL_DEVICE, INSULATED_BOOM, DIELECTRIC, etc.)
  - Equipment Data (JSONField - placard, dielectric, etc.)
  - Notes

**Custom Actions:**
- **Mount Equipment:** Bulk mount to selected vehicle (must be same customer)
- **Unmount Equipment:** Bulk unmount selected equipment
- **Export Equipment List:** Export with customer, mounting status, tags

**Equipment Data Structure:**

The `equipment_data` JSONField stores structured data based on equipment tags:

```json
{
  "placard": {
    "max_platform_height": 40,
    "max_working_height": 46,
    "platform_capacity": 500,
    "max_wind_speed": 28
  },
  "dielectric": {
    "insulation_rating_kv": 46,
    "last_test_date": "2024-06-15",
    "next_test_due": "2025-06-15",
    "test_certificate_number": "DT-2024-1234"
  }
}
```

---

## Inspection Management

### Inspection Run Admin Features

**Location:** Admin → Inspections → Inspection Runs

**List View:**
- **Display Fields:** template_key, asset_display, customer_name, status, started_at, finalized_at, defect_count
- **Filters:** status, customer, asset_type, template_key, finalized (yes/no)
- **Search:** template_key, program_key, inspector_name, asset_id
- **Ordering:** Default by -started_at (newest first)

**Detail View:**
- **Sections:**
  - Asset Reference (asset_type, asset_id, customer)
  - Template Info (template_key, program_key, template_snapshot JSONField)
  - Status (status, started_at, finalized_at)
  - Inspector (inspector_name, inspector_signature JSONField)
  - Inspection Data (step_data JSONField)
  - Notes

- **Inline Editors:**
  - **Defects Inline:** View all defects generated from this inspection

**Read-Only Fields After Finalization:**
- step_data
- template_snapshot
- status

These fields become immutable once `finalized_at` is set (audit compliance).

**Custom Actions:**
- **Evaluate Rules:** Trigger defect rule evaluation on selected inspections
- **Export Inspection Report:** Generate PDF report (future feature)
- **Finalize Inspections:** Bulk finalize DRAFT/IN_PROGRESS inspections

**Custom Admin Methods:**
- **Defect Count:** Total defects for inspection
- **Critical Defect Count:** Count of CRITICAL severity defects
- **Is Finalized:** Boolean indicator
- **Asset Display:** Human-readable asset representation

**Important Notes:**
- Once finalized, inspections are locked for data integrity
- Use "Evaluate Rules" action after updating step_data
- Template snapshot preserves exact template version used

### Working with Inspection Step Data

The `step_data` JSONField stores all inspection responses:

**Structure:**
```json
{
  "module_key.step_key": {
    "response": "PASS|FAIL|NA",
    "notes": "Inspector notes",
    "photos": ["photo_uuid_1", "photo_uuid_2"],
    "measurements": {
      "pressure": 3000,
      "temperature": 72
    }
  }
}
```

**Admin Editing:**
1. Click JSON expand button in admin
2. Edit using JSON editor widget
3. Validate JSON syntax before saving
4. Cannot edit once finalized

---

## Defect Management

### Inspection Defect Admin Features

**Location:** Admin → Inspections → Inspection Defects

**List View:**
- **Display Fields:** title, severity, status, inspection_display, module_key, step_key, created_at
- **Filters:** severity, status, inspection_run, module_key
- **Search:** title, description, defect_identity, step_key
- **Ordering:** Default by -created_at (newest first)

**Detail View:**
- **Sections:**
  - Inspection Reference (inspection_run link)
  - Identity (defect_identity SHA256 hash)
  - Location (module_key, step_key, rule_id)
  - Severity (CRITICAL, MAJOR, MINOR, ADVISORY)
  - Status (OPEN, WORK_ORDER_CREATED, RESOLVED)
  - Defect Info (title, description)
  - Details (defect_details JSONField)
  - Audit Trail (evaluation_trace JSONField)

- **Inline Editors:**
  - **Work Orders Inline:** View linked work orders (via WorkOrderDefect junction)

**Custom Actions:**
- **Generate Work Orders:** Create work orders from selected defects
- **Mark Resolved:** Bulk mark defects as RESOLVED
- **Export Defect List:** Export with inspection, customer, work order status

**Custom Admin Methods:**
- **Inspection Display:** Shows template_key, asset, and date
- **Work Order Count:** Number of linked work orders
- **Days Since Created:** Age of defect

**Status Flow:**
```
OPEN (created by rule evaluation)
  ↓
WORK_ORDER_CREATED (work order generated and linked)
  ↓
RESOLVED (linked work order completed)
```

**Defect Details Structure:**

```json
{
  "location": "Boom cylinder connection",
  "photos": ["photo_uuid_1", "photo_uuid_2"],
  "measurements": {
    "leak_rate": "2 drops per minute",
    "pressure_at_failure": 2800
  },
  "resolution": "Replaced cylinder seals, tested at 3000 PSI"
}
```

---

## Work Order Management

### Work Order Admin Features

**Location:** Admin → Work Orders → Work Orders

**List View:**
- **Display Fields:** work_order_number, title, customer_name, asset_display, status, priority, approval_status, due_date
- **Filters:** status, priority, approval_status, customer, asset_type, source_type, assigned_to, department
- **Search:** work_order_number, title, description, verb, noun, service_location
- **Ordering:** Default by -created_at (newest first)

**Detail View:**
- **Sections:**
  - Work Order Number (auto-generated)
  - Customer & Asset (customer, asset_type, asset_id)
  - Task Definition (title, description, verb, noun, service_location)
  - Status & Priority (status, priority, approval_status)
  - Assignment (assigned_to, department, due_date)
  - Source (source_type, source_id)
  - Service Details (odometer_at_service, engine_hours_at_service)
  - Costing (labor_hours, parts_cost, labor_cost)
  - Timestamps (created_at, completed_at, updated_at)
  - Notes

- **Inline Editors:**
  - **Defects Inline:** View/link related defects (via WorkOrderDefect junction)

**Custom Actions:**
- **Approve Work Orders:** Bulk approve PENDING_APPROVAL work orders
- **Complete Work Orders:** Bulk mark as COMPLETED (prompts for completion data)
- **Export Work Orders:** Export with customer, asset, defects, costing

**Custom Admin Methods:**
- **Asset Display:** Human-readable asset representation
- **Defect Count:** Number of linked defects
- **Total Cost:** parts_cost + labor_cost
- **Days to Due Date:** Time until due_date (red if overdue)
- **Department Name:** Department display name

**Status Choices:**
- DRAFT - Initial creation
- PENDING - Approved and awaiting scheduling
- IN_PROGRESS - Work actively being performed
- ON_HOLD - Work paused
- COMPLETED - Work finished
- CANCELLED - Work order cancelled

**Priority Choices:**
- LOW - Routine maintenance
- NORMAL - Standard work
- HIGH - Important repairs
- URGENT - Safety-critical
- EMERGENCY - Asset down, immediate action

**Approval Status Choices:**
- DRAFT - Not yet submitted
- PENDING_APPROVAL - Awaiting approval
- APPROVED - Approved for work
- REJECTED - Declined by customer/manager

**Automatic Behaviors:**

1. **On COMPLETED Status:**
   - Updates linked defects to RESOLVED
   - Updates asset meters (odometer_miles, engine_hours) if values provided and higher than current
   - Sets completed_at timestamp

2. **On CANCELLED Status:**
   - Reverts linked defects to OPEN status
   - Allows defects to be reprocessed

3. **Work Order Number Generation:**
   - Auto-generates on save: `WO-{YEAR}-{SEQUENCE}`
   - Example: WO-2025-00123

### Work Order Defect Junction (Advanced)

**Location:** Admin → Work Orders → Work Order Defects

This junction table links work orders to defects (many-to-many relationship).

**Fields:**
- work_order (FK to WorkOrder)
- defect (FK to InspectionDefect)
- created_at

**Use Cases:**
- View all defects for a work order
- View all work orders addressing a defect
- Manual linking of defects to work orders

**Note:** Typically managed through inlines, rarely edited directly.

---

## Organization Management

### Department Admin Features

**Location:** Admin → Organization → Departments

**List View:**
- **Display Fields:** name, is_active, employee_count, created_at
- **Filters:** is_active
- **Search:** name, description
- **Ordering:** Default by name

**Detail View:**
- **Sections:**
  - Name
  - Description
  - Status (is_active)
  - Metadata (created_at, updated_at)

- **Inline Editors:**
  - **Employees Inline:** View employees in this department

**Custom Actions:**
- **Activate Departments:** Bulk activate
- **Deactivate Departments:** Bulk deactivate

**Examples:**
- Hydraulics
- Electrical
- Mechanical
- Fabrication
- Paint & Body
- Inspection Services

### Employee Admin Features

**Location:** Admin → Organization → Employees

**List View:**
- **Display Fields:** full_name, email, department_name, is_active, can_be_assigned_work_orders
- **Filters:** is_active, department, can_be_assigned_work_orders
- **Search:** first_name, last_name, email, employee_number
- **Ordering:** Default by last_name, first_name

**Detail View:**
- **Sections:**
  - Personal Info (first_name, last_name, employee_number)
  - Contact (email, phone)
  - Department (department link)
  - Permissions (can_be_assigned_work_orders, can_perform_inspections)
  - Status (is_active, hire_date)
  - Certifications (certifications JSONField)

**Custom Actions:**
- **Assign to Department:** Bulk assign employees to department
- **Enable Work Order Assignment:** Bulk enable can_be_assigned_work_orders
- **Export Employee List:** Export with department and certifications

**Certifications Structure:**

```json
{
  "certifications": [
    {
      "name": "ASE Master Technician",
      "number": "A1234567",
      "issued": "2023-01-15",
      "expires": "2026-01-15"
    },
    {
      "name": "ANSI A92.2 Inspector",
      "number": "INS-9876",
      "issued": "2024-06-01",
      "expires": "2027-06-01"
    }
  ]
}
```

---

## Advanced Features

### Bulk Actions

**Using Bulk Actions:**
1. Select items using checkboxes in list view
2. Choose action from Actions dropdown at top of list
3. Click "Go"
4. Confirm action on confirmation page

**Available Bulk Actions:**
- Customer: Activate/Deactivate, Export CSV
- Contact: Make Primary, Bulk Email (future)
- Vehicle: Decode VINs, Export List
- Equipment: Mount/Unmount, Export List
- Inspection: Evaluate Rules, Finalize, Export Reports
- Defect: Generate Work Orders, Mark Resolved
- Work Order: Approve, Complete, Export
- Department/Employee: Activate/Deactivate

### Filtering and Search

**Advanced Filtering:**
1. Use filter sidebar on right side of list views
2. Combine multiple filters
3. Filters persist during session

**Examples:**
```
# Find overdue high-priority work orders
Filters: priority=HIGH, status=PENDING, due_date < today

# Find critical defects without work orders
Filters: severity=CRITICAL, status=OPEN

# Find completed inspections this month
Filters: status=COMPLETED, finalized_at >= 2025-01-01
```

**Search Tips:**
- Search is case-insensitive
- Searches across all configured search fields
- Use partial matches (e.g., "hydr" finds "hydraulic")
- Combine with filters for precise results

### Data Export

**Export Methods:**

1. **Admin Bulk Action:**
   - Select records
   - Choose "Export to CSV" action
   - Download CSV file

2. **API Export:**
   - Use API with pagination disabled
   - Add `?format=json` to URL
   - Process with external tools

3. **Database Export:**
   - Use Django dumpdata command
   - Export specific models or full database

**Example CSV Exports:**
- Customer list with contacts and asset counts
- Work order history with costing data
- Defect trends by severity and status
- Inspection completion rates by template

### JSON Field Editing

**JSONField Editor in Admin:**
- Django admin provides JSON editor widget
- Syntax highlighting and validation
- Expand/collapse nested objects
- Copy/paste JSON from external tools

**Editing Best Practices:**
1. Validate JSON syntax before saving
2. Use consistent key naming (snake_case)
3. Document structure in model docstrings
4. Back up data before bulk JSON edits

**Common JSON Fields:**
- InspectionRun: template_snapshot, step_data, inspector_signature
- InspectionDefect: defect_details, evaluation_trace
- Equipment: equipment_data
- Employee: certifications

---

## Common Tasks

### Task 1: Set Up New Customer with Assets

**Steps:**
1. Create Customer:
   - Admin → Customers → Add Customer
   - Fill basic info, address, USDOT/MC

2. Add Primary Contact:
   - Use Contacts inline
   - Set "Is primary" checkbox

3. Add Vehicles:
   - Admin → Assets → Vehicles → Add Vehicle
   - Select customer from dropdown
   - Enter VIN, unit number, make, model
   - Add tags if applicable

4. Add Equipment:
   - Admin → Assets → Equipment → Add Equipment
   - Select customer and mounted_on_vehicle
   - Enter serial, asset number, type
   - Fill equipment_data if needed

### Task 2: Process Inspection and Generate Work Orders

**Steps:**
1. Review Completed Inspection:
   - Admin → Inspections → Inspection Runs
   - Filter: status=COMPLETED
   - Click inspection to review

2. Check Defects:
   - Scroll to Defects inline
   - Review severity and status
   - Note: OPEN defects need work orders

3. Generate Work Orders:
   - Select inspection(s)
   - Choose "Generate Work Orders" action
   - Configure min_severity (default: MAJOR)
   - Click "Go"

4. Approve Work Orders:
   - Admin → Work Orders → Work Orders
   - Filter: approval_status=PENDING_APPROVAL
   - Select work orders
   - Choose "Approve Work Orders" action

5. Assign Work:
   - Open work order detail
   - Set assigned_to (employee)
   - Set department
   - Set due_date
   - Update status to PENDING
   - Save

### Task 3: Complete Work Order

**Steps:**
1. Open Work Order:
   - Admin → Work Orders → Work Orders
   - Find work order (search by WO number or asset)

2. Update Status:
   - Change status to IN_PROGRESS (when starting)
   - Record odometer_at_service and/or engine_hours_at_service

3. Complete:
   - Change status to COMPLETED
   - Set completed_at (auto-populated)
   - Enter labor_hours, parts_cost, labor_cost
   - Add completion notes
   - Save

4. Verify Automatic Updates:
   - Check linked defects → status should be RESOLVED
   - Check asset → meters should be updated (if values were higher)

### Task 4: Monitor Work Order Pipeline

**Dashboard Views:**

**Pending Approvals:**
```
Admin → Work Orders → Work Orders
Filter: approval_status=PENDING_APPROVAL
Sort by: -created_at
```

**In Progress:**
```
Filter: status=IN_PROGRESS
Sort by: due_date
```

**Overdue:**
```
Filter: status=PENDING, due_date < today
Sort by: priority, due_date
```

**Critical Defects:**
```
Admin → Inspections → Defects
Filter: severity=CRITICAL, status=OPEN
Sort by: -created_at
```

### Task 5: Bulk Operations

**Example: Deactivate Old Equipment**

1. List Equipment:
   - Admin → Assets → Equipment
   - Filter: is_active=True

2. Identify Old Equipment:
   - Sort by created_at
   - Review year and condition

3. Bulk Deactivate:
   - Select equipment to deactivate
   - Choose "Deactivate Equipment" action
   - Click "Go"
   - Confirm

**Example: Batch Approve Work Orders**

1. Filter Work Orders:
   - Filter: approval_status=PENDING_APPROVAL, customer={specific customer}

2. Review for Approval:
   - Check titles and descriptions
   - Verify priorities

3. Bulk Approve:
   - Select all appropriate work orders
   - Choose "Approve Work Orders" action
   - Click "Go"

### Task 6: Data Cleanup

**Find Orphaned Records:**

1. Equipment without customer:
   ```
   Filter: customer=None
   ```

2. Defects without work orders (old, should have been addressed):
   ```
   Filter: status=OPEN, created_at < 30 days ago
   ```

3. Draft inspections (incomplete):
   ```
   Filter: status=DRAFT, created_at < 7 days ago
   ```

**Cleanup Actions:**
- Deactivate old draft inspections
- Link orphaned equipment to correct customer
- Generate work orders for old open defects or mark as non-actionable

---

## Troubleshooting

### Common Issues

**Issue 1: Cannot Edit Finalized Inspection**
```
Error: Cannot modify step_data after inspection is finalized
```
**Solution:** Inspections are immutable once finalized_at is set. This is by design for audit compliance. If changes are needed, create a new inspection or add notes explaining the issue.

**Issue 2: Work Order Not Updating Asset Meters**
```
Warning: Asset meters not updating after work order completion
```
**Causes:**
1. Meter readings not provided (odometer_at_service, engine_hours_at_service)
2. New readings are lower than current (rollback prevention)
3. Asset type mismatch (trying to update odometer on equipment)

**Solution:** Verify meter readings are provided and higher than current values.

**Issue 3: Duplicate Defects**
```
Error: Defect with this identity already exists
```
**Cause:** Attempting to create defect with existing defect_identity hash.

**Solution:** This is correct behavior - defects are idempotent. Update existing defect instead of creating new one.

**Issue 4: Cannot Approve Work Order**
```
Error: Work order not in PENDING_APPROVAL status
```
**Cause:** Work order already approved or status is wrong.

**Solution:** Check approval_status field. Only PENDING_APPROVAL work orders can be approved.

**Issue 5: JSON Validation Error**
```
Error: Invalid JSON in equipment_data field
```
**Causes:**
1. Missing quotes around keys
2. Trailing commas
3. Invalid escape characters

**Solution:** Use JSON validator (jsonlint.com) to check syntax before saving.

### Performance Tips

**For Large Datasets:**

1. **Use Filters Before Searching:**
   - Apply filters first to reduce dataset size
   - Then use search within filtered results

2. **Limit List View:**
   - Default pagination is 100 items
   - Adjust in Django settings if needed

3. **Use select_related/prefetch_related:**
   - Already optimized in admin
   - Foreign key lookups are efficient

4. **Export Large Datasets:**
   - Use API with pagination
   - Export in chunks rather than all at once

---

## Best Practices

### For System Administrators

1. **Regular Backups:**
   - Daily database backups
   - Export critical data weekly
   - Test restore procedures monthly

2. **Data Integrity:**
   - Monitor orphaned records
   - Review defect→work order linkage
   - Verify meter readings are updating

3. **User Management:**
   - Create staff users with limited permissions
   - Use groups for permission management
   - Regular access audits

4. **Performance Monitoring:**
   - Monitor slow queries in Django debug toolbar
   - Review database indexes
   - Check disk space for JSON field growth

### For Data Entry

1. **Consistent Formatting:**
   - Use standard formats for VIN, serial numbers
   - Consistent unit numbering scheme
   - Standard tag usage across assets

2. **Complete Information:**
   - Fill all required fields
   - Add meaningful notes
   - Upload photos for defects

3. **Regular Reviews:**
   - Review draft inspections weekly
   - Close or update old work orders
   - Verify contact information quarterly

4. **Quality Checks:**
   - Verify customer matches asset
   - Check meter readings are reasonable
   - Validate work order costing

---

**Version:** 2.0 (Phase 5 Complete)
**Last Updated:** 2026-03-12
**See Also:**
- [API Reference](API_REFERENCE.md)
- [User Workflows](USER_WORKFLOWS.md)
- [Performance Optimization](PERFORMANCE_OPTIMIZATION.md)
