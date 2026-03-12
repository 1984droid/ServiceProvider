# API Summary - ServiceProvider

Quick reference for all available API endpoints.

**Base URL:** `http://localhost:8100/api/`

**Authentication:** All endpoints require JWT Bearer token (except login/register)
**Header:** `Authorization: Bearer <access_token>`

---

## Authentication

### Login & Token Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/login/` | Login (get access + refresh tokens) | No |
| POST | `/auth/logout/` | Logout (blacklist refresh token) | Yes |
| POST | `/auth/refresh/` | Refresh tokens | No |
| GET | `/auth/me/` | Get current user profile + permissions | Yes |
| PATCH | `/auth/me/` | Update user profile | Yes |
| POST | `/auth/change-password/` | Change password | Yes |

**Login Request:**
```json
{
  "username": "john.inspector",
  "password": "SecurePass123!"
}
```

**Login Response:**
```json
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc...",
  "user": {
    "id": 1,
    "username": "john.inspector",
    "email": "john@example.com",
    "employee": {...},
    "roles": ["INSPECTOR"],
    "permissions": ["inspections.view_inspectionrun", ...]
  }
}
```

### User Management (Admin Only)

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| POST | `/auth/register/` | Create new user | Admin |
| GET | `/auth/users/` | List all users | Admin |
| GET | `/auth/users/{id}/` | Get user detail | Admin |
| PATCH | `/auth/users/{id}/` | Update user | Admin |
| DELETE | `/auth/users/{id}/` | Delete user | Admin |

### Roles & Permissions

**Available Roles:**
- `SUPER_ADMIN` - Full system access
- `ADMIN` - Manage customers, assets, organization
- `INSPECTOR` - Perform inspections
- `SERVICE_TECH` - Manage work orders
- `DISPATCHER` - Schedule work
- `CUSTOMER_SERVICE` - Manage customers
- `VIEWER` - Read-only

**Management Command:**
```bash
python manage.py create_roles  # Create/update all roles
```

---

## Organization Management

### Company

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/company/` | List companies (should only be one) |
| GET | `/company/current/` | Get current company |
| POST | `/company/` | Create company (only if none exists) |
| PATCH | `/company/{id}/` | Update company |

**Note:** Single-tenant - only one company record allowed.

### Departments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/departments/` | List all departments |
| POST | `/departments/` | Create department |
| GET | `/departments/{id}/` | Get department detail |
| PATCH | `/departments/{id}/` | Update department |
| DELETE | `/departments/{id}/` | Delete department |
| GET | `/departments/{id}/employees/` | Get all employees (base + floating) |

**Filters:** `is_active`, `allows_floating`
**Search:** `name`, `code`, `description`

### Employees

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/employees/` | List all employees |
| GET | `/employees/active/` | Get active employees only |
| POST | `/employees/` | Create employee |
| GET | `/employees/{id}/` | Get employee detail |
| PATCH | `/employees/{id}/` | Update employee |
| DELETE | `/employees/{id}/` | Delete employee |
| GET | `/employees/{id}/can_work_in/?department_id={id}` | Check department access |

**Filters:** `is_active`, `base_department`
**Search:** `employee_number`, `first_name`, `last_name`, `email`

---

## Customer Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers/` | List all customers |
| POST | `/customers/` | Create customer |
| GET | `/customers/{id}/` | Get customer detail |
| PATCH | `/customers/{id}/` | Update customer |
| DELETE | `/customers/{id}/` | Delete customer (soft) |
| POST | `/customers/{id}/set_primary_contact/` | Set primary contact |
| GET | `/customers/{id}/contacts/` | Get customer contacts |
| GET | `/customers/search_by_usdot/?usdot=123456` | Search by USDOT |

**Filters:** `is_active`, `state`, `has_usdot`, `has_mc`, `has_contacts`
**Search:** `name`, `legal_name`, `city`, `usdot_number`, `mc_number`

---

## Contact Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/contacts/` | List all contacts |
| POST | `/contacts/` | Create contact |
| GET | `/contacts/{id}/` | Get contact detail |
| PATCH | `/contacts/{id}/` | Update contact |
| DELETE | `/contacts/{id}/` | Delete contact |
| POST | `/contacts/{id}/make_primary/` | Make primary contact |

**Filters:** `is_active`, `is_automated`, `customer`, `primary`, `has_email`
**Search:** `first_name`, `last_name`, `email`, `phone`

---

## USDOT Profile Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/usdot-profiles/` | List all profiles |
| POST | `/usdot-profiles/` | Create profile |
| GET | `/usdot-profiles/{id}/` | Get profile detail |
| PATCH | `/usdot-profiles/{id}/` | Update profile |
| DELETE | `/usdot-profiles/{id}/` | Delete profile |
| GET | `/usdot-profiles/lookup_by_usdot/?usdot=123456` | Lookup by USDOT |
| POST | `/usdot-profiles/{id}/copy_to_customer/` | Copy to customer |

