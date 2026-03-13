# Equipment Data Schemas

**Purpose:** Define the expected structure of `equipment_data` JSONField for each equipment type.

**Philosophy:** Each equipment type has specific data requirements driven by:
1. **Placard Information** - Manufacturer specs, capacities, ratings
2. **Safety Systems** - Features required by standards (LMI, anti-two-block, etc.)
3. **Inspection Requirements** - Data needed during standards-based inspections
4. **Regulatory Compliance** - ANSI/ASME/OSHA required documentation

---

## General Guidelines

- `equipment_data` is a **JSONField** on the Equipment model
- Schemas are **flexible** - not all fields required for all equipment
- **Inspector-facing** - data that inspectors need before/during inspections
- **Single source of truth** - collect once, use for all inspections
- Store dates as ISO 8601 strings (`YYYY-MM-DD`)
- Store measurements in **imperial units** (ft, lbs, mph) unless otherwise noted

---

## A92_2_AERIAL - Vehicle-Mounted Elevating & Rotating Aerial Devices

**Standards:** ANSI/SAIA A92.2-2021
**Examples:** Bucket trucks, articulating/telescoping booms mounted on trucks
**Inspection Templates:** ANSI A92.2 Periodic, ANSI A92.2 Dielectric (if insulated)

### Schema

```json
{
  "placard_info": {
    "manufacturer": "Altec",
    "model": "AT37G",
    "serial_number": "12345AB",
    "manufacture_year": 2018,
    "max_platform_height_ft": 37,
    "max_working_height_ft": 43,
    "platform_capacity_lbs": 300,
    "max_wind_speed_mph": 25,
    "placard_location": "Lower boom section, driver's side"
  },
  "insulation_specs": {
    "is_insulated": true,
    "unit_category": "A",
    "rated_line_voltage_kv": 46.0,
    "test_type": "AC",
    "bare_hand_rated": true,
    "last_dielectric_test_date": "2024-06-15",
    "next_dielectric_test_due": "2024-12-15",
    "insulation_notes": "Category A - Bare-hand work rated for 46kV lines"
  },
  "boom_specs": {
    "boom_type": "Telescoping",
    "number_of_sections": 3,
    "articulating": false,
    "telescoping": true,
    "jib_boom": false,
    "over_center_capable": true
  },
  "safety_systems": {
    "insulated_lower_controls": true,
    "high_resistance_upper_controls": false,
    "platform_load_sensor": true,
    "tilt_alarm": true,
    "platform_rotation_limiter": true,
    "boom_cradle": true
  },
  "hydraulic_info": {
    "hydraulic_fluid_type": "Dexron III ATF",
    "reservoir_capacity_gal": 25,
    "relief_valve_settings_psi": {
      "boom_functions": 3000,
      "platform_functions": 2500
    }
  }
}
```

### Field Definitions

#### placard_info
- **manufacturer** - Equipment manufacturer name
- **model** - Model designation
- **serial_number** - Manufacturer serial number
- **manufacture_year** - Year manufactured
- **max_platform_height_ft** - Maximum platform height from ground (feet)
- **max_working_height_ft** - Maximum working height (typically platform + 6ft)
- **platform_capacity_lbs** - Rated platform capacity (pounds)
- **max_wind_speed_mph** - Maximum operating wind speed (mph)
- **placard_location** - Physical location of placard on equipment

#### insulation_specs (only if capabilities includes INSULATING_SYSTEM)
- **is_insulated** - Boolean, true if equipment has insulating boom
- **unit_category** - A92.2 category: A, B, C, D, or E
  - **Category A/B**: Bare-hand work units (strict leakage limits)
  - **Category C/D/E**: Cover-up work units (relaxed leakage limits)
- **rated_line_voltage_kv** - Rated line voltage in kilovolts
- **test_type** - "AC" or "DC" testing
- **bare_hand_rated** - Boolean, true if rated for bare-hand technique
- **last_dielectric_test_date** - ISO date of last dielectric test
- **next_dielectric_test_due** - ISO date when next test is due
- **insulation_notes** - Additional insulation system notes

#### boom_specs
- **boom_type** - "Telescoping", "Articulating", "Articulating/Telescoping"
- **number_of_sections** - Number of boom sections
- **articulating** - Boolean, has articulating joints
- **telescoping** - Boolean, has telescoping sections
- **jib_boom** - Boolean, has jib attachment
- **over_center_capable** - Boolean, can operate over center of rotation

