# Asset Field Strategy - Repair Facility Focus

## Field Categories

### 1. CORE FIELDS (All Assets)
**Always visible, most required:**
- `name` - Asset name (required)
- `identifier` - Unit number/asset ID (required for tracking)
- `description` - Notes/additional info
- `serial_number` - Manufacturer serial (equipment/tools)
- `is_active` - Active status (required)
- `owned_by_organization` - Customer who owns it (for customer assets)

### 2. VEHICLE FIELDS (Fleet Assets)
**From VIN Profile - Repair-Relevant Only:**

**Identification:**
- `vin` - Vehicle Identification Number
- `manufacturer` / `make`
- `model`
- `model_year`
- `trim`

**Engine & Powertrain (CRITICAL FOR REPAIR):**
- `engine_model` - Full engine designation
- `engine_manufacturer` - Engine brand
- `engine_cylinders` - Number of cylinders
- `displacement_l` - Engine size in liters
- `engine_hp` - Horsepower
- `fuel_type_primary` - Gasoline, Diesel, Electric, etc.
- `fuel_type_secondary` - For hybrids

**Drivetrain (NEEDED FOR PARTS/SERVICE):**
- `drive_type` - 4WD, AWD, FWD, RWD
- `transmission_style` - Automatic, Manual, CVT
- `transmission_speeds` - Number of gears

**Vehicle Type (FOR COMPLIANCE/ROUTING):**
- `vehicle_type` - Truck, Passenger, Trailer
- `body_class` - Pickup, Van, Truck-Tractor, etc.
- `gvwr` - Weight rating (DOT compliance)
- `axles` - Number of axles
- `axle_configuration` - Axle setup

**DO NOT SHOW (Not repair-relevant):**
- plant_city, plant_state, plant_country (manufacturing location)
- airbag locations (safety features - not serviceable)
- wheel_base, track_width, bed_length (dimensions)
- doors, seats (interior - not repair focus)
- trailer-specific fields (unless it's a trailer)

### 3. EQUIPMENT FIELDS (MEWP, Forklifts, Generators)
**Capabilities (dynamic based on equipment type):**
- `manufacturer`
- `model`
- `model_year`
- `serial_number` - Primary identifier for equipment
- `engine_model` - If powered equipment
- `fuel_type` - Gas, Diesel, Electric, Propane
- Plus type-specific capabilities:
  - **Aerial Devices**: `insulating`, `electrical_category`, `rated_line_voltage_kv`
  - **Forklifts**: `lift_capacity`, `fuel_type`, `tire_type`
  - **Generators**: `output_kw`, `voltage`, `phase`

### 4. TOOLS & CALIBRATED TOOLS
**Minimal fields:**
- `name`
- `identifier` / `tool_number`
- `manufacturer`
- `model`
- `serial_number`
- **Calibrated Tools Add:**
  - `calibration_due_date`
  - `calibration_interval_days`
  - `last_calibration_date`

### 5. FACILITIES & REAL ESTATE
**Minimal fields:**
- `name`
- `identifier` / `location_code`
- `description`
- `owned_by_organization` (property owner)

## Proposed asset_fields Configuration

### Service Truck Example:
```json
{
  "visible": [
    "name",
    "identifier",
    "description",
    "vin",
    "owned_by_organization",
    "is_active",
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
    "vin_profile.axles",
    "vin_profile.axle_configuration"
  ],
  "required": [
    "name",
    "identifier",
    "vin",
    "is_active"
  ]
}
```

### Forklift Example:
```json
{
  "visible": [
    "name",
    "identifier",
    "description",
    "serial_number",
    "manufacturer",
    "model",
    "model_year",
    "owned_by_organization",
    "is_active",
    "capability.lift_capacity",
    "capability.fuel_type",
    "capability.tire_type"
  ],
  "required": [
    "name",
    "identifier",
    "serial_number",
    "is_active"
  ]
}
```

### Aerial Device Example:
```json
{
  "visible": [
    "name",
    "identifier",
    "description",
    "vin",
    "owned_by_organization",
    "is_active",
    "vin_profile.manufacturer",
    "vin_profile.model",
    "vin_profile.model_year",
    "vin_profile.engine_model",
    "vin_profile.fuel_type_primary",
    "capability.insulating",
    "capability.electrical_category",
    "capability.rated_line_voltage_kv",
    "capability.upper_controls_high_resistance"
  ],
  "required": [
    "name",
    "identifier",
    "is_active",
    "capability.insulating"
  ]
}
```

## Implementation Plan

1. **Update asset_subtypes.json** - Add comprehensive field lists for each type
2. **Update Frontend** - Support nested fields (vin_profile.*, capability.*)
3. **Update API** - Handle nested VIN profile data on asset creation
4. **Add Ownership Field** - Show owned_by_organization dropdown (for customer assets)

## Key Principles

✅ **Repair-Focused**: Only show data useful for maintenance/repair
✅ **Complete Engine Data**: All engine specs for parts ordering
✅ **Customer Tracking**: owned_by_organization for customer assets
✅ **Practical Details**: Serial numbers, model years, fuel types
❌ **No Fluff**: Skip airbag locations, plant info, interior dimensions
