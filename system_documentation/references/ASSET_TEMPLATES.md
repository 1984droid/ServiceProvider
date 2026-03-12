# Asset Type Templates

This document defines the hierarchical asset type templates for the system. Each asset type inherits fields and capabilities from its parent.

## Template Structure

```
AssetSubtype (key, name, description)
├── Fields (stored in Asset model itself)
├── Capabilities (stored in AssetCapability with CapabilityDefinition)
└── Children (recursive AssetSubtype)
```

## Inheritance Rules

1. **Fields** - Hard-coded in Asset model (VIN, serial_number, etc.)
2. **Capabilities** - Dynamically attached via AssetCapability
3. **Hierarchy** - Each subtype inherits capabilities from all ancestors

### Example: Vehicle > Trailer > DryVan

```
Root Asset
  ├── serial_number (all assets)
  ├── identifier (all assets)
  └── is_active (all assets)

Vehicle (inherits Root Asset)
  ├── vin (17 chars) - Vehicle-specific field
  └── VINDecodeProfile (OneToOne) - NHTSA data

Trailer (inherits Vehicle)
  ├── trailer_type (capability: string)
  ├── trailer_length_ft (capability: decimal)
  └── axle_count (capability: int)

DryVan (inherits Trailer)
  ├── interior_height_inches (capability: decimal)
  ├── has_liftgate (capability: bool)
  ├── has_air_ride (capability: bool)
  └── floor_type (capability: enum: ['aluminum', 'wood', 'steel'])
```

---

## Current Hierarchy

Based on your existing code, you have:

### Minimal Example
```
aerial (Aerial Device)
scissor (Scissor Lift)
```

---

## Proposed Full Hierarchy

Below is a comprehensive asset type hierarchy for various industries.

### 1. VEHICLES

```
vehicle
├── vehicle.light_duty
│   ├── vehicle.light_duty.sedan
│   ├── vehicle.light_duty.suv
│   ├── vehicle.light_duty.pickup
│   └── vehicle.light_duty.van
│       ├── vehicle.light_duty.van.passenger
│       └── vehicle.light_duty.van.cargo
├── vehicle.medium_duty
│   ├── vehicle.medium_duty.box_truck
│   ├── vehicle.medium_duty.flatbed
│   └── vehicle.medium_duty.service_truck
├── vehicle.heavy_duty
│   ├── vehicle.heavy_duty.tractor
│   │   ├── vehicle.heavy_duty.tractor.day_cab
│   │   └── vehicle.heavy_duty.tractor.sleeper
│   ├── vehicle.heavy_duty.dump_truck
│   └── vehicle.heavy_duty.cement_truck
└── vehicle.trailer
    ├── vehicle.trailer.dry_van
    │   ├── vehicle.trailer.dry_van.53ft
    │   ├── vehicle.trailer.dry_van.48ft
    │   └── vehicle.trailer.dry_van.pup_28ft
    ├── vehicle.trailer.refrigerated
    │   ├── vehicle.trailer.refrigerated.53ft
    │   └── vehicle.trailer.refrigerated.48ft
    ├── vehicle.trailer.flatbed
    │   ├── vehicle.trailer.flatbed.48ft
    │   ├── vehicle.trailer.flatbed.53ft
    │   └── vehicle.trailer.flatbed.stepdeck
    ├── vehicle.trailer.lowboy
    ├── vehicle.trailer.tanker
    │   ├── vehicle.trailer.tanker.fuel
    │   ├── vehicle.trailer.tanker.chemical
    │   └── vehicle.trailer.tanker.food_grade
    ├── vehicle.trailer.auto_hauler
    ├── vehicle.trailer.livestock
    ├── vehicle.trailer.dump
    └── vehicle.trailer.specialty
        ├── vehicle.trailer.specialty.car_carrier
        ├── vehicle.trailer.specialty.boat_trailer
        └── vehicle.trailer.specialty.equipment_trailer
```

### 2. EQUIPMENT

