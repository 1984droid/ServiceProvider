# Schema Quick Reference - UPDATED

Visual guide to all models, fields, and relationships.

---

## Customer

**Purpose:** Business entity that owns assets

```
┌─────────────────────────────────────┐
│ Customer                            │
├─────────────────────────────────────┤
│ PK  id                 UUID         │
│ FK  primary_contact_id UUID    ────┐│ NEW: Points to primary Contact
│     name               string      ││ Required, indexed
│     legal_name         string       │
│     is_active          boolean      │ Default: True, indexed
│     address_line1      string       │
│     address_line2      string       │
│     city               string       │
│     state              string(2)    │
│     postal_code        string       │
│     country            string(2)    │ Default: 'US'
│     usdot_number       string       │ Unique, indexed
│     mc_number          string       │ Unique, indexed
│     notes              text         │
│     created_at         datetime     │
│     updated_at         datetime     │
└─────────────────────────────────────┘
         │                            │
         │ Has many (1:N)             │ Points to (N:1)
         ├──→ Contact                 └──→ Contact (primary)
         ├──→ Vehicle
         ├──→ Equipment
         ├──→ USDOTProfile (1:1)
         └──→ InspectionRun
```

**No contact info on Customer - use Contact model!**

---

## USDOTProfile (NEW)

**Purpose:** FMCSA lookup data (1:1 with Customer)

```
┌─────────────────────────────────────┐
│ USDOTProfile                        │
├─────────────────────────────────────┤
│ PK  id                 UUID         │
│ FK  customer_id        UUID    ────┐│ OneToOne
│     usdot_number       string      ││ Indexed
│     mc_number          string       │
│     legal_name         string       │
│     dba_name           string       │
│     entity_type        string       │
│     physical_address   string       │
│     physical_city      string       │
│     physical_state     string(2)    │
│     physical_zip       string       │
│     mailing_address    string       │
│     mailing_city       string       │
│     mailing_state      string(2)    │
│     mailing_zip        string       │
│     phone              string       │
│     email              email        │
│     carrier_operation  string       │
│     cargo_carried      text         │
│     operation_classification JSON   │
│     safety_rating      string       │
│     out_of_service_date date        │
│     total_power_units  integer      │
│     total_drivers      integer      │
│     raw_fmcsa_data     JSON         │
│     lookup_date        datetime     │ Auto-updated
│     created_at         datetime     │
│     updated_at         datetime     │
└─────────────────────────────────────┘
                                      │
                    ┌─────────────────┘
                    │ Belongs to (1:1)
                    ↓
              ┌──────────┐
              │ Customer │
              └──────────┘
```

**Workflow:**
1. User enters USDOT# → Lookup FMCSA
2. Create USDOTProfile with raw data
3. User reviews → Creates Customer (copies data, can override)

**CASCADE DELETE: Deleting customer deletes profile**

---

## Contact

**Purpose:** Person at customer with communication preferences

```
┌─────────────────────────────────────┐
│ Contact                             │
├─────────────────────────────────────┤
│ PK  id                 UUID         │
│ FK  customer_id        UUID    ────┐│
│     first_name         string      ││ Required
│     last_name          string      ││ Required
│     title              string       │
│     email              email        │ Indexed
│     phone              string       │
│     phone_extension    string       │
│     mobile             string       │
│     is_active          boolean      │ Default: True, indexed
│     is_automated       boolean      │ NEW: Default: False, indexed
│     receive_invoices             boolean │ Default: False
│     receive_estimates            boolean │ Default: False
│     receive_service_updates      boolean │ Default: False
│     receive_inspection_reports   boolean │ Default: False
│     notes              text         │
│     created_at         datetime     │
│     updated_at         datetime     │
└─────────────────────────────────────┘
         │                            ↑
         │ Belongs to (N:1)           │
         ↓                            │
   ┌──────────┐                       │
   │ Customer │ ──────────────────────┘
   └──────────┘   Can be primary (Customer.primary_contact_id)

   @property is_primary → bool (computed from customer.primary_contact_id)
```

**CASCADE DELETE: Deleting customer deletes contacts**
**is_primary REMOVED** - Now FK at Customer level
**is_automated ADDED** - For API endpoints, webhooks, automated systems

---

## Vehicle

**Purpose:** VIN-based asset (trucks, trailers, vans)

