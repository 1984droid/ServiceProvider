# Defect Schema Specification

**Version:** 1.0
**Date:** 2026-03-15
**Purpose:** Define the standardized defect schema for structured defect capture during inspections

---

## Overview

The **defect_schema** is a standardized data structure that defines how defects are captured during inspections. It provides a consistent, structured way to document issues found during equipment inspections, ensuring all critical information is collected for work order generation, PDF reporting, and compliance documentation.

---

## Why Defect Schema?

### Problems with Unstructured Defects
❌ Inconsistent data capture
❌ Missing critical information (location, severity, photos)
❌ Hard to generate meaningful work orders
❌ Poor PDF documentation quality
❌ Can't track defect patterns over time

### Benefits of Structured Schema
✅ **Consistent data collection** - Every defect has same fields
✅ **Rich work order generation** - All details flow to repair tasks
✅ **Professional documentation** - PDFs with complete defect details
✅ **Audit compliance** - Complete trail of what/where/when/severity
✅ **Analytics ready** - Can track defect patterns by component/severity
✅ **Photo enforcement** - Automatic photo requirements based on severity

---

## Schema Definition

### Standard Defect Schema (v1.0)

**Used in:** periodic_inspection.json, frequent_inspection.json, major_structural_inspection.json, load_test_only.json, dielectric_test_periodic.json

```json
{
  "defect_schema": {
    "defect_id_format": "UUID",
    "fields": [
      {
        "field_id": "title",
        "type": "TEXT",
        "required": true,
        "max_length": 200,
        "help_text": "Brief, descriptive title of the defect"
      },
      {
        "field_id": "severity",
        "type": "ENUM",
        "enum_ref": "severity",
        "required": true,
        "help_text": "Severity level: SAFE, MINOR, SERVICE_REQUIRED, UNSAFE_OUT_OF_SERVICE"
      },
      {
        "field_id": "description",
        "type": "TEXT_AREA",
        "required": true,
        "max_length": 2000,
        "help_text": "Detailed description of the defect, including observations and measurements"
      },
      {
        "field_id": "component",
        "type": "TEXT",
        "required": false,
        "max_length": 100,
        "help_text": "Component or system where defect was found (e.g., 'Boom Pivot Pin', 'Hydraulic Cylinder')"
      },
      {
        "field_id": "location",
        "type": "TEXT",
        "required": false,
        "max_length": 200,
        "help_text": "Specific location on equipment (e.g., 'Driver side, lower boom section', 'Platform right rear corner')"
      },
      {
        "field_id": "photo_evidence",
        "type": "PHOTO",
        "required": false,
        "conditionally_required_if": {
          "field": "severity",
          "values": ["SERVICE_REQUIRED", "UNSAFE_OUT_OF_SERVICE"]
        },
        "help_text": "Photos documenting the defect. Required for SERVICE_REQUIRED and UNSAFE_OUT_OF_SERVICE severity."
      },
      {
        "field_id": "corrective_action",
        "type": "TEXT_AREA",
        "required": false,
        "max_length": 1000,
        "help_text": "Recommended corrective action or repair procedure"
      },
      {
        "field_id": "standard_reference",
        "type": "TEXT",
        "required": false,
        "max_length": 100,
        "help_text": "Reference to applicable standard section (e.g., 'ANSI A92.2-2021 Section 8.2.4(13)')"
      }
    ]
  }
}
```

---

## Field Specifications

### 1. title (TEXT, REQUIRED)
**Purpose:** Brief, descriptive summary of the defect

**Format:**
- Max length: 200 characters
- Should be concise but descriptive
- Include component and issue type

**Examples:**
- ✅ "Loose structural bolt on pedestal mounting"
- ✅ "Hydraulic fluid leak at boom cylinder rod seal"
- ✅ "Excessive wear on boom pivot pin"
- ✅ "Crack in lower boom section weld"
- ❌ "Bad" (too vague)
- ❌ "Issue found during inspection" (not descriptive)

**Auto-population Strategy:**
When user triggers defect from a field assessment:
```
{component} + {issue_type} + {severity_indicator}

Examples:
- boom_pivot_pins = FAIL → "Failed boom pivot pins"
- boom_pivot_pin_wear = EXCESSIVE → "Excessive wear on boom pivot pins"
- hydraulic_hoses = FAIL → "Failed hydraulic hoses"
```

---

### 2. severity (ENUM, REQUIRED)
**Purpose:** Classify the defect's impact on safety and operations