```
equipment
├── equipment.mewp (Mobile Elevated Work Platform)
│   ├── equipment.mewp.boom_lift
│   │   ├── equipment.mewp.boom_lift.articulating
│   │   ├── equipment.mewp.boom_lift.telescopic
│   │   └── equipment.mewp.boom_lift.trailer_mounted
│   ├── equipment.mewp.scissor_lift
│   │   ├── equipment.mewp.scissor_lift.electric
│   │   ├── equipment.mewp.scissor_lift.rough_terrain
│   │   └── equipment.mewp.scissor_lift.compact
│   ├── equipment.mewp.personnel_lift
│   │   ├── equipment.mewp.personnel_lift.push_around
│   │   └── equipment.mewp.personnel_lift.self_propelled
│   └── equipment.mewp.aerial_device
│       ├── equipment.mewp.aerial_device.bucket_truck
│       ├── equipment.mewp.aerial_device.digger_derrick
│       └── equipment.mewp.aerial_device.ladder_truck
├── equipment.forklift
│   ├── equipment.forklift.warehouse
│   │   ├── equipment.forklift.warehouse.electric
│   │   ├── equipment.forklift.warehouse.propane
│   │   └── equipment.forklift.warehouse.reach
│   ├── equipment.forklift.rough_terrain
│   ├── equipment.forklift.telehandler
│   └── equipment.forklift.pallet_jack
│       ├── equipment.forklift.pallet_jack.manual
│       └── equipment.forklift.pallet_jack.electric
├── equipment.construction
│   ├── equipment.construction.excavator
│   │   ├── equipment.construction.excavator.mini
│   │   ├── equipment.construction.excavator.standard
│   │   └── equipment.construction.excavator.long_reach
│   ├── equipment.construction.loader
│   │   ├── equipment.construction.loader.skid_steer
│   │   ├── equipment.construction.loader.track_loader
│   │   ├── equipment.construction.loader.wheel_loader
│   │   └── equipment.construction.loader.backhoe
│   ├── equipment.construction.dozer
│   │   ├── equipment.construction.dozer.crawler
│   │   └── equipment.construction.dozer.wheel
│   ├── equipment.construction.grader
│   ├── equipment.construction.roller
│   │   ├── equipment.construction.roller.smooth_drum
│   │   ├── equipment.construction.roller.padfoot
│   │   └── equipment.construction.roller.pneumatic
│   ├── equipment.construction.compactor
│   │   ├── equipment.construction.compactor.vibratory_plate
│   │   ├── equipment.construction.compactor.jumping_jack
│   │   └── equipment.construction.compactor.trench_roller
│   └── equipment.construction.trencher
│       ├── equipment.construction.trencher.walk_behind
│       ├── equipment.construction.trencher.ride_on
│       └── equipment.construction.trencher.chain
├── equipment.generator
│   ├── equipment.generator.portable
│   │   ├── equipment.generator.portable.small (< 5kW)
│   │   ├── equipment.generator.portable.medium (5-20kW)
│   │   └── equipment.generator.portable.large (> 20kW)
│   ├── equipment.generator.towable
│   └── equipment.generator.standby
├── equipment.compressor
│   ├── equipment.compressor.portable
│   │   ├── equipment.compressor.portable.electric
│   │   ├── equipment.compressor.portable.gas
│   │   └── equipment.compressor.portable.diesel
│   ├── equipment.compressor.towable
│   └── equipment.compressor.stationary
├── equipment.welding
│   ├── equipment.welding.stick
│   ├── equipment.welding.mig
│   ├── equipment.welding.tig
│   └── equipment.welding.plasma_cutter
└── equipment.power_tools
    ├── equipment.power_tools.drill
    ├── equipment.power_tools.saw
    │   ├── equipment.power_tools.saw.circular
    │   ├── equipment.power_tools.saw.miter
    │   ├── equipment.power_tools.saw.table
    │   └── equipment.power_tools.saw.band
    ├── equipment.power_tools.grinder
    └── equipment.power_tools.impact_wrench
```

### 3. ELECTRICAL UTILITY

```
electrical
├── electrical.insulating_equipment
│   ├── electrical.insulating_equipment.blanket
│   ├── electrical.insulating_equipment.cover
│   ├── electrical.insulating_equipment.sleeve
│   ├── electrical.insulating_equipment.gloves
│   │   ├── electrical.insulating_equipment.gloves.class_00
│   │   ├── electrical.insulating_equipment.gloves.class_0
│   │   ├── electrical.insulating_equipment.gloves.class_1
│   │   ├── electrical.insulating_equipment.gloves.class_2
│   │   ├── electrical.insulating_equipment.gloves.class_3
│   │   └── electrical.insulating_equipment.gloves.class_4
│   └── electrical.insulating_equipment.matting
├── electrical.test_equipment
│   ├── electrical.test_equipment.dielectric_tester
│   ├── electrical.test_equipment.torque_tester
│   ├── electrical.test_equipment.hydraulic_tester
│   └── electrical.test_equipment.multimeter
├── electrical.hot_stick
│   ├── electrical.hot_stick.measuring
│   ├── electrical.hot_stick.shotgun
│   └── electrical.hot_stick.universal
└── electrical.grounding
    ├── electrical.grounding.cable
    ├── electrical.grounding.clamp
    └── electrical.grounding.mat
```

