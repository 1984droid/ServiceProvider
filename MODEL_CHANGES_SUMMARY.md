# Model Changes Summary

## Changes Based on Your Feedback

### 1. Customer Model

**ADDED:**
- `primary_contact` FK → Contact (replaces `Contact.is_primary` boolean)

**REASON:** Cleaner to have FK at Customer level than boolean at Contact level. One source of truth.

**Relationship:**
```
Customer.primary_contact_id → Contact.id (SET NULL)
```

---

### 2. USDOTProfile Model (NEW)

**PURPOSE:** Store FMCSA lookup data separately from verified Customer data.

**WORKFLOW:**
1. User enters USDOT number or VIN
2. System looks up FMCSA data
3. Populate `USDOTProfile` with raw data
4. User reviews and creates `Customer` (copies data from profile, can override)

**KEY FIELDS:**
- `customer` (OneToOne FK)
- `usdot_number`, `mc_number`
- `legal_name`, `dba_name`, `entity_type`
- `physical_address`, `mailing_address`
- `phone`, `email`
- `carrier_operation`, `cargo_carried`
- `safety_rating`, `total_power_units`, `total_drivers`
- `raw_fmcsa_data` (complete JSON response)

**WHY SEPARATE MODEL:**
- Lookup data is unverified
- Customer data is verified/overridden by user
- Allows re-lookup without affecting customer record
- Clean separation of concerns

---

### 3. Contact Model

**ADDED:**
- `is_automated` (boolean, default=False) - For API endpoints, webhooks, automated systems

**REMOVED:**
- `is_primary` (boolean) - Now handled by Customer.primary_contact_id FK

**ADDED PROPERTY:**
- `is_primary` (computed property) - Returns `self.customer.primary_contact_id == self.id`

**REASON:** Cleaner design - primary contact is a Customer-level concern, not Contact-level.

---

### 4. Vehicle Model

**ADDED:**
- `tags` (JSONField, default=[]) - For inspection applicability

**EXAMPLES:**
```python
tags = ['INSULATED_BOOM', 'DIELECTRIC', 'BOOM_TRUCK']
```

**USE CASES:**
- Determine which inspection modules apply
- Filter vehicles for specific inspections
- Tag-based forms during inspection setup

---

### 5. Equipment Model

**ADDED:**
- `tags` (JSONField, default=[]) - For inspection applicability
- `equipment_data` (JSONField, default={}) - Store placard info, capabilities, etc.

**TAGS EXAMPLES:**
```python
tags = ['AERIAL_DEVICE', 'INSULATED_BOOM', 'DIELECTRIC']
tags = ['CRANE', 'MOBILE_CRANE', 'HYDRAULIC']
tags = ['GENERATOR', 'DIESEL']
```

**EQUIPMENT_DATA STRUCTURE:**
```json
{
  "placard": {
    "rated_capacity": 500,
    "rated_capacity_unit": "lbs",
    "max_working_height": 45,
    "max_working_height_unit": "ft",
    "max_horizontal_reach": 35
  },
  "dielectric": {
    "insulation_class": "Class A",
    "rated_voltage": 46000,
    "test_voltage": 69000
  },
  "capabilities": {
    "has_insulated_boom": true,
    "has_platform_leveling": true,
    "rotation_degrees": 360
  },
  "last_updated": "2025-01-15T10:30:00Z"
}
```

**WORKFLOW:**
1. Equipment created with basic info (SN, type, manufacturer) + tags
2. When starting inspection, check tags
3. If tags require data (e.g., `DIELECTRIC` → need voltage ratings), show form
4. User fills form → data saved to `equipment_data`
5. Inspection uses data from `equipment_data`

**WHY JSON FIELD:**
- No schema changes for new equipment types
- Flexible structure per equipment type
- Easy to extend (add new data without migrations)
- Keeps Equipment model clean (no 50 nullable fields)

---

## Updated Relationships

### Customer Relationships

```
Customer
├─→ primary_contact (FK → Contact, SET NULL)
├─→ usdot_profile (1:1 → USDOTProfile, CASCADE)
├─→ contacts (1:N)
├─→ vehicles (1:N)
├─→ equipment (1:N)
└─→ inspections (1:N)
```

### Contact

**No more `is_primary` boolean!**

Check if contact is primary:
```python
contact.is_primary  # Property, returns boolean
# OR
customer.primary_contact == contact
```

### Equipment

```
Equipment
├─→ customer (FK)
├─→ mounted_on_vehicle (FK, nullable)
├─→ tags (JSON array)
└─→ equipment_data (JSON object)
```

---

## Inspection Flow Changes

### OLD (Too Eager):
```
1. InspectionRun assumes all data exists
2. User enters inspection data
3. Hope equipment details are already there
```

### NEW (On-Demand):
```
1. Customer, Contact, Vehicle, Equipment exist (basics only)
2. User starts inspection
3. System checks equipment.tags
4. If tags require data (placard, dielectric, etc.) → show forms
5. User fills forms → saved to equipment.equipment_data
6. NOW inspection can run with all required data
```

---

## Tag-Driven Forms

### Mapping: Tag → Required Form