**Enum Reference:** `severity`

**Values:**
```json
{
  "severity": [
    "SAFE",                      // No safety impact, informational only
    "MINOR",                     // Minor issue, plan for next scheduled maintenance
    "SERVICE_REQUIRED",          // Requires service/repair, schedule soon
    "UNSAFE_OUT_OF_SERVICE"      // Critical safety issue, equipment must be tagged out
  ]
}
```

**Severity Mapping to Work Order Priority:**
| Severity | Work Order Priority | Response Time | Photo Required |
|----------|-------------------|---------------|----------------|
| SAFE | N/A | Informational | No |
| MINOR | LOW | Next scheduled maintenance | Suggested |
| SERVICE_REQUIRED | NORMAL/HIGH | Schedule within 1-2 weeks | **Required** |
| UNSAFE_OUT_OF_SERVICE | EMERGENCY | Immediate - tag out equipment | **Required** |

**Impact on InspectionDefect Model:**
Severity maps to model's severity choices:
```python
SEVERITY_MAPPING = {
    'SAFE': 'ADVISORY',
    'MINOR': 'MINOR',
    'SERVICE_REQUIRED': 'MAJOR',
    'UNSAFE_OUT_OF_SERVICE': 'CRITICAL'
}
```

---

### 3. description (TEXT_AREA, REQUIRED)
**Purpose:** Detailed description of the defect with observations and measurements

**Format:**
- Max length: 2000 characters
- Should include:
  - What was observed
  - Measurements if applicable
  - Comparison to expected/normal condition
  - Any immediate actions taken

**Examples:**

**Good Description:**
```
Hydraulic cylinder rod seal is leaking. Observed steady drip of hydraulic
fluid from lower boom lift cylinder rod seal when boom is fully extended.
Leak rate approximately 1 drop per 3 seconds. Fluid level in reservoir
dropped 1 quart over 30-minute operational test. Rod surface appears
scored near seal area. Recommend cylinder rebuild or replacement.
```

**Adequate Description:**
```
Boom pivot pin shows excessive wear. Pin diameter measured at 1.89"
(spec is 2.00" nominal). Visible play in boom joint - approximately
1/8" vertical movement when boom is raised. Recommend pin replacement
before next use.
```

**Poor Description:**
```
Pin is bad, needs replaced.
```

---

### 4. component (TEXT, OPTIONAL)
**Purpose:** Identify which component or system has the defect

**Format:**
- Max length: 100 characters
- Should be specific but standardized
- Use manufacturer terminology when possible

**Component Categories:**

**Structural:**
- Boom Structure (Base/Mid/Fly Section)
- Platform Floor
- Platform Railings
- Turret
- Pedestal
- Outrigger Beams
- Outrigger Pads

**Fasteners:**
- Boom Pivot Pins
- Structural Bolts
- Platform Mounting Bolts
- Pedestal Mounting Bolts
- Turret Bearing Bolts

**Hydraulic:**
- Hydraulic Cylinders (specify which)
- Hydraulic Hoses
- Hydraulic Pump
- Hydraulic Reservoir
- Control Valves
- Relief Valves

**Electrical:**
- Wiring Harness
- Control Panel
- Batteries
- Lighting System
- Sensors

**Controls:**
- Ground Controls
- Platform Controls
- Emergency Stop Systems
- Limit Switches
- Safety Interlocks

**Examples:**
- "Boom Pivot Pin (upper joint)"
- "Hydraulic Cylinder - Boom Lift"
- "Platform Right Side Railing"
- "Turret Bearing"

---

### 5. location (TEXT, OPTIONAL)
**Purpose:** Specify exact physical location of defect on equipment

**Format:**
- Max length: 200 characters
- Should provide enough detail for technician to find defect
- Use directional references (driver/passenger, front/rear, upper/lower)

**Location Conventions:**

**Directional References:**
- **Driver side / Passenger side** (relative to vehicle orientation)
- **Front / Rear** (relative to vehicle)
- **Upper / Lower** (vertical position)
- **Left / Right** (when facing component)

**Boom Sections:**
- Base section (closest to turret)
- Mid section (middle)
- Fly section (outermost)

**Platform References:**
- Platform floor
- Platform railings (left/right/front/rear)
- Platform controls (left/right side)
- Platform gate