#### safety_systems
- **insulated_lower_controls** - Boolean, lower controls insulated
- **high_resistance_upper_controls** - Boolean, upper controls use high-resistance components (A92.2 5.4.3.6)
- **platform_load_sensor** - Boolean, has platform overload sensor
- **tilt_alarm** - Boolean, has chassis tilt alarm
- **platform_rotation_limiter** - Boolean, has platform rotation limiter
- **boom_cradle** - Boolean, has boom storage cradle

#### hydraulic_info
- **hydraulic_fluid_type** - Type of hydraulic fluid
- **reservoir_capacity_gal** - Reservoir capacity (gallons)
- **relief_valve_settings_psi** - Object with relief valve pressure settings

---

## A92_20_SCISSOR - Scissor Lifts (Self-Propelled)

**Standards:** ANSI A92.20
**Examples:** Electric slab scissors, rough terrain diesel scissors
**Inspection Templates:** ANSI A92.20 Periodic

### Schema

```json
{
  "placard_info": {
    "manufacturer": "Genie",
    "model": "GS-3246",
    "serial_number": "GS3246-123456",
    "manufacture_year": 2020,
    "max_platform_height_ft": 32,
    "max_working_height_ft": 38,
    "platform_capacity_lbs": 500,
    "platform_length_in": 115,
    "platform_width_in": 46,
    "overall_width_in": 46,
    "stowed_height_in": 80,
    "max_wind_speed_mph": 28
  },
  "drive_specs": {
    "drive_type": "Electric",
    "battery_voltage": 48,
    "rough_terrain_capable": false,
    "indoor_rated": true,
    "outdoor_rated": false,
    "non_marking_tires": true
  },
  "safety_systems": {
    "platform_overload_sensor": true,
    "tilt_alarm": true,
    "descent_alarm": true,
    "pothole_guards": true,
    "dual_lane_access": false,
    "lanyard_attachment_points": 4
  }
}
```

---

## A92_20_BOOM - Boom Lifts (Self-Propelled)

**Standards:** ANSI A92.20
**Examples:** Articulating boom lifts, telescoping boom lifts
**Inspection Templates:** ANSI A92.20 Periodic

### Schema

```json
{
  "placard_info": {
    "manufacturer": "JLG",
    "model": "600AJ",
    "serial_number": "JLG600AJ-789012",
    "manufacture_year": 2019,
    "max_platform_height_ft": 60,
    "max_working_height_ft": 66,
    "max_horizontal_outreach_ft": 51,
    "platform_capacity_lbs": 500,
    "max_wind_speed_mph": 28
  },
  "boom_specs": {
    "boom_type": "Articulating",
    "articulating": true,
    "telescoping": false,
    "jib_boom": true,
    "up_and_over_clearance_ft": 25
  },
  "drive_specs": {
    "drive_type": "Diesel",
    "rough_terrain_capable": true,
    "4wd": true,
    "oscillating_axle": true
  },
  "safety_systems": {
    "platform_overload_sensor": true,
    "tilt_alarm": true,
    "platform_rotation_limiter": true,
    "descent_alarm": true,
    "lanyard_attachment_points": 4
  }
}
```

---

## B30_5_CRANE - Mobile/Locomotive Cranes

**Standards:** ANSI/ASME B30.5
**Examples:** Hydraulic truck cranes, rough terrain cranes, all-terrain cranes
**Inspection Templates:** ASME B30.5 Periodic, ASME B30.5 Frequent

### Schema