### 4. HVAC & FACILITIES

```
facilities
├── facilities.hvac
│   ├── facilities.hvac.furnace
│   ├── facilities.hvac.boiler
│   ├── facilities.hvac.chiller
│   ├── facilities.hvac.air_handler
│   └── facilities.hvac.heat_pump
├── facilities.pump
│   ├── facilities.pump.centrifugal
│   ├── facilities.pump.submersible
│   └── facilities.pump.positive_displacement
├── facilities.tank
│   ├── facilities.tank.fuel
│   ├── facilities.tank.water
│   └── facilities.tank.chemical
└── facilities.lighting
    ├── facilities.lighting.floodlight
    └── facilities.lighting.tower
```

### 5. TECHNOLOGY

```
technology
├── technology.computer
│   ├── technology.computer.desktop
│   ├── technology.computer.laptop
│   ├── technology.computer.tablet
│   └── technology.computer.server
├── technology.network
│   ├── technology.network.router
│   ├── technology.network.switch
│   ├── technology.network.firewall
│   └── technology.network.wireless_ap
├── technology.printer
│   ├── technology.printer.laser
│   ├── technology.printer.inkjet
│   └── technology.printer.large_format
└── technology.scanner
```

---

## Capability Definitions by Category

### Universal (All Assets)
```python
{
    "purchase_date": {"type": "date", "name": "Purchase Date"},
    "purchase_price": {"type": "decimal", "name": "Purchase Price"},
    "current_value": {"type": "decimal", "name": "Current Value"},
    "warranty_expiration": {"type": "date", "name": "Warranty Expiration"},
    "service_interval_days": {"type": "int", "name": "Service Interval (Days)"},
    "last_service_date": {"type": "date", "name": "Last Service Date"},
    "next_service_date": {"type": "date", "name": "Next Service Date"},
    "operating_hours": {"type": "int", "name": "Operating Hours"},
    "odometer_miles": {"type": "int", "name": "Odometer (Miles)"},
}
```

### Vehicle-Specific
```python
{
    "vehicle_type": {"type": "enum", "options": ["truck", "trailer", "car", "van"], "name": "Vehicle Type"},
    "fuel_type": {"type": "enum", "options": ["diesel", "gasoline", "electric", "hybrid", "propane", "cng"], "name": "Fuel Type"},
    "fuel_tank_capacity_gallons": {"type": "decimal", "name": "Fuel Tank Capacity (Gallons)"},
    "mpg_average": {"type": "decimal", "name": "MPG Average"},
    "license_plate": {"type": "string", "name": "License Plate"},
    "registration_state": {"type": "string", "name": "Registration State"},
    "registration_expiration": {"type": "date", "name": "Registration Expiration"},
    "insurance_policy_number": {"type": "string", "name": "Insurance Policy Number"},
    "insurance_expiration": {"type": "date", "name": "Insurance Expiration"},
}
```

### Trailer-Specific (Inherits Vehicle)
```python
{
    "trailer_type": {"type": "enum", "options": ["dry_van", "refrigerated", "flatbed", "tanker", "lowboy", "dump", "auto_hauler", "livestock"], "name": "Trailer Type"},
    "trailer_length_ft": {"type": "int", "name": "Trailer Length (ft)"},
    "trailer_width_inches": {"type": "decimal", "name": "Trailer Width (inches)"},
    "trailer_height_inches": {"type": "decimal", "name": "Trailer Height (inches)"},
    "axle_count": {"type": "int", "name": "Axle Count"},
    "gvwr_lbs": {"type": "int", "name": "GVWR (lbs)"},
    "payload_capacity_lbs": {"type": "int", "name": "Payload Capacity (lbs)"},
    "has_air_ride": {"type": "bool", "name": "Air Ride Suspension"},
    "has_liftgate": {"type": "bool", "name": "Has Liftgate"},
    "liftgate_capacity_lbs": {"type": "int", "name": "Liftgate Capacity (lbs)"},
}
```