**Examples:**
- ✅ "Driver side, lower boom section, second pivot pin from base"
- ✅ "Platform right rear corner, top rail connection"
- ✅ "Boom lift cylinder, driver side, rod seal"
- ✅ "Turret bearing, passenger side, 3 o'clock position"
- ✅ "Outrigger beam, rear passenger side, pad mounting point"
- ❌ "On the boom" (too vague)
- ❌ "Near the controls" (not specific)

---

### 6. photo_evidence (PHOTO, OPTIONAL → CONDITIONALLY REQUIRED)
**Purpose:** Visual documentation of defect

**Requirements:**
- **Format:** JPEG, PNG, HEIC (mobile)
- **Max file size:** 10MB per photo
- **Max photos per defect:** 10
- **Min resolution:** 1024x768 recommended
- **Auto-metadata:** Timestamp, GPS (if available), device info

**Conditional Requirements:**
```json
"conditionally_required_if": {
  "field": "severity",
  "values": ["SERVICE_REQUIRED", "UNSAFE_OUT_OF_SERVICE"]
}
```

**Photos REQUIRED when:**
- Severity = SERVICE_REQUIRED
- Severity = UNSAFE_OUT_OF_SERVICE

**Photos SUGGESTED when:**
- Severity = MINOR
- Any wear level = MODERATE or EXCESSIVE

**Photo Best Practices:**

**For Structural Defects:**
1. Wide shot showing component location
2. Close-up of defect (crack, deformation, etc.)
3. Measurement reference (ruler, caliper, etc.)

**For Leaks:**
1. Source of leak
2. Drip/puddle showing severity
3. Affected area (fluid accumulation)

**For Wear:**
1. Worn component
2. Comparison to new/good part (if available)
3. Measurement showing wear extent

**Photo Naming Convention (Backend Auto-Generated):**
```
{inspection_id}_{step_key}_{defect_index}_{photo_index}_{timestamp}.jpg

Example:
a3f4e891-..._bolts_fasteners_01_01_20260315143022.jpg
```

---

### 7. corrective_action (TEXT_AREA, OPTIONAL)
**Purpose:** Document recommended repair or corrective action

**Format:**
- Max length: 1000 characters
- Should be actionable and specific
- Can reference parts, procedures, or standards

**Examples:**

**Structural:**
```
Replace boom pivot pin with OEM part #BP-2045. Inspect bushing for
wear during disassembly. If bushing worn, replace with part #BS-2046.
Torque retaining hardware per service manual (85 ft-lbs). Re-inspect
pin after 50 operating hours.
```

**Hydraulic:**
```
Rebuild or replace boom lift cylinder. If rebuilding, replace rod seal
kit (part #SK-1234), inspect rod for scoring. If rod is scored beyond
0.005", replace cylinder assembly. Refill hydraulic reservoir with
AW-32 hydraulic fluid. Test for leaks under full load.
```

**Electrical:**
```
Replace damaged section of wiring harness between control panel and
platform controls. Use marine-grade 14 AWG wire, seal all connections
with heat-shrink tubing. Verify all control functions after repair.
```

**Bolts/Fasteners:**
```
Re-torque all pedestal mounting bolts to specification (120 ft-lbs).
Apply Loctite 242 to threads. Verify no cracks in mounting flanges
before re-torquing. Re-check torque after 8 hours of operation.
```

---

### 8. standard_reference (TEXT, OPTIONAL)
**Purpose:** Link defect to specific standard requirement

**Format:**
- Max length: 100 characters
- Should cite specific section/clause

**Examples:**
- "ANSI A92.2-2021 Section 8.2.4(13)"
- "ANSI A92.5-2021 Section 7.1.3"
- "OSHA 1926.453(b)(2)(v)"
- "Manufacturer Service Bulletin SB-2024-03"

**When to Use:**
- Defect relates to specific standard requirement
- Failure to meet standard specification
- Compliance-related defect

---

## Integration with Inspection Steps

### Step Configuration with defect_schema

**Steps that support structured defect capture must include:**

```json
{
  "step_key": "bolts_fasteners",
  "type": "VISUAL_INSPECTION",
  "title": "Bolts, Pins, and Fasteners Detailed Inspection",
  "standard_reference": "ANSI A92.2-2021 Section 8.2.4(13)",
  "required": true,

  // Link to defect schema
  "defect_schema_ref": "defect_schema",

  // UI mode for defect capture
  "ui": {
    "mode": "ADD_DEFECT_ITEMS",
    "guidance": [
      "Check all bolts, pins, and fasteners for tightness, wear, and damage",
      "When defects are found, click 'Add Defect' to document details",
      "Include photos of any wear, damage, or loose fasteners"
    ]
  },

  // Assessment fields (not defect fields)
  "fields": [
    {
      "field_id": "boom_pivot_pin_wear",
      "label": "Boom Pivot Pin Wear Assessment",
      "type": "ENUM",
      "enum_ref": "wear_level",
      "required": true
    }
    // ... more assessment fields
  ]
}
```