```json
{
  "placard_info": {
    "manufacturer": "Manitex",
    "model": "TC50155",
    "serial_number": "MAN-TC50155-456789",
    "manufacture_year": 2019,
    "rated_capacity_tons": 50,
    "max_boom_length_ft": 155,
    "max_jib_length_ft": 58,
    "max_tip_height_ft": 213
  },
  "boom_specs": {
    "boom_type": "Telescoping Hydraulic",
    "number_of_sections": 6,
    "boom_extension_type": "Hydraulic",
    "jib_available": true,
    "jib_offset_angles_deg": [5, 15, 30, 45]
  },
  "safety_systems": {
    "load_moment_indicator": true,
    "lmi_manufacturer": "RaycoWylie",
    "lmi_model": "i4500",
    "anti_two_block": true,
    "atb_manufacturer": "Rayco",
    "load_charts_on_file": true,
    "outrigger_monitoring": true,
    "swing_brake": true,
    "boom_angle_indicator": true
  },
  "capacity_info": {
    "max_rated_capacity_tons": 50,
    "capacity_at_max_radius_tons": 2.5,
    "main_hoist_line_pulls": 4,
    "aux_hoist_line_pulls": 2,
    "hook_block_weight_lbs": 850
  },
  "wire_rope_info": {
    "main_hoist_diameter_in": 0.625,
    "main_hoist_construction": "6x19 IWRC",
    "aux_hoist_diameter_in": 0.5,
    "aux_hoist_construction": "6x19 IWRC",
    "boom_hoist_diameter_in": 0.5
  }
}
```

---

## B30_22_ARTICULATING - Articulating Boom Cranes

**Standards:** ANSI/ASME B30.22
**Examples:** Knuckle boom cranes, loader cranes, stiff-boom cranes
**Inspection Templates:** ASME B30.22 Periodic

### Schema

```json
{
  "placard_info": {
    "manufacturer": "Palfinger",
    "model": "PK 32002",
    "serial_number": "PAL-32002-123456",
    "manufacture_year": 2021,
    "rated_capacity_ton_meters": 32,
    "max_hydraulic_outreach_ft": 65,
    "max_tip_height_ft": 68
  },
  "boom_specs": {
    "boom_type": "Articulating Hydraulic",
    "number_of_main_sections": 4,
    "number_of_extensions": 2,
    "rotation_degrees": 400,
    "jib_available": true,
    "jib_type": "Hydraulic telescoping"
  },
  "safety_systems": {
    "load_moment_indicator": true,
    "lmi_manufacturer": "Palfinger",
    "overload_protection": true,
    "stability_control": true,
    "outrigger_monitoring": true,
    "load_charts_on_file": true
  },
  "mounting_info": {
    "mounted_on_vehicle": true,
    "mounting_type": "Fifth wheel mounted",
    "requires_outriggers": true,
    "number_of_outriggers": 4
  }
}
```

---

## DIGGER_DERRICK

**Standards:** ANSI/ASME B30.14, OSHA 1926 Subpart V
**Examples:** Utility digger derricks, pole setters
**Inspection Templates:** B30.14 Periodic, OSHA Utility Work

### Schema

```json
{
  "placard_info": {
    "manufacturer": "Terex",
    "model": "Commander 4047",
    "serial_number": "TRX-CMD4047-987654",
    "manufacture_year": 2018,
    "rated_capacity_lbs": 10000,
    "max_boom_length_ft": 47,
    "max_auger_diameter_in": 36,
    "max_auger_depth_ft": 10
  },
  "boom_specs": {
    "boom_type": "Telescoping Hydraulic",
    "number_of_sections": 3,
    "boom_rotation_degrees": 360,
    "sheave_height_ft": 51
  },
  "auger_specs": {
    "auger_type": "Hydraulic planetary",
    "max_torque_ft_lbs": 15000,
    "auger_diameters_available_in": [18, 24, 30, 36]
  },
  "safety_systems": {
    "load_moment_indicator": true,
    "anti_two_block": true,
    "outrigger_interlocks": true,
    "boom_angle_indicator": true,
    "load_charts_on_file": true
  }
}
```

---

## FORKLIFT

**Standards:** OSHA 1910.178, ANSI/ASME B56.1
**Examples:** Counterbalance forklifts, reach trucks, telehandlers
**Inspection Templates:** OSHA Powered Industrial Trucks

### Schema

```json
{
  "placard_info": {
    "manufacturer": "Toyota",
    "model": "8FGU25",
    "serial_number": "TOY-8FGU25-321654",
    "manufacture_year": 2020,
    "rated_capacity_lbs": 5000,
    "load_center_in": 24,
    "max_lift_height_in": 189
  },
  "power_specs": {
    "power_type": "LPG",
    "fuel_type": "Propane",
    "battery_voltage": null,
    "engine_model": "1DZ-III"
  },
  "mast_specs": {
    "mast_type": "Triple Stage",
    "free_lift_in": 68,
    "max_lift_height_in": 189,
    "lowered_height_in": 85
  },
  "safety_systems": {
    "overhead_guard": true,
    "load_backrest": true,
    "seat_belt": true,
    "horn": true,
    "backup_alarm": true,
    "strobe_light": true
  }
}
```