| Equipment Tag | Required Form | Data Stored In |
|---------------|---------------|----------------|
| `AERIAL_DEVICE` | Placard form | `equipment_data.placard` |
| `DIELECTRIC` or `INSULATED_BOOM` | Dielectric form | `equipment_data.dielectric` |
| `CRANE` | Load chart form | `equipment_data.crane` |
| `GENERATOR` | Nameplate form | `equipment_data.generator` |
| `COMPRESSOR` | Pressure form | `equipment_data.compressor` |

### Example: Aerial Device with Dielectric

**Equipment Tags:**
```python
['AERIAL_DEVICE', 'INSULATED_BOOM', 'DIELECTRIC']
```

**Required Forms:**
1. Placard form (rated capacity, working height, reach)
2. Dielectric form (insulation class, voltage ratings)

**Data Stored:**
```json
{
  "placard": {...},
  "dielectric": {...}
}
```

**Inspection Modules Applied:**
- ANSI A92.2 Periodic Inspection
- ANSI A92.2 Dielectric Test Module

---

## API Changes

### Customer

**NEW FIELD:**
```json
{
  "primary_contact_id": "uuid-here",
  "primary_contact": {
    "id": "uuid",
    "full_name": "John Doe",
    "email": "john@example.com"
  }
}
```

### USDOTProfile (NEW)

**Endpoints:**
```
POST   /api/usdot-lookup/          Lookup USDOT, create profile
GET    /api/usdot-profiles/{id}/   Get profile
PATCH  /api/usdot-profiles/{id}/   Update profile
DELETE /api/usdot-profiles/{id}/   Delete profile
```

**Lookup Workflow:**
```
POST /api/usdot-lookup/
{
  "usdot_number": "123456"
}

→ Fetches FMCSA data
→ Creates USDOTProfile
→ Returns profile data

User reviews → clicks "Create Customer"
→ Copies data from USDOTProfile to new Customer
→ User can override any field
```

### Contact

**REMOVED FIELD:**
- `is_primary` (boolean)

**ADDED FIELD:**
```json
{
  "is_automated": false
}
```

**ADDED COMPUTED FIELD:**
```json
{
  "is_primary": true  // Computed from customer.primary_contact_id
}
```

### Vehicle

**NEW FIELD:**
```json
{
  "tags": ["INSULATED_BOOM", "DIELECTRIC"]
}
```

### Equipment

**NEW FIELDS:**
```json
{
  "tags": ["AERIAL_DEVICE", "INSULATED_BOOM", "DIELECTRIC"],
  "equipment_data": {
    "placard": {...},
    "dielectric": {...},
    "capabilities": {...}
  }
}
```

**NEW ENDPOINTS:**
```
GET    /api/equipment/{id}/inspection-readiness/
PATCH  /api/equipment/{id}/data/
POST   /api/equipment/{id}/add-tag/
DELETE /api/equipment/{id}/remove-tag/
```

---

## Migration Path

### From Old Build to New

**Customer:**
- Add `primary_contact_id` FK (nullable initially)
- Migrate: Set primary_contact_id from Contact.is_primary=True
- Make non-nullable after migration

**Contact:**
- Remove `is_primary` boolean field
- Add `is_automated` boolean field
- Remove index on `is_primary`

**Vehicle:**
- Add `tags` JSONField (default=[])

**Equipment:**
- Add `tags` JSONField (default=[])
- Add `equipment_data` JSONField (default={})

**USDOTProfile:**
- Create new model
- No migration needed (new table)

---

## Benefits of Changes

### 1. Primary Contact at Customer Level
✅ One source of truth
✅ No race conditions (multiple is_primary=True)
✅ Cleaner queries: `customer.primary_contact`
✅ Still has property on Contact for convenience

### 2. USDOTProfile Separation
✅ Lookup data separate from verified data
✅ Can re-lookup without affecting customer
✅ User explicitly reviews and creates customer
✅ Preserves raw FMCSA response

### 3. Contact.is_automated
✅ Identify API endpoints, webhooks, automated systems
✅ Filter human contacts vs. automated
✅ Different correspondence handling

### 4. Tags on Vehicle/Equipment
✅ Flexible categorization
✅ Drives inspection module selection
✅ No schema changes for new tags
✅ Easy filtering and search

### 5. Equipment.equipment_data
✅ No 50 nullable fields on Equipment model
✅ Flexible structure per equipment type
✅ Easy to extend without migrations
✅ Collected on-demand during inspection setup

---

## Database Schema Summary

### Tables

1. **customers** (updated)
   - Added: `primary_contact_id` FK

2. **usdot_profiles** (NEW)
   - OneToOne with customers

3. **contacts** (updated)
   - Removed: `is_primary` boolean
   - Added: `is_automated` boolean

4. **vehicles** (updated)
   - Added: `tags` JSONField

5. **equipment** (updated)
   - Added: `tags` JSONField
   - Added: `equipment_data` JSONField

### Indexes Added

- `customers.primary_contact_id`
- `usdot_profiles.usdot_number`
- `usdot_profiles.mc_number`
- `contacts.is_automated`

---

## Next Steps

1. ✅ Models updated
2. ✅ Documentation created
3. ⚠️ Need migrations (after copying to new location)
4. ⚠️ Need admin.py updates for new fields
5. ⚠️ Need API serializers for new fields
6. ⚠️ Need frontend forms for equipment data entry

---

**All changes preserve existing functionality while adding flexibility for equipment-specific data and cleaner relationships.**