---

## Defect Creation Workflow

### UI Flow

```
1. Inspector performs step assessment
   ↓
2. Selects condition for each component
   - wear_level = EXCESSIVE
   - condition = FAIL
   - leak_severity = MAJOR_LEAK
   ↓
3. System shows "Defects Found" indicator
   - Highlights fields with defect conditions
   - Shows "Add Defect" button
   ↓
4. Inspector clicks "Add Defect"
   ↓
5. Defect creation modal opens with schema fields
   - title: Auto-populated from component + issue
   - severity: REQUIRED dropdown
   - description: REQUIRED textarea
   - component: Optional (pre-filled from field)
   - location: Optional text
   - photo_evidence: CONDITIONALLY REQUIRED based on severity
   - corrective_action: Optional textarea
   - standard_reference: Optional text
   ↓
6. Inspector fills defect details
   - Adds description
   - Uploads photos (if required/suggested)
   - Adds corrective action notes
   ↓
7. Validates defect
   - Check required fields
   - Check photo requirements based on severity
   - Show validation errors if incomplete
   ↓
8. Saves defect to step_data
   ↓
9. Displays defect in step summary
   - Shows defect title
   - Shows severity badge
   - Allows edit/delete before finalization
```

---

## Data Storage

### In InspectionRun.step_data

Defects are stored in `step_data` under each step:

```json
{
  "bolts_fasteners": {
    // Assessment field values
    "boom_pivot_pin_wear": "EXCESSIVE",
    "structural_bolts": "FAIL",

    // Defects array
    "defects": [
      {
        "defect_id": "uuid-generated-frontend",
        "title": "Excessive wear on boom pivot pins",
        "severity": "SERVICE_REQUIRED",
        "description": "Boom pivot pin diameter measured at 1.87\" (spec 2.00\"). Visible play in boom joint approximately 1/8\" vertical movement.",
        "component": "Boom Pivot Pin (upper joint)",
        "location": "Driver side, lower boom section, second pivot pin from base",
        "photo_evidence": [
          "photo_uuid_1",
          "photo_uuid_2"
        ],
        "corrective_action": "Replace boom pivot pin with OEM part #BP-2045. Inspect bushing during disassembly.",
        "standard_reference": "ANSI A92.2-2021 Section 8.2.4(13)"
      },
      {
        "defect_id": "uuid-generated-frontend-2",
        "title": "Loose structural bolts on pedestal mounting",
        "severity": "UNSAFE_OUT_OF_SERVICE",
        "description": "Three of eight pedestal mounting bolts found finger-tight. No visible damage to bolt threads or mounting flanges.",
        "component": "Pedestal Mounting Bolts",
        "location": "Passenger side, lower pedestal flange",
        "photo_evidence": [
          "photo_uuid_3"
        ],
        "corrective_action": "Re-torque all pedestal mounting bolts to 120 ft-lbs with Loctite 242.",
        "standard_reference": "ANSI A92.2-2021 Section 8.2.4"
      }
    ]
  }
}
```

### Conversion to InspectionDefect Records

**On inspection finalization**, defects from `step_data` are converted to `InspectionDefect` model records:

```python
# apps/inspections/models.py - InspectionDefect
{
    "id": UUID,
    "inspection_run_id": UUID,
    "defect_identity": "SHA256(run_id + step_key + defect_id)",
    "step_key": "bolts_fasteners",
    "rule_id": null,  # null for manual defects
    "severity": "MAJOR",  # Mapped from schema severity
    "title": "Excessive wear on boom pivot pins",
    "description": "Boom pivot pin diameter measured at 1.87\"...",
    "defect_details": {
        "component": "Boom Pivot Pin (upper joint)",
        "location": "Driver side, lower boom section...",
        "photos": ["photo_uuid_1", "photo_uuid_2"],
        "corrective_action": "Replace boom pivot pin...",
        "standard_reference": "ANSI A92.2-2021 Section 8.2.4(13)"
    },
    "status": "OPEN",
    "created_at": "2026-03-15T14:30:22Z"
}
```

---

## Severity Mapping