**Filters:** `customer`, `safety_rating`
**Search:** `usdot_number`, `mc_number`, `legal_name`, `dba_name`

---

## Vehicle Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/vehicles/` | List all vehicles |
| POST | `/vehicles/` | Create vehicle |
| GET | `/vehicles/{id}/` | Get vehicle detail |
| PATCH | `/vehicles/{id}/` | Update vehicle |
| DELETE | `/vehicles/{id}/` | Delete vehicle (soft) |
| GET | `/vehicles/lookup_by_vin/?vin=...` | Lookup by VIN |
| GET | `/vehicles/lookup_by_unit/?unit_number=...` | Lookup by unit number |
| GET | `/vehicles/{id}/equipment/` | Get mounted equipment |
| POST | `/vehicles/{id}/decode_vin/` | Decode VIN (TODO) |

**Filters:** `is_active`, `customer`, `make`, `year`, `has_equipment`, `tags`, `year_min`, `year_max`
**Search:** `vin`, `unit_number`, `make`, `model`, `license_plate`

---

## Equipment Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/equipment/` | List all equipment |
| POST | `/equipment/` | Create equipment |
| GET | `/equipment/{id}/` | Get equipment detail |
| PATCH | `/equipment/{id}/` | Update equipment |
| DELETE | `/equipment/{id}/` | Delete equipment (soft) |
| GET | `/equipment/lookup_by_serial/?serial_number=...` | Lookup by serial |
| POST | `/equipment/{id}/mount/` | Mount on vehicle |
| POST | `/equipment/{id}/unmount/` | Unmount from vehicle |
| POST | `/equipment/{id}/update_data/` | Update equipment_data |
| GET | `/equipment/{id}/required_data_fields/` | Get required fields by tags |

**Filters:** `is_active`, `customer`, `equipment_type`, `mounted_on_vehicle`, `tags`, `mounted`, `has_data`
**Search:** `serial_number`, `asset_number`, `manufacturer`, `model`

---

## VIN Decode Data Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/vin-decode-data/` | List all decode records |
| POST | `/vin-decode-data/` | Create decode record |
| GET | `/vin-decode-data/{id}/` | Get decode detail |
| PATCH | `/vin-decode-data/{id}/` | Update decode record |
| DELETE | `/vin-decode-data/{id}/` | Delete decode record |
| GET | `/vin-decode-data/lookup_by_vin/?vin=...` | Lookup by VIN |
| POST | `/vin-decode-data/decode_vin/` | Decode VIN (NHTSA - TODO) |

**Filters:** `vehicle`, `make`, `model_year`, `fuel_type_primary`
**Search:** `vin`, `make`, `model`, `manufacturer`

---

## Inspection Management

### Inspections

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inspections/` | List all inspections |
| POST | `/inspections/` | Create inspection (requires template_key) |
| GET | `/inspections/{id}/` | Get inspection detail |
| PATCH | `/inspections/{id}/` | Update inspection |
| DELETE | `/inspections/{id}/` | Delete inspection |
| POST | `/inspections/{id}/complete_step/` | Mark step as complete with data |
| POST | `/inspections/{id}/finalize/` | Finalize inspection (immutable after) |
| GET | `/inspections/{id}/next_incomplete_step/` | Get next incomplete step |
| POST | `/inspections/{id}/evaluate_rules/` | **Evaluate rules and generate defects** |
| GET | `/inspections/{id}/defects/` | **Get defects with summary statistics** |

**Filters:** `status`, `customer`, `asset_type`, `template_key`, `is_finalized`
**Search:** `template_key`, `inspector_name`, `notes`

**New in Phase 4:**
- Automated defect generation via rule evaluation
- 14 assertion types supported
- Idempotent defect creation (re-evaluation updates existing defects)

### Defects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inspections/{id}/defects/` | List defects for inspection with summary |
| POST | `/inspections/{id}/evaluate_rules/` | Generate defects from rules |

**Defect Summary Response:**
```json
{
  "count": 3,
  "defects": [...],
  "summary": {
    "total_defects": 3,
    "by_severity": {
      "CRITICAL": 1,
      "MAJOR": 1,
      "MINOR": 1,
      "ADVISORY": 0
    },
    "by_status": {
      "OPEN": 2,
      "WORK_ORDER_CREATED": 1,
      "RESOLVED": 0
    }
  }
}
```

---

## Common Features

### Pagination
All list endpoints support pagination:
```
GET /api/customers/?page=2&page_size=50
```

### Filtering
Filter by specific fields:
```
GET /api/vehicles/?is_active=true&customer={uuid}&make=Ford
```

