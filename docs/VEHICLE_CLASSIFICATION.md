# Vehicle Classification

**Philosophy:** Derive classification from VIN decode. Tags only exist if they affect inspections or maintenance.

**Last Updated:** 2026-03-12

---

## Overview

### The Simple Approach

- **Vehicle = Chassis** (classification from VIN decode)
- **Special Body = Equipment** (refuse body, sweeper, etc.) mounted on vehicle
- **Work Equipment = Equipment** (crane, aerial device, etc.) mounted on vehicle
- **Tags = Only if it affects inspections or maintenance**

**No manual tags on vehicles.** Everything comes from the VIN.

---

## Vehicle Classification (From VIN Decode)

### NHTSA Fields

When you decode a VIN through NHTSA vPIC API, you get:

| Field | What It Tells You | Example Values |
|-------|-------------------|----------------|
| `vehicle_type` | Basic vehicle category | Truck, Trailer, Bus, Passenger Car |
| `body_class` | Body/chassis type | Cab & Chassis, Pickup, Van |
| `gvwr` | Weight class | Class 2-8 (truck classes) |
| `fuel_type_primary` | Fuel type | Diesel, Gasoline, Electric, CNG |
| `abs` | Brake system type | Standard, Hydraulic, Air Brakes |

These are stored in the `VINDecodeData` model (one-to-one with Vehicle).

### Truck Classes (From GVWR)

| GVWR | Class | Examples |
|------|-------|----------|
| 6,001 - 10,000 lbs | Class 2 | F-250, Ram 2500 |
| 10,001 - 14,000 lbs | Class 3 | F-350, Ram 3500 |
| 14,001 - 16,000 lbs | Class 4 | F-450, Isuzu NPR |
| 16,001 - 19,500 lbs | Class 5 | F-550 |
| 19,501 - 26,000 lbs | Class 6 | F-600, Isuzu FTR |
| 26,001 - 33,000 lbs | Class 7 | F-750, Freightliner M2 |
| 33,001+ lbs | Class 8 | Semi-tractors |

### Incomplete Vehicle Flag

When VIN decode returns:
- `vehicle_type = "Incomplete Vehicle"` OR
- `body_class = "Cab & Chassis"`

**This means:** An aftermarket manufacturer added a special body (garbage compactor, street sweeper, school bus body, etc.)

**Action:** Create a separate Equipment record for the body.

---

## Capability Tags - Inspection/Maintenance Driven

**Rule:** Tags only exist if they change what inspections you need to perform or how you maintain the vehicle/equipment.

### Vehicle Capability Tags

**From VIN decode (automatic):**
- Brake system type (affects inspection procedures)
- Fuel type (affects maintenance)
- Drive type (4WD, 6WD - affects drivetrain inspection)

**Manual override only if VIN decode is wrong or incomplete:**

| Tag | Why It Matters | Inspection/Maintenance Impact |
|-----|----------------|-------------------------------|
| `AIR_BRAKES` | Brake system uses air | Air brake inspection required (different from hydraulic) |
| `HYDRAULIC_BRAKES` | Brake system uses hydraulic fluid | Hydraulic brake inspection (standard) |
| `ELECTRIC_BRAKES` | Electric trailer brakes | Electric brake controller inspection |
| `FOUR_WHEEL_DRIVE` | Has 4WD/AWD system | Transfer case, front differential inspection |
| `SIX_WHEEL_DRIVE` | Has 6WD system | Additional drivetrain components |

**That's it for vehicles.** Most of this comes from VIN decode, tags are only backup.

### Equipment Capability Tags

**Only tag if it affects inspection or maintenance:**

| Tag | Why It Matters | Inspection/Maintenance Impact |
|-----|----------------|-------------------------------|
| `DIELECTRIC` | Electrical insulation | Annual dielectric test required (ANSI A92.2) |
| `HYDRAULIC` | Hydraulic system | Hydraulic system inspection, pressure tests |
| `PNEUMATIC` | Air-powered | Air system inspection, pressure tests |
| `ELECTRIC` | Electric powered | Electrical system inspection |
| `PTO_DRIVEN` | Uses vehicle PTO | PTO system inspection |
| `ENGINE_DRIVEN` | Has its own engine | Engine maintenance, oil changes |

---

## Special Bodies (Equipment Records)