### Template Severity → Model Severity

```python
SEVERITY_MAPPING = {
    # Template value → Database value
    'SAFE': 'ADVISORY',
    'MINOR': 'MINOR',
    'SERVICE_REQUIRED': 'MAJOR',
    'UNSAFE_OUT_OF_SERVICE': 'CRITICAL'
}
```

### Model Severity Definitions

```python
class InspectionDefect(models.Model):
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),      # Unsafe to operate, immediate action
        ('MAJOR', 'Major'),            # Significant issue, schedule repair
        ('MINOR', 'Minor'),            # Maintenance needed, not urgent
        ('ADVISORY', 'Advisory'),      # Informational, no action required
    ]
```

---

## Validation Rules

### Required Field Validation

**Always Required:**
- `title`: Must not be empty
- `severity`: Must be valid enum value
- `description`: Must not be empty

**Conditionally Required:**
- `photo_evidence`: Required when severity = SERVICE_REQUIRED or UNSAFE_OUT_OF_SERVICE

### Field Length Validation

```javascript
{
  title: { maxLength: 200 },
  description: { maxLength: 2000 },
  component: { maxLength: 100 },
  location: { maxLength: 200 },
  corrective_action: { maxLength: 1000 },
  standard_reference: { maxLength: 100 }
}
```

### Photo Validation

```javascript
{
  maxPhotos: 10,
  maxFileSizeMB: 10,
  allowedFormats: ['image/jpeg', 'image/png', 'image/heic'],
  minResolution: { width: 800, height: 600 }
}
```

---

## Frontend Implementation

### Defect Schema Validation (TypeScript)

```typescript
interface DefectSchemaField {
  field_id: string;
  type: 'TEXT' | 'TEXT_AREA' | 'ENUM' | 'PHOTO';
  required: boolean;
  max_length?: number;
  enum_ref?: string;
  conditionally_required_if?: {
    field: string;
    values: string[];
  };
  help_text?: string;
}

interface DefectData {
  defect_id: string;
  title: string;
  severity: 'SAFE' | 'MINOR' | 'SERVICE_REQUIRED' | 'UNSAFE_OUT_OF_SERVICE';
  description: string;
  component?: string;
  location?: string;
  photo_evidence?: string[];
  corrective_action?: string;
  standard_reference?: string;
}

function validateDefect(
  defect: Partial<DefectData>,
  schema: DefectSchemaField[]
): Record<string, string> {
  const errors: Record<string, string> = {};

  for (const field of schema) {
    const value = defect[field.field_id as keyof DefectData];

    // Check required
    if (field.required && !value) {
      errors[field.field_id] = `${field.field_id} is required`;
    }

    // Check conditional requirements
    if (field.conditionally_required_if) {
      const triggerField = field.conditionally_required_if.field;
      const triggerValues = field.conditionally_required_if.values;
      const triggerValue = defect[triggerField as keyof DefectData];

      if (triggerValues.includes(triggerValue as string) && !value) {
        errors[field.field_id] = `${field.field_id} is required for this severity level`;
      }
    }

    // Check max length
    if (field.max_length && typeof value === 'string' && value.length > field.max_length) {
      errors[field.field_id] = `${field.field_id} must be ${field.max_length} characters or less`;
    }
  }

  return errors;
}
```

---

## Backend Processing

### Defect Generation Service