---

## GENERATOR

**Standards:** NFPA 110, Manufacturer specs
**Examples:** Portable generators, trailer-mounted generators
**Inspection Templates:** Generator Maintenance, NFPA 110

### Schema

```json
{
  "placard_info": {
    "manufacturer": "Generac",
    "model": "MDG100DF4",
    "serial_number": "GEN-MDG100-654321",
    "manufacture_year": 2019,
    "rated_output_kw": 100,
    "voltage_options": [120, 240, 208, 480],
    "phase": "Three Phase",
    "power_factor": 0.8
  },
  "engine_specs": {
    "engine_manufacturer": "John Deere",
    "engine_model": "4045TF280",
    "fuel_type": "Diesel",
    "fuel_tank_capacity_gal": 75,
    "run_time_at_full_load_hours": 24
  },
  "alternator_specs": {
    "alternator_manufacturer": "Stamford",
    "alternator_model": "HC5",
    "cooling_type": "Radiator"
  },
  "safety_systems": {
    "ground_fault_protection": true,
    "low_oil_shutdown": true,
    "high_temp_shutdown": true,
    "overcurrent_protection": true
  }
}
```

---

## COMPRESSOR - Air Compressor

**Standards:** ASME Section VIII, Manufacturer specs
**Examples:** Portable diesel air compressors, trailer-mounted compressors
**Inspection Templates:** Compressor Maintenance

### Schema

```json
{
  "placard_info": {
    "manufacturer": "Atlas Copco",
    "model": "XAS 375 JD7",
    "serial_number": "ATC-XAS375-147258",
    "manufacture_year": 2020,
    "rated_cfm": 375,
    "max_pressure_psi": 150
  },
  "engine_specs": {
    "engine_manufacturer": "John Deere",
    "engine_model": "4045HF475",
    "fuel_type": "Diesel",
    "fuel_tank_capacity_gal": 50
  },
  "compressor_specs": {
    "compressor_type": "Rotary Screw",
    "stages": 1,
    "lubrication_type": "Oil-injected"
  },
  "safety_systems": {
    "pressure_relief_valve": true,
    "safety_valve_set_pressure_psi": 175,
    "low_oil_shutdown": true,
    "high_temp_shutdown": true
  }
}
```

---

## WELDER

**Standards:** AWS, Manufacturer specs
**Examples:** Engine-driven welders, portable welding machines
**Inspection Templates:** Welder Maintenance

### Schema

```json
{
  "placard_info": {
    "manufacturer": "Lincoln Electric",
    "model": "Ranger 330MPX",
    "serial_number": "LIN-R330-963852",
    "manufacture_year": 2021,
    "output_amperage": 330,
    "duty_cycle_percent": 100,
    "processes_supported": ["SMAW", "GMAW", "GTAW", "FCAW"]
  },
  "engine_specs": {
    "engine_manufacturer": "Kubota",
    "engine_model": "D1105-E4BG",
    "fuel_type": "Diesel",
    "fuel_tank_capacity_gal": 12
  },
  "output_specs": {
    "dc_output_range_amps": "40-330",
    "ac_output_range_amps": "40-250",
    "auxiliary_power_watts": 11000,
    "auxiliary_power_voltage": 120/240
  }
}
```

---

## Usage in Application

### Creating Equipment
When creating equipment with a specific `equipment_type`, the application should:
1. Show appropriate form fields based on equipment type
2. Validate required fields for that type
3. Store data in `equipment_data` JSONField

### During Inspections
When inspector starts an inspection:
1. Equipment data is displayed on inspection start screen
2. Critical values (capacities, ratings, etc.) are pre-filled into inspection forms
3. Inspector verifies accuracy before proceeding

### Template Filtering
Templates check:
- `equipment_type` matches template domain
- `capabilities` array contains required capabilities
- Equipment data has necessary placard info for inspection

---

## Versioning

**Current Version:** 1.0
**Last Updated:** 2026-03-13

As new inspection templates are added, this document will be updated with additional equipment types and refined data schemas.