### Search
Full-text search across relevant fields:
```
GET /api/customers/?search=acme
```

### Ordering
Sort results:
```
GET /api/customers/?ordering=name           # Ascending
GET /api/customers/?ordering=-created_at    # Descending
```

### Soft Delete
Most DELETE operations set `is_active=False`. For hard delete:
```
DELETE /api/customers/{id}/?force_delete=true
```

---

## Example Requests

### Create Customer with Initial Contact
```bash
curl -X POST http://localhost:8100/api/customers/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ABC Trucking",
    "city": "Chicago",
    "state": "IL",
    "initial_contact": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@abctrucking.com"
    }
  }'
```

### Create Vehicle
```bash
curl -X POST http://localhost:8100/api/vehicles/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "uuid",
    "vin": "1HGCM82633A123456",
    "unit_number": "T-101",
    "year": 2020,
    "make": "Ford",
    "model": "F-350",
    "tags": ["BUCKET_TRUCK"]
  }'
```

### Mount Equipment on Vehicle
```bash
curl -X POST http://localhost:8100/api/equipment/{equipment_id}/mount/ \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id": "uuid"}'
```

### Update Equipment Data
```bash
curl -X POST http://localhost:8100/api/equipment/{id}/update_data/ \
  -H "Content-Type: application/json" \
  -d '{
    "data_type": "placard",
    "data": {
      "max_platform_height": 40,
      "max_working_height": 46,
      "platform_capacity": 500
    }
  }'
```

---

## Response Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success (no body)
- `400 Bad Request` - Validation error
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `501 Not Implemented` - Feature not yet implemented

---

## Frontend Integration

### Quick Start

**Install dependencies:**
```bash
cd frontend
npm install
```

**Start dev server:**
```bash
npm run dev
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

**Seed test data:**
```bash
python manage.py seed_data
```

### API Client Setup

The frontend uses Axios with automatic JWT token management:

**Configuration:** `frontend/src/config/api.ts`
```typescript
export const API_CONFIG = {
  baseURL: '/api',  // Proxied to http://localhost:8000/api in dev
  timeout: 30000,
  tokenKeys: {
    access: 'access_token',
    refresh: 'refresh_token',
  },
};
```

**Usage Example:**
```typescript
import { authApi } from '@/api/auth.api';

// Login
const response = await authApi.login({
  username: 'admin',
  password: 'admin'
});
// Tokens automatically stored in localStorage

// Make authenticated request
const user = await authApi.getCurrentUser();
// Access token automatically injected via interceptor

// Token refresh happens automatically on 401 response
```

### Authentication Flow

1. **Login:** User submits credentials to `/api/auth/login/`
2. **Store Tokens:** Access + refresh tokens stored in localStorage
3. **Auto-Inject:** Axios interceptor adds `Authorization: Bearer <token>` to all requests
4. **Auto-Refresh:** On 401, interceptor uses refresh token to get new access token
5. **Retry:** Original request automatically retried with new token
6. **Logout:** Refresh token blacklisted via `/api/auth/logout/`

### Test Users (from seed_data)

| Username   | Password | Role             | Use Case                |
|------------|----------|------------------|-------------------------|
| admin      | admin    | ADMIN            | Full admin access       |
| inspector1 | admin    | INSPECTOR        | Create/view inspections |
| inspector2 | admin    | INSPECTOR        | Create/view inspections |
| service1   | admin    | SERVICE_TECH     | Manage work orders      |
| service2   | admin    | SERVICE_TECH     | Manage work orders      |
| support1   | admin    | CUSTOMER_SERVICE | Manage customers        |

### CORS Configuration

Django is configured to allow frontend requests:

```python
# config/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
]
CORS_ALLOW_CREDENTIALS = True
```

### API Response Format

**Success (200/201):**
```json
{
  "id": "uuid",
  "field": "value",
  ...
}
```

**List (200):**
```json
[
  { "id": "uuid", ... },
  { "id": "uuid", ... }
]
```

**Error (400):**
```json
{
  "field_name": ["Error message"],
  "non_field_errors": ["General error"]
}
```

**Error (401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Error (403):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Frontend Tech Stack

- **React 19.2.4** - Latest stable
- **Vite 8.0.0** - Build tool
- **TypeScript 5.9.3** - Type safety
- **Tailwind CSS v4.2.1** - Styling with CSS variables
- **TanStack Query v5.90+** - Server state management
- **TanStack Router v1.166+** - Type-safe routing
- **Axios** - HTTP client with interceptors
- **Zustand** - Client state management
- **Playwright** - E2E testing

**See `frontend/README.md` for complete frontend documentation.**

---

## Response Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success (no body)
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

**Version:** 2.1
**Base URL:** http://localhost:8000/api/
**Frontend:** http://localhost:5173/
**Last Updated:** March 12, 2026
