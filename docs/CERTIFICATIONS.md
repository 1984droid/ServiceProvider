# Inspector Certifications

## Overview

The system automatically matches inspector certifications to inspection standards and pre-populates certification information in inspection runs.

## Certification Data Structure

Employee certifications are stored in the `Employee.certifications` JSON field with the following structure:

```json
[
  {
    "standard": "ANSI/SAIA A92.2",
    "cert_number": "A92-12345",
    "expiry": "2025-12-31",
    "issued_by": "SAIA",
    "issued_date": "2023-01-15"
  },
  {
    "standard": "ANSI/ALOIM A10.31",
    "cert_number": "A10-67890",
    "expiry": "2026-06-30",
    "issued_by": "ALOIM",
    "issued_date": "2024-01-20"
  }
]
```

### Required Fields

- **standard** (string): The standard code, must match template's `standard.code` exactly
  - Example: `"ANSI/SAIA A92.2"`
  - This is used for automatic matching with inspection templates

- **cert_number** (string): The certification/license number
  - Example: `"A92-12345"`
  - Displayed on inspection reports and forms

- **expiry** (string): Expiration date in ISO format (YYYY-MM-DD)
  - Example: `"2025-12-31"`
  - Used for validation and warnings

### Optional Fields

- **issued_by** (string): Certifying organization
- **issued_date** (string): Date issued in ISO format (YYYY-MM-DD)
- **notes** (string): Additional notes about the certification

## Automatic Matching

When an inspection is created:

1. System extracts the `standard.code` from the inspection template
   - Example: Template has `"standard": {"code": "ANSI/SAIA A92.2", "revision": "2021"}`

2. System searches the logged-in user's `employee.certifications` for a matching standard
   - Matches on exact `standard` field value

3. If found, certification info is stored in `inspection.metadata.inspector_certification`:
   ```json
   {
     "inspector_certification": {
       "standard": "ANSI/SAIA A92.2",
       "cert_number": "A92-12345",
       "expiry_date": "2025-12-31",
       "inspector_name": "John Smith"
     }
   }
   ```

4. This certification info is then available:
   - For display in inspection forms
   - For validation (checking expiry)
   - For inclusion in PDF reports
   - For audit trails

## Common Standards

Standard codes used in templates:

- `ANSI/SAIA A92.2` - Vehicle-Mounted Elevating and Rotating Aerial Devices
- `ANSI/ALOIM A10.31` - Safety Requirements for Aerial Lifts
- `ANSI/SAIA A92.5` - Boom-Supported Elevating Work Platforms
- `ANSI/SAIA A92.6` - Self-Propelled Elevating Work Platforms

## Managing Certifications

### Adding Certifications to an Employee

Certifications are managed through the Employee model. Use Django admin or API:

```python
employee.certifications = [
    {
        "standard": "ANSI/SAIA A92.2",
        "cert_number": "A92-12345",
        "expiry": "2025-12-31",
        "issued_by": "SAIA",
        "issued_date": "2023-01-15"
    }
]
employee.save()
```

### Validation

Consider implementing validation for:
- Certification expiry dates before allowing inspections
- Warning if certification expires within 30 days
- Preventing inspections if inspector lacks required certification

## Future Enhancements

Potential improvements:

1. **Expiry Warnings**: Alert inspectors when certifications are expiring soon
2. **Required Certifications**: Enforce that inspector must have matching certification
3. **Certification Photos**: Attach scanned certification documents
4. **Renewal Tracking**: Track certification renewal history
5. **Multi-Standard**: Some inspections may require multiple certifications
