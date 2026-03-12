# Asset Configuration Files Guide

## Location
**Main Directory:** `asset_templates_v2_2/`

All asset type configurations, capabilities, and field definitions are stored here.

## Key Configuration Files

### 1. `asset_subtypes.json` (4,242 lines)
**Purpose:** Defines all 132 asset types with their field configurations

**Structure:**
```json
{
  "schema_version": "2.0.0",
  "asset_subtypes": [
    {
      "key": "fleet.straight_truck.service",
      "name": "Service Truck",
      "description": "Truck configured for field service.",
      "parent": "fleet.straight_truck",
      "capability_packs": [],
      "asset_fields": {
        "visible": [
          "name",
          "identifier",
          "description",
          "owned_by_organization",
          "is_active",
          "vin",
          "vin_profile.manufacturer",
          "vin_profile.model",
          "vin_profile.model_year",
          "vin_profile.trim",
          "vin_profile.vehicle_type",
          "vin_profile.body_class",
          "vin_profile.engine_model",
          "vin_profile.engine_manufacturer",
          "vin_profile.engine_cylinders",
          "vin_profile.displacement_l",
          "vin_profile.engine_hp",
          "vin_profile.fuel_type_primary",
          "vin_profile.fuel_type_secondary",
          "vin_profile.drive_type",
          "vin_profile.transmission_style",
          "vin_profile.transmission_speeds",
          "vin_profile.gvwr",
          "vin_profile.axles"
        ],
        "required": [
          "name",
          "identifier",
          "vin",
          "is_active"
        ]
      },
      "defaults": {},
      "tags": [],
      "ui": {}
    }
  ]
}
```

**Asset Categories (132 total subtypes):**
- **Fleet** (37 types): Tractors, trucks, vans, cars, trailers
- **Equipment** (11 types): MEWPs, forklifts, generators, compressors
- **Shop Equipment** (25 types): Lifts, welders, tire equipment, diagnostics
- **Tools** (6 types): Hand tools, power tools, calibrated tools
- **Safety** (8 types): PPE, gas monitors, first aid, lockout/tagout
- **Facilities** (27 types): Wash systems, body shops, fire safety, HVAC, fuel storage
- **Real Estate** (4 types): Parcels, buildings, suites, yards
- **IT** (9 types): Computers, tablets, printers, network gear
- **Containers** (5 types): Tanks, totes, drums, dumpsters

### 2. `capability_definitions.json` (2,209 lines)
**Purpose:** Defines dynamic capabilities that can be assigned to assets

**Examples:**
```json
{
  "key": "insulating",
  "name": "Insulating",
  "capability_type": "bool",
  "description": "Whether equipment is insulated for electrical work"
}

{
  "key": "lift_capacity",
  "name": "Lift Capacity",
  "capability_type": "int",
  "description": "Maximum lift capacity in pounds"
}

{
  "key": "electrical_category",
  "name": "Electrical Category",
  "capability_type": "enum",
  "enum_options": ["A", "B", "C"],
  "description": "Electrical work category"
}
```

**Capability Types:**
- `bool` - True/False (e.g., insulating)
- `int` - Integer (e.g., lift_capacity)
- `decimal` - Decimal (e.g., rated_line_voltage_kv)
- `string` - Text (e.g., engine_serial_number)
- `enum` - Fixed options (e.g., electrical_category)
- `date` - Date (e.g., last_calibration_date)

### 3. `capability_packs.json` (203 lines)
**Purpose:** Groups capabilities into reusable packs for asset types

**Example:**
```json
{
  "aerial_device.insulating": [
    "insulating",
    "electrical_category",
    "rated_line_voltage_kv",
    "barehand",
    "upper_controls_high_resistance",
    "supports_ac",
    "supports_dc"
  ],
  "equipment.forklift": [
    "lift_capacity",
    "fuel_type",
    "tire_type"
  ]
}
```

### 4. `asset_field_definitions.json` (87 lines)
**Purpose:** Defines available field types and their properties

**Field Types:**
- **Core Fields:** name, identifier, description, serial_number, vin, is_active
- **Ownership:** owned_by_organization, owned_by_tenant, leased_by_organization
- **VIN Profile Fields:** vin_profile.manufacturer, vin_profile.model, etc.
- **Capability Fields:** capability.insulating, capability.lift_capacity, etc.

## Field Configuration Patterns

### Pattern 1: Vehicles (Fleet Assets)
**24 fields total:**
```
Core: name, identifier, description, owned_by_organization, is_active, vin
VIN Profile: 18 vehicle-specific fields (engine, drivetrain, weight rating)
```

**Example:** Service Truck, Pickup, Van, Tractor, Trailer

### Pattern 2: Powered Equipment
**9 fields total:**
```
Core: name, identifier, description, owned_by_organization, is_active
Equipment: serial_number, manufacturer, model, model_year
```

