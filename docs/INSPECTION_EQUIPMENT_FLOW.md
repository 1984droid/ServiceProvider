# Inspection & Equipment Data Entry Flow

## Overview

Equipment starts with **basic info only** (serial number, type, manufacturer). During inspection setup, **tag-based forms** appear to collect detailed placard/capability data.

---

## The Problem with InspectionRun

You're right - `InspectionRun` assumes too much. We need a cleaner flow:

1. Customer, Contact, Vehicle, Equipment are **already in the system** (basics only)
2. When starting an inspection, check equipment **tags**
3. Based on tags, show **equipment data entry forms** (placard info, capabilities)
4. Store that data in `Equipment.equipment_data` JSON field
5. **Then** run the inspection using that data

---

## Equipment Data Model

### Basic Equipment (Always Required)
```
Equipment
├── serial_number       Required, unique
├── asset_number        Optional (customer's #)
├── equipment_type      "Aerial Device", "Crane", etc.
├── manufacturer        "Altec", "Terex", etc.
├── model               "AT37G", "Hi-Ranger"
├── year                Manufacturing year
└── tags                ['AERIAL_DEVICE', 'INSULATED_BOOM', 'DIELECTRIC']
```

### Equipment-Specific Data (Populated During Inspection Setup)

**Stored in `Equipment.equipment_data` JSON:**

```json
{
  "placard": {
    "rated_capacity": 500,
    "rated_capacity_unit": "lbs",
    "platform_capacity": 350,
    "platform_capacity_unit": "lbs",
    "max_working_height": 45,
    "max_working_height_unit": "ft",
    "max_horizontal_reach": 35,
    "max_horizontal_reach_unit": "ft"
  },
  "dielectric": {
    "insulation_class": "Class A",
    "rated_voltage": 46000,
    "rated_voltage_unit": "V",
    "test_voltage": 69000,
    "test_voltage_unit": "V"
  },
  "capabilities": {
    "has_insulated_boom": true,
    "has_bare_hand_work_unit": false,
    "has_platform_leveling": true,
    "has_rotation": true,
    "rotation_degrees": 360
  },
  "last_updated": "2025-01-15T10:30:00Z",
  "updated_by": "user_id_here"
}
```

---

## Tag-Based Form Flow

### Step 1: Equipment Created (Basic Info Only)

```
Equipment: Altec AT37G
├── Serial Number: 123456ABC
├── Equipment Type: Aerial Device
├── Tags: ['AERIAL_DEVICE', 'INSULATED_BOOM', 'DIELECTRIC']
└── equipment_data: {} (empty)
```

### Step 2: User Starts Inspection

**UI Flow:**
1. User selects Customer → Vehicle → Equipment
2. System checks `Equipment.tags`
3. If tags present, show **"Equipment Details Required"** modal

**Tag Detection Logic:**
```python
equipment = Equipment.objects.get(id=equipment_id)

if 'AERIAL_DEVICE' in equipment.tags:
    show_form('placard_form')  # Rated capacity, working height, etc.

if 'DIELECTRIC' in equipment.tags or 'INSULATED_BOOM' in equipment.tags:
    show_form('dielectric_form')  # Insulation class, rated voltage, etc.

if 'CRANE' in equipment.tags:
    show_form('crane_form')  # Load chart, boom length, etc.
```

### Step 3: User Fills Equipment Data Forms

**Example: Aerial Device with Dielectric**

**Placard Form:**
```
Rated Platform Capacity: [500] lbs
Max Working Height: [45] ft
Max Horizontal Reach: [35] ft
```

**Dielectric Form:**
```
Insulation Class: [Class A ▼]
Rated Voltage: [46000] V
Test Voltage: [69000] V
```

**On Submit:**
```python
equipment.equipment_data = {
    "placard": {...},
    "dielectric": {...},
    "last_updated": timezone.now(),
    "updated_by": request.user.id
}
equipment.save()
```

### Step 4: Inspection Runs

Now the inspection engine has all the data it needs:
- Basic equipment info from model fields
- Detailed capability data from `equipment_data` JSON
- Tags determine which inspection modules apply

---

## Tag → Form → Inspection Mapping

### Common Tags

| Tag | Form Required | Inspection Modules |
|-----|---------------|-------------------|
| `AERIAL_DEVICE` | Placard form | ANSI A92.2 Periodic |
| `INSULATED_BOOM` | Dielectric form | Dielectric Test Module |
| `DIELECTRIC` | Dielectric form | Dielectric Test Module |
| `CRANE` | Load chart form | ASME B30.5 Crane Inspection |
| `GENERATOR` | Nameplate form | Generator Load Test |
| `COMPRESSOR` | Pressure form | Air System Inspection |

### Example: Tag-Driven Module Selection

```python
def get_applicable_modules(equipment):
    """Determine which inspection modules apply based on tags."""
    modules = []

    if 'AERIAL_DEVICE' in equipment.tags:
        modules.append('ansi_a92_2_periodic')
        modules.append('ansi_a92_2_structural')
        modules.append('ansi_a92_2_hydraulic')

    if 'DIELECTRIC' in equipment.tags or 'INSULATED_BOOM' in equipment.tags:
        # Only if equipment_data has dielectric info
        if equipment.equipment_data.get('dielectric'):
            modules.append('ansi_a92_2_dielectric')

    if 'CRANE' in equipment.tags:
        modules.append('asme_b30_5_crane_periodic')

    return modules
```

---

## Data Validation Rules

### Placard Data Validation

