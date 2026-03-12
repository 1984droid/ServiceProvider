# API Reference

Complete REST API documentation for NEW_BUILD_STARTER.

**Base URL:** `http://localhost:8100/api/`

**API Style:** RESTful with Django REST Framework

---

## Table of Contents

1. [Authentication](#authentication)
2. [Common Patterns](#common-patterns)
3. [Customer Management](#customer-management)
4. [Contact Management](#contact-management)
5. [USDOT Profile Management](#usdot-profile-management)
6. [Vehicle Management](#vehicle-management)
7. [Equipment Management](#equipment-management)
8. [VIN Decode Data Management](#vin-decode-data-management)
9. [Error Responses](#error-responses)

---

## Authentication

**Current:** No authentication required (development mode)

**Future:** JWT authentication via djangorestframework-simplejwt

```http
Authorization: Bearer <token>
```

---

## Common Patterns

### Pagination

All list endpoints support pagination:

```http
GET /api/customers/?page=2&page_size=50
```

**Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8100/api/customers/?page=3",
  "previous": "http://localhost:8100/api/customers/?page=1",
  "results": [...]
}
```

### Filtering

```http
GET /api/customers/?is_active=true&state=CA
GET /api/vehicles/?customer={uuid}&is_active=true
GET /api/equipment/?tags=AERIAL_DEVICE&mounted=true
```

### Search

```http
GET /api/customers/?search=acme
GET /api/vehicles/?search=F350
GET /api/contacts/?search=john
```

### Ordering

```http
GET /api/customers/?ordering=name
GET /api/customers/?ordering=-created_at  # Descending
GET /api/vehicles/?ordering=year,make
```

### Soft Delete

Most DELETE operations perform soft delete (set `is_active=False`):

```http
DELETE /api/customers/{id}/
```

For hard delete:
```http
DELETE /api/customers/{id}/?force_delete=true
```

---

## Customer Management

### List Customers

```http
GET /api/customers/
```

**Query Parameters:**
- `is_active` (boolean) - Filter by active status
- `state` (string) - Filter by state code
- `has_usdot` (boolean) - Filter customers with/without USDOT
- `has_mc` (boolean) - Filter customers with/without MC number
- `has_contacts` (boolean) - Filter customers with/without contacts
- `search` (string) - Search name, legal_name, city, USDOT, MC
- `ordering` (string) - Order by: name, created_at, city, state

**Response:** `200 OK`
```json
{
  "count": 25,
  "results": [
    {
      "id": "uuid",
      "name": "Acme Utilities",
      "legal_name": "Acme Utilities Corporation",
      "city": "Springfield",
      "state": "IL",
      "usdot_number": "123456",
      "mc_number": "MC654321",
      "is_active": true,
      "primary_contact_name": "John Doe",
      "contact_count": 3,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### Create Customer

```http
POST /api/customers/
```

**Body:**
```json
{
  "name": "ABC Trucking",
  "legal_name": "ABC Trucking LLC",
  "address_line1": "123 Main St",
  "city": "Chicago",
  "state": "IL",
  "postal_code": "60601",
  "country": "US",
  "usdot_number": "999888",
  "mc_number": "MC888999",
  "notes": "New customer",
  "initial_contact": {
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@abctrucking.com",
    "phone": "555-1234"
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "ABC Trucking",
  ...
}
```

### Get Customer Detail

```http
GET /api/customers/{id}/
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "ABC Trucking",
  "legal_name": "ABC Trucking LLC",
  "address_line1": "123 Main St",
  "address_line2": null,
  "city": "Chicago",
  "state": "IL",
  "postal_code": "60601",
  "country": "US",
  "usdot_number": "999888",
  "mc_number": "MC888999",
  "is_active": true,
  "notes": "New customer",
  "primary_contact": "uuid",
  "primary_contact_name": "Jane Smith",
  "contacts": [
    {
      "id": "uuid",
      "full_name": "Jane Smith",
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@abctrucking.com",
      "phone": "555-1234",
      "is_primary": true,
      "is_active": true
    }
  ],
  "usdot_profile": null,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Update Customer

```http
PATCH /api/customers/{id}/
```

**Body:**
```json
{
  "address_line1": "456 New Address",
  "notes": "Updated address"
}
```

**Response:** `200 OK`

### Delete Customer

```http
DELETE /api/customers/{id}/
```

**Response:** `204 No Content` (soft delete - sets `is_active=False`)

### Set Primary Contact

```http
POST /api/customers/{id}/set_primary_contact/
```

**Body:**
```json
{
  "contact_id": "uuid"
}
```

**Response:** `200 OK`

### Get Customer Contacts

```http
GET /api/customers/{id}/contacts/
```

**Query Parameters:**
- `is_active` (boolean) - Filter by active status

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "full_name": "Jane Smith",
    "email": "jane@abctrucking.com",
    "is_primary": true,
    "is_active": true
  }
]
```

### Search by USDOT

```http
GET /api/customers/search_by_usdot/?usdot=123456
```

**Response:** `200 OK` (Customer detail) or `404 Not Found`

---

## Contact Management

### List Contacts

```http
GET /api/contacts/
```

**Query Parameters:**
- `is_active` (boolean) - Filter by active status
- `is_automated` (boolean) - Filter automated contacts
- `customer` (uuid) - Filter by customer
- `primary` (boolean) - Show only primary contacts
- `has_email` (boolean) - Filter contacts with/without email
- `search` (string) - Search name, email, phone
- `ordering` (string) - Order by: last_name, first_name, created_at, email

**Response:** `200 OK`
```json
{
  "results": [
    {
      "id": "uuid",
      "full_name": "Jane Smith",
      "first_name": "Jane",
      "last_name": "Smith",
      "title": "Fleet Manager",
      "email": "jane@abctrucking.com",
      "phone": "555-1234",
      "mobile": "555-5678",
      "is_primary": true,
      "is_automated": false,
      "is_active": true
    }
  ]
}
```

### Create Contact

```http
POST /api/contacts/
```

**Body:**
```json
{
  "customer": "uuid",
  "first_name": "John",
  "last_name": "Doe",
  "title": "Maintenance Supervisor",
  "email": "john@abctrucking.com",
  "phone": "555-2345",
  "mobile": "555-6789",
  "receive_service_updates": true,
  "receive_inspection_reports": true
}
```

**Response:** `201 Created`

### Get Contact Detail

```http
GET /api/contacts/{id}/
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "customer": "uuid",
  "customer_name": "ABC Trucking",
  "full_name": "John Doe",
  "first_name": "John",
  "last_name": "Doe",
  "title": "Maintenance Supervisor",
  "email": "john@abctrucking.com",
  "phone": "555-2345",
  "phone_extension": null,
  "mobile": "555-6789",
  "is_active": true,
  "is_automated": false,
  "is_primary": false,
  "receive_invoices": false,
  "receive_estimates": false,
  "receive_service_updates": true,
  "receive_inspection_reports": true,
  "notes": "",
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-01-15T11:00:00Z"
}
```

### Update Contact

```http
PATCH /api/contacts/{id}/
```

**Body:**
```json
{
  "mobile": "555-9999",
  "receive_invoices": true
}
```

**Response:** `200 OK`

### Delete Contact

```http
DELETE /api/contacts/{id}/
```

**Response:** `204 No Content`

### Make Primary Contact

```http
POST /api/contacts/{id}/make_primary/
```

**Response:** `200 OK` (sets this contact as customer's primary contact)

---

## USDOT Profile Management

### List USDOT Profiles

```http
GET /api/usdot-profiles/
```

**Query Parameters:**
- `customer` (uuid) - Filter by customer
- `safety_rating` (string) - Filter by safety rating
- `search` (string) - Search USDOT, MC, legal name, DBA

**Response:** `200 OK`

### Create USDOT Profile

```http
POST /api/usdot-profiles/
```

**Body:**
```json
{
  "customer": "uuid",
  "usdot_number": "123456",
  "mc_number": "MC654321",
  "legal_name": "Acme Utilities Corporation",
  "dba_name": "Acme Utilities",
  "physical_address_line1": "123 Industrial Pkwy",
  "physical_city": "Springfield",
  "physical_state": "IL",
  "physical_postal_code": "62701",
  "phone": "555-0000",
  "email": "info@acmeutilities.com",
  "safety_rating": "SATISFACTORY",
  "total_power_units": 45,
  "total_drivers": 60,
  "raw_fmcsa_data": {}
}
```

**Response:** `201 Created`

### Get USDOT Profile

```http
GET /api/usdot-profiles/{id}/
```

**Response:** `200 OK`

### Lookup by USDOT Number

```http
GET /api/usdot-profiles/lookup_by_usdot/?usdot=123456
```

**Response:** `200 OK` or `404 Not Found`

### Copy Profile to Customer

```http
POST /api/usdot-profiles/{id}/copy_to_customer/
```

**Body (optional):**
```json
{
  "fields": ["legal_name", "physical_address_line1", "physical_city", "physical_state"]
}
```

If no fields specified, copies all available fields.

**Response:** `200 OK`
```json
{
  "customer": { ... },
  "fields_copied": ["legal_name", "address_line1", "city", "state"]
}
```

---

## Vehicle Management

### List Vehicles

```http
GET /api/vehicles/
```

**Query Parameters:**
- `is_active` (boolean) - Filter by active status
- `customer` (uuid) - Filter by customer
- `make` (string) - Filter by make
- `year` (integer) - Filter by year
- `has_equipment` (boolean) - Filter vehicles with/without equipment
- `tags` (string) - Filter by tags (comma-separated)
- `year_min` (integer) - Filter by minimum year
- `year_max` (integer) - Filter by maximum year
- `search` (string) - Search VIN, unit number, make, model, license plate
- `ordering` (string) - Order by: unit_number, year, make, model, created_at

**Response:** `200 OK`
```json
{
  "results": [
    {
      "id": "uuid",
      "customer": "uuid",
      "customer_name": "ABC Trucking",
      "vin": "1HGCM82633A123456",
      "unit_number": "T-101",
      "year": 2020,
      "make": "Ford",
      "model": "F-350",
      "is_active": true,
      "tags": ["BUCKET_TRUCK", "INSULATED_BOOM"],
      "created_at": "2025-01-15T12:00:00Z"
    }
  ]
}
```

### Create Vehicle

```http
POST /api/vehicles/
```

**Body:**
```json
{
  "customer": "uuid",
  "vin": "1HGCM82633A123456",
  "unit_number": "T-101",
  "year": 2020,
  "make": "Ford",
  "model": "F-350",
  "license_plate": "ABC1234",
  "tags": ["BUCKET_TRUCK", "INSULATED_BOOM"],
  "notes": "Primary service truck"
}
```

**Response:** `201 Created`

### Get Vehicle Detail

```http
GET /api/vehicles/{id}/
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "customer": "uuid",
  "customer_name": "ABC Trucking",
  "vin": "1HGCM82633A123456",
  "unit_number": "T-101",
  "year": 2020,
  "make": "Ford",
  "model": "F-350",
  "license_plate": "ABC1234",
  "odometer_miles": 45000,
  "engine_hours": 2100,
  "is_active": true,
  "notes": "Primary service truck",
  "tags": ["BUCKET_TRUCK", "INSULATED_BOOM"],
  "vin_decode_data": { ... },
  "equipment_count": 2,
  "created_at": "2025-01-15T12:00:00Z",
  "updated_at": "2025-01-15T12:00:00Z"
}
```

### Update Vehicle

```http
PATCH /api/vehicles/{id}/
```

**Body:**
```json
{
  "odometer_miles": 46500,
  "notes": "Replaced tires"
}
```

**Response:** `200 OK`

### Delete Vehicle

```http
DELETE /api/vehicles/{id}/
```

**Response:** `204 No Content` (soft delete)

### Lookup by VIN

```http
GET /api/vehicles/lookup_by_vin/?vin=1HGCM82633A123456
```

**Response:** `200 OK` or `404 Not Found`

### Lookup by Unit Number

```http
GET /api/vehicles/lookup_by_unit/?unit_number=T-101&customer=uuid
```

**Response:** `200 OK` or `404 Not Found`

### Get Vehicle Equipment

```http
GET /api/vehicles/{id}/equipment/
```

**Query Parameters:**
- `is_active` (boolean) - Filter by active status

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "serial_number": "SN123456",
    "asset_number": "A-501",
    "equipment_type": "AERIAL_DEVICE",
    "manufacturer": "Terex",
    "model": "HyPower 40",
    "is_active": true
  }
]
```

### Decode VIN

```http
POST /api/vehicles/{id}/decode_vin/
```

**Response:** `200 OK` (placeholder - NHTSA integration TODO)
```json
{
  "vin": "1HGCM82633A123456",
  "decoded": false,
  "message": "VIN decode integration not yet implemented"
}
```

---

## Equipment Management

### List Equipment

```http
GET /api/equipment/
```

**Query Parameters:**
- `is_active` (boolean) - Filter by active status
- `customer` (uuid) - Filter by customer
- `equipment_type` (string) - Filter by equipment type
- `mounted_on_vehicle` (uuid) - Filter by vehicle
- `tags` (string) - Filter by tags (comma-separated)
- `mounted` (boolean) - Filter mounted/unmounted
- `has_data` (boolean) - Filter equipment with/without equipment_data
- `search` (string) - Search serial, asset number, manufacturer, model
- `ordering` (string) - Order by: asset_number, serial_number, equipment_type, created_at

**Response:** `200 OK`
```json
{
  "results": [
    {
      "id": "uuid",
      "customer": "uuid",
      "customer_name": "ABC Trucking",
      "serial_number": "SN123456",
      "asset_number": "A-501",
      "equipment_type": "AERIAL_DEVICE",
      "manufacturer": "Terex",
      "model": "HyPower 40",
      "mounted_on_vehicle": "uuid",
      "mounted_on_unit": "T-101",
      "is_active": true,
      "tags": ["AERIAL_DEVICE", "INSULATED_BOOM", "DIELECTRIC"],
      "created_at": "2025-01-15T13:00:00Z"
    }
  ]
}
```

### Create Equipment

```http
POST /api/equipment/
```

**Body:**
```json
{
  "customer": "uuid",
  "serial_number": "SN123456",
  "asset_number": "A-501",
  "equipment_type": "AERIAL_DEVICE",
  "manufacturer": "Terex",
  "model": "HyPower 40",
  "year": 2018,
  "mounted_on_vehicle": "uuid",
  "tags": ["AERIAL_DEVICE", "INSULATED_BOOM", "DIELECTRIC"],
  "equipment_data": {},
  "notes": "46kV insulated aerial device"
}
```

**Response:** `201 Created`

### Get Equipment Detail

```http
GET /api/equipment/{id}/
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "customer": "uuid",
  "customer_name": "ABC Trucking",
  "serial_number": "SN123456",
  "asset_number": "A-501",
  "equipment_type": "AERIAL_DEVICE",
  "manufacturer": "Terex",
  "model": "HyPower 40",
  "year": 2018,
  "mounted_on_vehicle": "uuid",
  "mounted_on_unit": "T-101",
  "mounted_on_vin": "1HGCM82633A123456",
  "is_active": true,
  "notes": "46kV insulated aerial device",
  "tags": ["AERIAL_DEVICE", "INSULATED_BOOM", "DIELECTRIC"],
  "equipment_data": {
    "placard": {
      "max_platform_height": 40,
      "max_working_height": 46,
      "platform_capacity": 500,
      "max_wind_speed": 28
    },
    "dielectric": {
      "insulation_rating_kv": 46,
      "last_test_date": "2024-06-15",
      "next_test_due": "2025-06-15",
      "test_certificate_number": "DT-2024-1234"
    }
  },
  "created_at": "2025-01-15T13:00:00Z",
  "updated_at": "2025-01-15T14:30:00Z"
}
```

### Update Equipment

```http
PATCH /api/equipment/{id}/
```

**Body:**
```json
{
  "notes": "Annual dielectric test completed"
}
```

**Response:** `200 OK`

### Delete Equipment

```http
DELETE /api/equipment/{id}/
```

**Response:** `204 No Content` (soft delete)

### Lookup by Serial Number

```http
GET /api/equipment/lookup_by_serial/?serial_number=SN123456
```

**Response:** `200 OK` or `404 Not Found`

### Mount Equipment

```http
POST /api/equipment/{id}/mount/
```

**Body:**
```json
{
  "vehicle_id": "uuid"
}
```

**Response:** `200 OK` (validates same customer)

### Unmount Equipment

```http
POST /api/equipment/{id}/unmount/
```

**Response:** `200 OK`

### Update Equipment Data

```http
POST /api/equipment/{id}/update_data/
```

**Body:**
```json
{
  "data_type": "placard",
  "data": {
    "max_platform_height": 40,
    "max_working_height": 46,
    "platform_capacity": 500,
    "max_wind_speed": 28
  }
}
```

**Response:** `200 OK` (returns updated equipment)

### Get Required Data Fields

```http
GET /api/equipment/{id}/required_data_fields/
```

**Response:** `200 OK`
```json
{
  "equipment_id": "uuid",
  "tags": ["AERIAL_DEVICE", "INSULATED_BOOM"],
  "required_fields": {
    "placard": {
      "max_platform_height": "number",
      "max_working_height": "number",
      "platform_capacity": "number",
      "max_wind_speed": "number"
    },
    "dielectric": {
      "insulation_rating_kv": "number",
      "last_test_date": "date",
      "next_test_due": "date",
      "test_certificate_number": "string"
    }
  },
  "current_data": { ... }
}
```

---

## VIN Decode Data Management

### List VIN Decode Data

```http
GET /api/vin-decode-data/
```

**Query Parameters:**
- `vehicle` (uuid) - Filter by vehicle
- `make` (string) - Filter by make
- `model_year` (integer) - Filter by year
- `fuel_type_primary` (string) - Filter by fuel type
- `search` (string) - Search VIN, make, model, manufacturer
- `ordering` (string) - Order by: decoded_at, model_year, make

**Response:** `200 OK`

### Get VIN Decode Detail

```http
GET /api/vin-decode-data/{id}/
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "vehicle": "uuid",
  "vehicle_unit_number": "T-101",
  "vehicle_customer_name": "ABC Trucking",
  "vin": "1HGCM82633A123456",
  "model_year": 2020,
  "make": "Ford",
  "model": "F-350 Super Duty",
  "manufacturer": "FORD MOTOR COMPANY",
  "vehicle_type": "Truck",
  "body_class": "Cab & Chassis",
  "engine_model": "Power Stroke 6.7L",
  "engine_configuration": "V",
  "engine_cylinders": 8,
  "displacement_liters": 6.7,
  "fuel_type_primary": "Diesel",
  "fuel_type_secondary": null,
  "gvwr": "Class 3: 10,001 - 14,000 lb",
  "gvwr_min_lbs": 10001,
  "gvwr_max_lbs": 14000,
  "abs": "Standard",
  "airbag_locations": "Front",
  "plant_city": "Louisville",
  "plant_state": "KY",
  "plant_country": "US",
  "error_code": "0",
  "error_text": null,
  "decoded_at": "2025-01-15T15:00:00Z",
  "raw_response": { ... },
  "created_at": "2025-01-15T15:00:00Z",
  "updated_at": "2025-01-15T15:00:00Z"
}
```

### Lookup by VIN

```http
GET /api/vin-decode-data/lookup_by_vin/?vin=1HGCM82633A123456
```

**Response:** `200 OK` or `404 Not Found`

### Decode VIN (NHTSA Integration)

```http
POST /api/vin-decode-data/decode_vin/
```

**Body:**
```json
{
  "vin": "1HGCM82633A123456",
  "vehicle_id": "uuid"
}
```

**Response:** `501 Not Implemented` (placeholder for NHTSA API integration)

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "Validation failed",
  "details": {
    "vin": ["VIN must be exactly 17 characters"]
  }
}
```

### 404 Not Found

```json
{
  "detail": "Not found."
}
```

or

```json
{
  "error": "Customer with USDOT 123456 not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Common Validation Rules

### VIN Validation
- Exactly 17 alphanumeric characters
- Cannot contain I, O, or Q
- Uppercase letters only
- Must be unique

### Serial Number Validation
- Required
- Uppercase letters and numbers
- Must be unique

### USDOT/MC Number Validation
- Alphanumeric only
- Must be unique if provided

### Email Validation
- Valid email format
- Lowercase
- Unique per customer for contacts

### Year Validation
- Minimum: 1900
- Maximum: Current year + 2

---

## Next Steps

1. **Add Authentication** - Implement JWT authentication
2. **Add Permissions** - Role-based access control
3. **Add Rate Limiting** - Protect against abuse
4. **Implement NHTSA VIN Decode** - Real VIN decoding
5. **Add Inspection Models** - InspectionRun, InspectionDefect, WorkOrder
6. **Add Webhook Support** - Event notifications

---

**Version:** 1.0
**Last Updated:** 2025-01-XX
**Base URL:** http://localhost:8100/api/