**Example:** Forklift, Generator, Compressor, MEWP

### Pattern 3: Shop Equipment
**9 fields total:**
```
Same as powered equipment
```

**Example:** Vehicle Lift, Welder, Tire Changer

### Pattern 4: Tools
**6 fields total (minimal):**
```
Core: name, identifier, serial_number, manufacturer, model, is_active
```

**Example:** Hand Tools, Power Tools, Torque Wrench

### Pattern 5: Facilities/Real Estate
**5 fields total (minimal):**
```
Core: name, identifier, description, owned_by_organization, is_active
```

**Example:** Land Parcel, Building, HVAC System

## How to Edit Field Configurations

### Step 1: Edit the JSON file
```bash
cd asset_templates_v2_2/
# Edit asset_subtypes.json
```

### Step 2: Find your asset type
Search for the `key` you want to modify, e.g., `"fleet.straight_truck.service"`

### Step 3: Modify the `asset_fields` section
Add or remove fields from `visible` and `required` arrays:

```json
"asset_fields": {
  "visible": [
    "name",
    "identifier",
    // Add your new field here
    "some_new_field"
  ],
  "required": [
    "name",
    "identifier"
    // Add required fields here
  ]
}
```

### Step 4: Re-import the configuration
```bash
python manage.py import_asset_subtypes_v2 asset_templates_v2_2/asset_subtypes.json --tenant=acme --update
```

## Available Field Names

### Core Asset Fields (on Asset model)
- `name` - Asset name (always required)
- `identifier` - Unit number/asset ID
- `description` - Additional notes
- `serial_number` - Manufacturer serial
- `vin` - Vehicle Identification Number (17 chars)
- `is_active` - Active status
- `owned_by_organization` - Customer who owns it
- `owned_by_tenant` - Tenant owner
- `leased_by_organization` - Customer who leases it
- `serviced_by_tenant` - Service provider

### VIN Profile Fields (on VINDecodeProfile model)
**Prefix with `vin_profile.`**

**Identification:**
- `vin_profile.manufacturer`
- `vin_profile.model`
- `vin_profile.model_year`
- `vin_profile.trim`
- `vin_profile.series`

**Vehicle Type:**
- `vin_profile.vehicle_type`
- `vin_profile.body_class`

**Engine & Powertrain:**
- `vin_profile.engine_model`
- `vin_profile.engine_manufacturer`
- `vin_profile.engine_cylinders`
- `vin_profile.displacement_l`
- `vin_profile.displacement_cc`
- `vin_profile.displacement_ci`
- `vin_profile.engine_hp`
- `vin_profile.engine_kw`
- `vin_profile.fuel_type_primary`
- `vin_profile.fuel_type_secondary`

**Drivetrain:**
- `vin_profile.drive_type`
- `vin_profile.transmission_style`
- `vin_profile.transmission_speeds`

**Weight & Dimensions:**
- `vin_profile.gvwr`
- `vin_profile.gvwr_from`
- `vin_profile.gvwr_to`
- `vin_profile.curb_weight_lb`
- `vin_profile.axles`
- `vin_profile.axle_configuration`

**Trailer-Specific:**
- `vin_profile.trailer_type`
- `vin_profile.trailer_body_type`
- `vin_profile.trailer_length`

**Electric/Hybrid:**
- `vin_profile.battery_kwh`
- `vin_profile.battery_type`
- `vin_profile.battery_voltage`
- `vin_profile.charger_level`
- `vin_profile.charger_power_kw`

### Capability Fields (dynamic per asset type)
**Prefix with `capability.`**

Examples:
- `capability.insulating` (bool)
- `capability.electrical_category` (enum: A, B, C)
- `capability.rated_line_voltage_kv` (decimal)
- `capability.lift_capacity` (int)
- `capability.fuel_type` (enum)

## Tips for Repair Facility

✅ **DO Include:**
- All engine specifications (for parts ordering)
- Serial numbers (for warranty/recalls)
- Manufacturer/model/year (for compatibility)
- Customer ownership (for billing)
- Weight ratings (for DOT compliance)

❌ **DON'T Include:**
- Manufacturing plant locations
- Airbag specifications
- Interior dimensions (doors, seats)
- Body style details (unless operationally relevant)

## Import Commands

**Import asset subtypes:**
```bash
python manage.py import_asset_subtypes_v2 asset_templates_v2_2/asset_subtypes.json --tenant=acme
```

**Update existing (preserves custom changes):**
```bash
python manage.py import_asset_subtypes_v2 asset_templates_v2_2/asset_subtypes.json --tenant=acme --update
```

**Import capabilities:**
```bash
python manage.py import_capability_definitions asset_templates_v2_2/capability_definitions.json
```

**View asset tree:**
```bash
python manage.py show_asset_tree --tenant=acme
```