```
┌─────────────────────────────────────┐
│ Vehicle                             │
├─────────────────────────────────────┤
│ PK  id                 UUID         │
│ FK  customer_id        UUID    ────┐│
│     vin                string(17)  ││ UNIQUE, Required, indexed
│     unit_number        string      ││ Indexed
│     year               integer      │
│     make               string       │ Indexed
│     model              string       │
│     vehicle_type       string       │
│     is_active          boolean      │ Default: True, indexed
│     odometer_miles     integer      │ Nullable, >= 0
│     engine_hours       integer      │ Nullable, >= 0
│     vin_decode_data    JSON         │ NHTSA data
│     vin_decode_date    datetime     │
│     tags               JSON         │ NEW: Array ['INSULATED_BOOM', 'DIELECTRIC']
│     notes              text         │
│     created_at         datetime     │
│     updated_at         datetime     │
└─────────────────────────────────────┘
                                      │
                    ┌─────────────────┘
                    │ Belongs to (N:1)
                    ↓
              ┌──────────┐
              │ Customer │
              └──────────┘
                    ↑
                    │ Has many (1:N)
                    └─────────────────┐
                                      │
┌─────────────────────────────────────┐
│ Equipment (mounted)                 │
│   mounted_on_vehicle_id → Vehicle   │
└─────────────────────────────────────┘
```

**PROTECT DELETE: Cannot delete customer with vehicles**
**VIN must be exactly 17 characters**
**Tags: e.g., ['INSULATED_BOOM', 'DIELECTRIC', 'BOOM_TRUCK']**

---

## Equipment

**Purpose:** Serial number-based asset (aerial devices, cranes, generators)

```
┌─────────────────────────────────────┐
│ Equipment                           │
├─────────────────────────────────────┤
│ PK  id                 UUID         │
│ FK  customer_id        UUID    ────┐│
│ FK  mounted_on_vehicle_id UUID ────┼┐ Nullable
│     serial_number      string      ││ UNIQUE, Required, indexed
│     asset_number       string      ││ Indexed
│     equipment_type     string      ││ Indexed
│     manufacturer       string       │
│     model              string       │
│     year               integer      │
│     is_active          boolean      │ Default: True, indexed
│     engine_hours       integer      │ Nullable, >= 0
│     cycles             integer      │ Nullable, >= 0
│     mount_date         date         │ Nullable
│     tags               JSON         │ NEW: Array ['AERIAL_DEVICE', 'DIELECTRIC']
│     equipment_data     JSON         │ NEW: Placard info, capabilities, etc.
│     notes              text         │
│     created_at         datetime     │
│     updated_at         datetime     │
└─────────────────────────────────────┘
                                      ││
                    ┌─────────────────┘│
                    │ Belongs to (N:1)  │
                    ↓                   │
              ┌──────────┐              │
              │ Customer │              │
              └──────────┘              │
                                        │
                           ┌────────────┘
                           │ Mounted on (N:1, optional)
                           ↓
                      ┌─────────┐
                      │ Vehicle │
                      └─────────┘
```

**PROTECT DELETE: Cannot delete customer with equipment**
**SET NULL: Deleting vehicle clears mounted_on_vehicle_id**

**Tags Examples:**
```json
["AERIAL_DEVICE", "INSULATED_BOOM", "DIELECTRIC"]
["CRANE", "MOBILE_CRANE", "HYDRAULIC"]
["GENERATOR", "DIESEL"]
```

**Equipment Data Structure:**
```json
{
  "placard": {
    "rated_capacity": 500,
    "rated_capacity_unit": "lbs",
    "max_working_height": 45,
    "max_working_height_unit": "ft"
  },
  "dielectric": {
    "insulation_class": "Class A",
    "rated_voltage": 46000,
    "test_voltage": 69000
  },
  "capabilities": {
    "has_insulated_boom": true,
    "rotation_degrees": 360
  },
  "last_updated": "2025-01-15T10:30:00Z"
}
```

---

**See DATA_CONTRACT.md for InspectionRun, InspectionDefect, WorkOrder models**
**See MODEL_CHANGES_SUMMARY.md for detailed change explanations**
**See INSPECTION_EQUIPMENT_FLOW.md for tag-driven equipment data entry**

---

**This is your cheat sheet for the core models. Print it. Reference it.**