When a truck starts as incomplete/cab & chassis and gets a special body:

| Equipment Type | Description | Typical Tags |
|----------------|-------------|--------------|
| `REFUSE_BODY` | Garbage truck body | `HYDRAULIC`, `PTO_DRIVEN` |
| `SWEEPER_BODY` | Street sweeper body | `HYDRAULIC`, `ENGINE_DRIVEN` or `PTO_DRIVEN` |
| `BUS_BODY` | School/shuttle bus body | Usually none (body doesn't need special inspection) |
| `DUMP_BODY` | Dump truck bed | `HYDRAULIC`, `PTO_DRIVEN` |
| `FLATBED_BODY` | Flatbed/stake bed | Usually none |
| `SERVICE_BODY` | Utility body with compartments | Usually none |
| `BOX_BODY` | Enclosed box | Usually none |
| `REFRIGERATED_BODY` | Reefer body | `ENGINE_DRIVEN` or `ELECTRIC` (for refrigeration unit) |
| `TANK_BODY` | Liquid/gas tank | May have `PNEUMATIC` for pumping system |
| `TOW_BODY` | Wrecker/rollback | `HYDRAULIC` |

---

## Work Equipment (Equipment Records)

Equipment mounted ON vehicles (or standalone):

### Aerial Equipment

| Equipment Type | Standard | Typical Tags |
|----------------|----------|--------------|
| `AERIAL_DEVICE` | ANSI A92.2 | `HYDRAULIC`, may have `DIELECTRIC` |
| `DIGGER_DERRICK` | ANSI A10.31 | `HYDRAULIC` |

### Lifting Equipment

| Equipment Type | Standard | Typical Tags |
|----------------|----------|--------------|
| `CRANE` | ASME B30.5 | `HYDRAULIC`, `PTO_DRIVEN` or `ENGINE_DRIVEN` |
| `LIFTGATE` | ANSI MH29.1 | `HYDRAULIC` or `ELECTRIC` |

### Utility Equipment

| Equipment Type | Standard | Typical Tags |
|----------------|----------|--------------|
| `SNOWPLOW` | None | `HYDRAULIC` or `ELECTRIC` |
| `SPREADER` | None | `HYDRAULIC`, `ELECTRIC`, or `ENGINE_DRIVEN` |
| `WINCH` | ASME B30.7 | `HYDRAULIC`, `ELECTRIC`, or `PTO_DRIVEN` |

### Standalone Equipment

| Equipment Type | Standard | Typical Tags |
|----------------|----------|--------------|
| `GENERATOR` | None | `ENGINE_DRIVEN` (has its own engine needing maintenance) |
| `AIR_COMPRESSOR` | None | `ENGINE_DRIVEN` or `ELECTRIC` |
| `WELDER` | None | `ENGINE_DRIVEN` or `ELECTRIC` |
| `PRESSURE_WASHER` | None | `ENGINE_DRIVEN` or `ELECTRIC` |

---

## How Tags Drive Inspections

### Example 1: Brake System

**Vehicle with Air Brakes:**
```json
{
  "vin": "1HTMMAAN5JH123456",
  "vin_decode": {
    "abs": "Air Brakes"
  },
  "capabilities": ["AIR_BRAKES"]
}
```

**Inspection Template Includes:**
- Air brake system inspection (compressor, tanks, lines, valves)
- Air pressure tests
- Drain moisture from air tanks
- Check air dryer

**vs. Hydraulic Brakes:**
```json
{
  "vin": "1FDAF56R67EA12345",
  "vin_decode": {
    "abs": "Hydraulic"
  },
  "capabilities": ["HYDRAULIC_BRAKES"]
}
```

**Inspection Template Includes:**
- Hydraulic brake fluid inspection
- Brake line condition
- Master cylinder
- Wheel cylinders/calipers

**The tag tells the system which brake inspection module to include.**

---

### Example 2: Aerial Device Power System

**Hydraulic Aerial Device:**
```json
{
  "equipment_type": "AERIAL_DEVICE",
  "capabilities": ["HYDRAULIC", "DIELECTRIC"]
}
```

**Inspection Includes:**
- Hydraulic system inspection (pumps, hoses, cylinders, filters)
- Hydraulic pressure tests
- Dielectric testing

**vs. Electric Aerial Device:**
```json
{
  "equipment_type": "AERIAL_DEVICE",
  "capabilities": ["ELECTRIC", "DIELECTRIC"]
}
```

**Inspection Includes:**
- Electrical system inspection (batteries, motors, controllers)
- Electric motor function tests
- Dielectric testing

**The tag tells the system which power system inspection to perform.**

---

### Example 3: Generator Maintenance

**Engine-Driven Generator:**
```json
{
  "equipment_type": "GENERATOR",
  "capabilities": ["ENGINE_DRIVEN"]
}
```

**Maintenance Schedule Includes:**
- Oil changes every 100 hours
- Air filter replacement
- Spark plug replacement (gas) or injector service (diesel)
- Coolant system maintenance

**vs. No Tag (if generator has no engine):**
```json
{
  "equipment_type": "GENERATOR",
  "capabilities": []
}
```

**Maintenance Schedule Includes:**
- Basic electrical inspection only
- No oil changes or engine maintenance

---

## Data Structure Examples

### Example 1: Class 8 Truck with Air Brakes and Hydraulic Crane

**Vehicle (from VIN decode):**
```json
{
  "vin": "1HTMMAAN5JH123456",
  "year": 2019,
  "make": "International",
  "model": "HV607",
  "vin_decode": {
    "vehicle_type": "Truck",
    "body_class": "Cab & Chassis",
    "gvwr": "Class 8: 33,001+ lb",
    "fuel_type_primary": "Diesel",
    "abs": "Air Brakes"
  },
  "capabilities": ["AIR_BRAKES"]
}
```

**Equipment (service body):**
```json
{
  "serial_number": "READING-1234",
  "equipment_type": "SERVICE_BODY",
  "capabilities": []
}
```

**Equipment (crane):**
```json
{
  "serial_number": "IMT-5678",
  "equipment_type": "CRANE",
  "capabilities": ["HYDRAULIC", "PTO_DRIVEN"],
  "equipment_data": {
    "max_capacity_lbs": 17500,
    "max_reach_ft": 26
  }
}
```

**Inspections Triggered:**
- Air brake system inspection (from `AIR_BRAKES` on vehicle)
- ASME B30.5 crane inspection (from `CRANE` equipment type)
- Hydraulic system inspection (from `HYDRAULIC` on crane)
- PTO system inspection (from `PTO_DRIVEN` on crane)

---

### Example 2: Insulated Aerial Bucket Truck

**Vehicle (from VIN decode):**
```json
{
  "vin": "1FDAF56R67EA12345",
  "year": 2020,
  "make": "Ford",
  "model": "F-550",
  "vin_decode": {
    "vehicle_type": "Truck",
    "body_class": "Cab & Chassis",
    "gvwr": "Class 5: 16,001 - 19,500 lb",
    "fuel_type_primary": "Diesel",
    "abs": "Hydraulic"
  },
  "capabilities": ["HYDRAULIC_BRAKES"]
}
```

**Equipment (aerial device):**
```json
{
  "serial_number": "TEREX123456",
  "equipment_type": "AERIAL_DEVICE",
  "capabilities": ["HYDRAULIC", "DIELECTRIC"],
  "equipment_data": {
    "placard": {
      "max_platform_height": 46,
      "insulation_rating_kv": 46
    },
    "dielectric": {
      "last_test_date": "2025-06-15",
      "next_test_due": "2026-06-15"
    }
  }
}
```

**Inspections Triggered:**
- Hydraulic brake inspection (from `HYDRAULIC_BRAKES` on vehicle)
- ANSI A92.2 aerial device inspection (from `AERIAL_DEVICE` equipment type)
- Hydraulic system inspection (from `HYDRAULIC` on equipment)
- Dielectric testing (from `DIELECTRIC` on equipment)

---

### Example 3: Electric Street Sweeper

**Vehicle (from VIN decode):**
```json
{
  "vin": "1HTMMAAN5JH789012",
  "year": 2022,
  "make": "Freightliner",
  "model": "M2-106",
  "vin_decode": {
    "vehicle_type": "Incomplete Vehicle",
    "body_class": "Cab & Chassis",
    "gvwr": "Class 7: 26,001 - 33,000 lb",
    "fuel_type_primary": "Diesel",
    "abs": "Air Brakes"
  },
  "capabilities": ["AIR_BRAKES"]
}
```

**Equipment (sweeper body):**
```json
{
  "serial_number": "TYMCO-45678",
  "equipment_type": "SWEEPER_BODY",
  "manufacturer": "Tymco",
  "model": "DST-6",
  "capabilities": ["HYDRAULIC", "ENGINE_DRIVEN"],
  "equipment_data": {
    "hopper_capacity_cubic_yards": 6,
    "sweeping_width_feet": 10,
    "auxiliary_engine": {
      "make": "John Deere",
      "model": "4045",
      "fuel_type": "Diesel"
    }
  }
}
```

**Inspections/Maintenance Triggered:**
- Air brake inspection on vehicle (from `AIR_BRAKES`)
- Hydraulic system inspection on sweeper (from `HYDRAULIC`)
- Auxiliary engine maintenance on sweeper (from `ENGINE_DRIVEN`)

---

## Implementation

### 1. Adding a Vehicle

```
1. Enter VIN
2. Call NHTSA vPIC API
3. Populate VINDecodeData
4. Auto-populate vehicle capabilities from VIN decode:
   - If vin_decode.abs contains "Air" → add AIR_BRAKES
   - If vin_decode.abs contains "Hydraulic" → add HYDRAULIC_BRAKES
   - If vehicle has 4WD from decode → add FOUR_WHEEL_DRIVE
5. Manual override only if VIN decode is wrong
```

### 2. Adding Equipment

```
1. Is this a special body?
   → If VIN shows "Incomplete Vehicle", create Equipment with body type

2. What work equipment is mounted?
   → Create Equipment record

3. What systems does it have that need inspection/maintenance?
   → Add capability tags (HYDRAULIC, PNEUMATIC, ENGINE_DRIVEN, etc.)
   → These drive inspection template modules
```

### 3. Inspection Template Selection

```python
def get_inspection_modules(vehicle):
    modules = []

    # Vehicle-level modules
    if 'AIR_BRAKES' in vehicle.capabilities:
        modules.append('air_brake_inspection')
    elif 'HYDRAULIC_BRAKES' in vehicle.capabilities:
        modules.append('hydraulic_brake_inspection')

    # Equipment modules
    for equipment in vehicle.equipment.all():
        if equipment.equipment_type == 'AERIAL_DEVICE':
            modules.append('ansi_a92_2_aerial_device')

        if 'HYDRAULIC' in equipment.capabilities:
            modules.append('hydraulic_system_inspection')

        if 'DIELECTRIC' in equipment.capabilities:
            modules.append('dielectric_test')

        if 'ENGINE_DRIVEN' in equipment.capabilities:
            modules.append('auxiliary_engine_inspection')

    return modules
```

---

## Database Queries

### Find all air brake vehicles
```python
vehicles = Vehicle.objects.filter(
    capabilities__contains=['AIR_BRAKES']
)
```

### Find all vehicles with hydraulic equipment
```python
vehicles = Vehicle.objects.filter(
    equipment__capabilities__contains=['HYDRAULIC']
).distinct()
```

### Find all equipment needing dielectric testing
```python
equipment = Equipment.objects.filter(
    capabilities__contains=['DIELECTRIC']
)
```

### Find all generators with engines (need oil changes)
```python
generators = Equipment.objects.filter(
    equipment_type='GENERATOR',
    capabilities__contains=['ENGINE_DRIVEN']
)
```

---

## Summary

**Tags only exist if they affect inspections or maintenance:**

### Vehicle Tags (minimal - mostly from VIN decode)
- `AIR_BRAKES` → Air brake inspection modules
- `HYDRAULIC_BRAKES` → Hydraulic brake inspection modules
- `ELECTRIC_BRAKES` → Electric brake inspection (trailers)
- `FOUR_WHEEL_DRIVE` → Transfer case/front diff inspection
- `SIX_WHEEL_DRIVE` → Additional drivetrain inspection

### Equipment Tags (only when they matter)
- `DIELECTRIC` → Annual dielectric testing
- `HYDRAULIC` → Hydraulic system inspection
- `PNEUMATIC` → Air system inspection
- `ELECTRIC` → Electrical system inspection
- `PTO_DRIVEN` → PTO system inspection
- `ENGINE_DRIVEN` → Engine maintenance (oil, filters, etc.)

**If it doesn't change what you inspect or how you maintain it, don't tag it.**

---

**Last Updated:** 2026-03-12