```python
# apps/inspections/services/defect_generator.py

from apps.inspections.models import InspectionDefect
import hashlib
import json

class DefectGenerator:
    """Generate InspectionDefect records from step_data defects."""

    SEVERITY_MAPPING = {
        'SAFE': 'ADVISORY',
        'MINOR': 'MINOR',
        'SERVICE_REQUIRED': 'MAJOR',
        'UNSAFE_OUT_OF_SERVICE': 'CRITICAL'
    }

    @classmethod
    def create_defects_from_step_data(cls, inspection_run):
        """
        Convert defects in step_data to InspectionDefect records.

        Called when inspection is finalized.
        """
        step_data = inspection_run.step_data
        created_defects = []

        for step_key, step_values in step_data.items():
            defects = step_values.get('defects', [])

            for defect_data in defects:
                # Generate defect identity for idempotency
                defect_identity = cls._generate_defect_identity(
                    inspection_run.id,
                    step_key,
                    defect_data.get('defect_id')
                )

                # Map severity
                template_severity = defect_data.get('severity')
                model_severity = cls.SEVERITY_MAPPING.get(template_severity, 'MINOR')

                # Build defect_details
                defect_details = {
                    'component': defect_data.get('component'),
                    'location': defect_data.get('location'),
                    'photos': defect_data.get('photo_evidence', []),
                    'corrective_action': defect_data.get('corrective_action'),
                    'standard_reference': defect_data.get('standard_reference')
                }

                # Create or update defect
                defect, created = InspectionDefect.objects.update_or_create(
                    defect_identity=defect_identity,
                    defaults={
                        'inspection_run': inspection_run,
                        'step_key': step_key,
                        'rule_id': None,  # Manual defect
                        'severity': model_severity,
                        'status': 'OPEN',
                        'title': defect_data.get('title'),
                        'description': defect_data.get('description'),
                        'defect_details': defect_details,
                        'evaluation_trace': {}
                    }
                )

                created_defects.append(defect)

        return created_defects

    @staticmethod
    def _generate_defect_identity(run_id, step_key, defect_id):
        """Generate SHA256 hash for defect identity."""
        identity_string = f"{run_id}_{step_key}_{defect_id}"
        return hashlib.sha256(identity_string.encode()).hexdigest()
```

---

## PDF Export Integration

### Defect Section in PDF

```python
# apps/inspections/services/pdf_export_service.py

def render_defects_section(inspection_run):
    """Render defects section in PDF report."""
    defects = inspection_run.defects.all().order_by('severity', 'step_key')

    html = '<h2>Defects Found</h2>'

    if not defects:
        html += '<p>No defects found during this inspection.</p>'
        return html

    # Group by severity
    critical = defects.filter(severity='CRITICAL')
    major = defects.filter(severity='MAJOR')
    minor = defects.filter(severity='MINOR')
    advisory = defects.filter(severity='ADVISORY')

    for severity_group, label, color in [
        (critical, 'CRITICAL - Unsafe to Operate', '#dc3545'),
        (major, 'MAJOR - Service Required', '#fd7e14'),
        (minor, 'MINOR - Maintenance Recommended', '#ffc107'),
        (advisory, 'ADVISORY - Informational', '#17a2b8')
    ]:
        if severity_group.exists():
            html += f'<h3 style="color: {color}">{label}</h3>'

            for defect in severity_group:
                html += render_defect_item(defect)

    return html

def render_defect_item(defect):
    """Render individual defect with photos."""
    details = defect.defect_details or {}

    html = f'''
    <div class="defect-item">
        <h4>{defect.title}</h4>
        <table>
            <tr>
                <td><strong>Component:</strong></td>
                <td>{details.get('component', 'N/A')}</td>
            </tr>
            <tr>
                <td><strong>Location:</strong></td>
                <td>{details.get('location', 'N/A')}</td>
            </tr>
            <tr>
                <td><strong>Description:</strong></td>
                <td>{defect.description}</td>
            </tr>
            <tr>
                <td><strong>Corrective Action:</strong></td>
                <td>{details.get('corrective_action', 'N/A')}</td>
            </tr>
        </table>
    '''

    # Add photos
    photos = details.get('photos', [])
    if photos:
        html += '<div class="defect-photos">'
        for photo_url in photos:
            html += f'<img src="{photo_url}" style="max-width: 300px; margin: 10px;" />'
        html += '</div>'

    html += '</div>'
    return html
```

---

## Schema Variations by Template

### Periodic Inspection
✅ All 8 fields including `standard_reference`

### Frequent Inspection
✅ 7 fields (no `standard_reference`)

### Dielectric Test
✅ 7 fields with `standard_reference` but no `component`

### Load Test
✅ 8 fields (all)

**Recommendation:** Standardize all templates to use the full 8-field schema for consistency.

---

## Version History

- **v1.0** (2026-03-15): Initial defect schema specification
  - 8 standard fields
  - Conditional photo requirements
  - Severity mapping defined
  - Integration with InspectionDefect model

---

## Next Steps

1. **Standardize schema across all templates** - Add missing fields to make all templates identical
2. **Enhance photo requirements** - Add photo_evidence validation in frontend
3. **Build defect UI components** - Create AddDefectModal, DefectList, DefectItem components
4. **Implement backend processor** - Complete DefectGenerator service
5. **Add PDF defect rendering** - Include defect photos in exported PDFs
6. **Create defect tracking dashboard** - Analytics on defect patterns

---

**Document Status:** ✅ Complete
**Maintainer:** Development Team
**Last Updated:** 2026-03-15