**Required if `AERIAL_DEVICE` tag:**
- `rated_capacity` > 0
- `max_working_height` > 0
- `max_horizontal_reach` > 0 (or null for vertical-only)

### Dielectric Data Validation

**Required if `DIELECTRIC` or `INSULATED_BOOM` tag:**
- `insulation_class` in ['Class A', 'Class B', 'Class C']
- `rated_voltage` > 0
- `test_voltage` >= rated_voltage * 1.5

### Crane Data Validation

**Required if `CRANE` tag:**
- `load_chart` (file or JSON)
- `max_boom_length`
- `max_lift_capacity`

---

## Equipment Data Update Flow

### Scenario: User Adds Dielectric Tag Later

1. **Initial State:**
```json
Equipment: Altec AT37G
tags: ['AERIAL_DEVICE']
equipment_data: {
  "placard": {...}
}
```

2. **User Adds Tag:**
```python
equipment.tags.append('DIELECTRIC')
equipment.save()
```

3. **Next Inspection Start:**
```
System detects: DIELECTRIC tag present but no dielectric data
→ Show "Missing Equipment Data" warning
→ Require dielectric form completion before inspection
```

4. **User Completes Form:**
```python
equipment.equipment_data['dielectric'] = {
  "insulation_class": "Class A",
  "rated_voltage": 46000,
  ...
}
equipment.save()
```

---

## UI/UX Guidelines

### Equipment Detail Page

**Show Data Completeness Badge:**
```
Equipment: Altec AT37G (SN: 123456ABC)
Tags: [AERIAL_DEVICE] [INSULATED_BOOM] [DIELECTRIC]

Equipment Data:
  ✅ Placard Info: Complete
  ✅ Dielectric Info: Complete
  ⚠️ Capabilities: Incomplete

[Edit Equipment Data]
```

### Inspection Start Modal

**If Equipment Data Missing:**
```
┌───────────────────────────────────────┐
│ Equipment Details Required            │
├───────────────────────────────────────┤
│ Before starting this inspection, we   │
│ need placard and dielectric info for: │
│                                       │
│ Equipment: Altec AT37G                │
│ Serial Number: 123456ABC              │
│                                       │
│ This data is required for ANSI A92.2 │
│ compliance and will be saved to the   │
│ equipment record.                     │
│                                       │
│ [Continue to Data Entry]   [Cancel]   │
└───────────────────────────────────────┘
```

### Equipment Data Entry Form

**Progressive Disclosure:**
```
Step 1: Placard Information ✓
Step 2: Dielectric Information ← You are here
Step 3: Capabilities (Optional)

Dielectric Information
━━━━━━━━━━━━━━━━━━━━
Insulation Class: [Class A ▼]
Rated Voltage: [46000] V
Test Voltage: [69000] V

[Back] [Continue]
```

---

## API Endpoints

### Get Equipment with Data Completeness

```
GET /api/equipment/{id}/

Response:
{
  "id": "uuid",
  "serial_number": "123456ABC",
  "tags": ["AERIAL_DEVICE", "INSULATED_BOOM", "DIELECTRIC"],
  "equipment_data": {...},
  "data_completeness": {
    "placard": "complete",
    "dielectric": "complete",
    "capabilities": "incomplete"
  },
  "required_forms": [],
  "can_start_inspection": true
}
```

### Update Equipment Data

```
PATCH /api/equipment/{id}/data/

Request:
{
  "placard": {
    "rated_capacity": 500,
    "max_working_height": 45,
    ...
  }
}

Response:
{
  "success": true,
  "equipment_data": {...},
  "data_completeness": {...}
}
```

### Check Inspection Readiness

```
GET /api/equipment/{id}/inspection-readiness/

Response:
{
  "ready": false,
  "missing_data": ["dielectric"],
  "required_forms": [
    {
      "form_id": "dielectric_form",
      "title": "Dielectric Information",
      "reason": "Required for DIELECTRIC tag"
    }
  ]
}
```

---

## Database Schema Changes

### Equipment Model (Updated)

```python
class Equipment(BaseModel):
    # ... existing fields ...

    # NEW: Tags for inspection applicability
    tags = models.JSONField(
        default=list,
        help_text="['AERIAL_DEVICE', 'INSULATED_BOOM', 'DIELECTRIC']"
    )

    # NEW: Equipment-specific data (populated on-demand)
    equipment_data = models.JSONField(
        default=dict,
        help_text="Placard info, capabilities, dielectric data, etc."
    )
```

**No InspectionRun changes needed** - it just references Equipment and reads the data.

---

## Migration Strategy

### Existing Equipment Records

**For equipment already in system:**
1. Tags are empty initially
2. Admin/user manually adds tags based on equipment type
3. Next inspection prompts for equipment data
4. Data is collected and saved to `equipment_data`

**Bulk Tag Assignment:**
```python
# Management command: assign_equipment_tags
Equipment.objects.filter(
    equipment_type__icontains='aerial'
).update(
    tags=['AERIAL_DEVICE']
)

Equipment.objects.filter(
    equipment_type__icontains='crane'
).update(
    tags=['CRANE']
)
```

---

## Summary

✅ **Equipment starts simple** - just basics (SN, type, manufacturer)
✅ **Tags drive complexity** - add tags as you learn about equipment
✅ **Data entry on-demand** - collect placard/capability data when needed
✅ **Stored in equipment_data** - one JSON field, no schema changes
✅ **Inspection-ready checks** - system validates data completeness
✅ **Flexible & extensible** - easy to add new tags and forms

**This approach keeps the data model clean while supporting complex inspection requirements.**