### Dry Van Trailer-Specific (Inherits Trailer)
```python
{
    "interior_height_inches": {"type": "decimal", "name": "Interior Height (inches)"},
    "interior_width_inches": {"type": "decimal", "name": "Interior Width (inches)"},
    "interior_length_ft": {"type": "decimal", "name": "Interior Length (ft)"},
    "door_type": {"type": "enum", "options": ["swing", "roll_up", "swing_and_roll"], "name": "Door Type"},
    "floor_type": {"type": "enum", "options": ["aluminum", "wood", "steel", "composite"], "name": "Floor Type"},
    "wall_type": {"type": "enum", "options": ["aluminum", "fiberglass", "steel", "composite"], "name": "Wall Type"},
    "has_e_track": {"type": "bool", "name": "Has E-Track"},
    "has_logistic_posts": {"type": "bool", "name": "Has Logistic Posts"},
    "has_side_door": {"type": "bool", "name": "Has Side Door"},
}
```

### Refrigerated Trailer-Specific (Inherits Trailer)
```python
{
    "reefer_unit_make": {"type": "string", "name": "Reefer Unit Make"},
    "reefer_unit_model": {"type": "string", "name": "Reefer Unit Model"},
    "reefer_unit_hours": {"type": "int", "name": "Reefer Unit Hours"},
    "temp_range_min_f": {"type": "int", "name": "Min Temperature (°F)"},
    "temp_range_max_f": {"type": "int", "name": "Max Temperature (°F)"},
    "has_multi_temp_zones": {"type": "bool", "name": "Multi-Temp Zones"},
    "fuel_type_reefer": {"type": "enum", "options": ["diesel", "electric", "hybrid"], "name": "Reefer Fuel Type"},
}
```

### MEWP (Mobile Elevated Work Platform) - Inherits Equipment
```python
{
    "mewp_type": {"type": "enum", "options": ["boom_lift", "scissor_lift", "personnel_lift", "aerial_device"], "name": "MEWP Type"},
    "platform_height_ft": {"type": "decimal", "name": "Platform Height (ft)"},
    "working_height_ft": {"type": "decimal", "name": "Working Height (ft)"},
    "horizontal_reach_ft": {"type": "decimal", "name": "Horizontal Reach (ft)"},
    "platform_capacity_lbs": {"type": "int", "name": "Platform Capacity (lbs)"},
    "power_source": {"type": "enum", "options": ["electric", "diesel", "propane", "hybrid", "hydraulic"], "name": "Power Source"},
    "drive_type": {"type": "enum", "options": ["2wd", "4wd", "track", "none"], "name": "Drive Type"},
    "is_self_propelled": {"type": "bool", "name": "Self-Propelled"},
    "is_indoor_rated": {"type": "bool", "name": "Indoor Rated"},
    "is_outdoor_rated": {"type": "bool", "name": "Outdoor Rated"},
    "ansi_category": {"type": "enum", "options": ["A", "B", "C"], "name": "ANSI Category"},
}
```

### Aerial Device-Specific (Inherits MEWP)
```python
{
    "aerial_device_type": {"type": "enum", "options": ["bucket_truck", "digger_derrick", "ladder_truck"], "name": "Aerial Device Type"},
    "insulated": {"type": "bool", "name": "Insulated"},
    "rated_line_voltage_kv": {"type": "decimal", "name": "Rated Line Voltage (kV)"},
    "dielectric_test_voltage_kv": {"type": "decimal", "name": "Dielectric Test Voltage (kV)"},
    "dielectric_test_date": {"type": "date", "name": "Last Dielectric Test Date"},
    "dielectric_test_due": {"type": "date", "name": "Dielectric Test Due Date"},
    "upper_controls_high_resistance": {"type": "bool", "name": "Upper Controls High Resistance"},
    "barehand_capable": {"type": "bool", "name": "Barehand Capable"},
}
```

### Forklift-Specific
```python
{
    "forklift_type": {"type": "enum", "options": ["warehouse", "rough_terrain", "telehandler", "pallet_jack"], "name": "Forklift Type"},
    "lift_capacity_lbs": {"type": "int", "name": "Lift Capacity (lbs)"},
    "max_lift_height_inches": {"type": "decimal", "name": "Max Lift Height (inches)"},
    "mast_type": {"type": "enum", "options": ["standard", "duplex", "triplex", "quad"], "name": "Mast Type"},
    "power_type": {"type": "enum", "options": ["electric", "propane", "diesel", "gasoline"], "name": "Power Type"},
    "battery_voltage": {"type": "int", "name": "Battery Voltage"},
    "tire_type": {"type": "enum", "options": ["pneumatic", "solid", "cushion"], "name": "Tire Type"},
    "has_side_shift": {"type": "bool", "name": "Has Side Shift"},
    "has_fork_positioner": {"type": "bool", "name": "Has Fork Positioner"},
}
```

### Generator-Specific
```python
{
    "generator_type": {"type": "enum", "options": ["portable", "towable", "standby"], "name": "Generator Type"},
    "power_output_kw": {"type": "decimal", "name": "Power Output (kW)"},
    "voltage_output": {"type": "enum", "options": ["120V", "240V", "120/240V", "480V", "600V"], "name": "Voltage Output"},
    "phase": {"type": "enum", "options": ["single", "three"], "name": "Phase"},
    "fuel_type_generator": {"type": "enum", "options": ["diesel", "gasoline", "propane", "natural_gas"], "name": "Generator Fuel Type"},
    "fuel_tank_hours": {"type": "decimal", "name": "Fuel Tank Runtime (hours)"},
    "is_automatic_transfer_switch": {"type": "bool", "name": "Automatic Transfer Switch"},
}
```

### Compressor-Specific
```python
{
    "compressor_type": {"type": "enum", "options": ["portable", "towable", "stationary"], "name": "Compressor Type"},
    "cfm_rating": {"type": "int", "name": "CFM Rating"},
    "pressure_psi": {"type": "int", "name": "Max Pressure (PSI)"},
    "tank_size_gallons": {"type": "int", "name": "Tank Size (Gallons)"},
    "power_source_compressor": {"type": "enum", "options": ["electric", "gas", "diesel"], "name": "Power Source"},
}
```

### Electrical Insulating Equipment
```python
{
    "electrical_category": {"type": "enum", "options": ["00", "0", "1", "2", "3", "4"], "name": "Voltage Class"},
    "max_use_voltage": {"type": "int", "name": "Max Use Voltage (AC)"},
    "proof_test_voltage": {"type": "int", "name": "Proof Test Voltage (AC)"},
    "test_date": {"type": "date", "name": "Last Test Date"},
    "test_due_date": {"type": "date", "name": "Next Test Due Date"},
    "test_interval_months": {"type": "int", "name": "Test Interval (Months)"},
    "size": {"type": "string", "name": "Size"},
}
```

---

## Implementation Scripts

### Script 1: Import Asset Subtypes from JSON

Create a JSON file with your hierarchy:

```json
{
  "vehicle": {
    "name": "Vehicle",
    "description": "All motorized vehicles",
    "children": {
      "vehicle.trailer": {
        "name": "Trailer",
        "description": "Towed trailers",
        "children": {
          "vehicle.trailer.dry_van": {
            "name": "Dry Van Trailer",
            "description": "Enclosed dry freight trailer",
            "children": {}
          }
        }
      }
    }
  }
}
```

Then run:

```python
python manage.py import_asset_subtypes asset_hierarchy.json
```

### Script 2: Import Capability Definitions from JSON

```json
{
  "trailer_length_ft": {
    "name": "Trailer Length (ft)",
    "capability_type": "int",
    "description": "Trailer length in feet"
  },
  "has_liftgate": {
    "name": "Has Liftgate",
    "capability_type": "bool",
    "description": "Whether trailer has a liftgate"
  }
}
```

---

## Visualization Tool

I recommend creating a management command to visualize the tree:

```bash
python manage.py show_asset_tree
```

Output:
```
vehicle (Vehicle)
├── vehicle.light_duty (Light Duty Vehicle)
│   ├── vehicle.light_duty.sedan (Sedan)
│   ├── vehicle.light_duty.suv (SUV)
│   └── vehicle.light_duty.pickup (Pickup Truck)
├── vehicle.medium_duty (Medium Duty Vehicle)
└── vehicle.trailer (Trailer)
    ├── vehicle.trailer.dry_van (Dry Van Trailer)
    │   ├── vehicle.trailer.dry_van.53ft (53' Dry Van)
    │   └── vehicle.trailer.dry_van.48ft (48' Dry Van)
    ├── vehicle.trailer.refrigerated (Refrigerated Trailer)
    └── vehicle.trailer.flatbed (Flatbed Trailer)
```

---

## Next Steps

1. **Choose your asset categories** - Which of the above hierarchies are relevant to your business?
2. **Define capabilities** - Which fields should be capabilities vs. hard-coded fields?
3. **Create JSON templates** - Build JSON files for bulk import
4. **Import data** - Use management commands to populate the database
5. **Test hierarchy** - Create test assets and verify inheritance

Would you like me to:
- Create management commands for importing these templates?
- Build a specific hierarchy for your use case?
- Create a web UI for managing the asset type tree?
