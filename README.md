# Service Provider Application - Clean Build

Single-tenant service provider application for equipment inspection and work order management.

## Design Principles

**Clean and Focused:**
- Single-tenant (no multi-tenant complexity)
- Simple models with clear responsibilities
- Customer → Contact → Assets → Inspections → Work Orders flow
- No premature optimization - add complexity only when needed

**Key Models:**
- **Customer**: Business entity only (NO contact info)
- **Contact**: All communication details (multiple per customer)
- **Vehicle**: VIN-based assets (trucks, trailers)
- **Equipment**: Serial number-based assets (aerial devices, cranes)

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- pip

### Installation

1. **Clone and setup virtual environment:**
```bash
cd NEW_BUILD_STARTER
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Create database:**
```bash
# Using psql
psql -U postgres -c "CREATE DATABASE service_provider;"
```

5. **Run migrations:**
```bash
python manage.py migrate
```

6. **Create superuser:**
```bash
python manage.py createsuperuser
```

7. **Run development server:**
```bash
python manage.py runserver
```

Visit: http://localhost:8000/admin

## Project Structure

```
NEW_BUILD_STARTER/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── config/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── apps/
    ├── customers/          # Customer and Contact models
    │   ├── models.py
    │   ├── admin.py
    │   ├── serializers.py
    │   └── views.py
    └── assets/             # Vehicle and Equipment models
        ├── models.py
        ├── admin.py
        ├── serializers.py
        └── views.py
```

## Models Overview

### Customer
Business entity we service. Contains:
- Business name and legal name
- Physical address
- Regulatory identifiers (USDOT, MC numbers)
- Status and notes

**NO contact information** - use Contact model instead.

### Contact
Person at customer organization. Contains:
- Name and title
- Email, phone, mobile
- Correspondence preferences (invoices, estimates, service updates, inspection reports)
- Primary contact flag

Multiple contacts per customer with role-based routing.

### Vehicle
VIN-based asset. Contains:
- VIN (unique identifier)
- Unit number (customer's internal number)
- Year/make/model
- Odometer and engine hours
- VIN decode data (from NHTSA API)

### Equipment
Serial number-based asset. Contains:
- Serial number (unique identifier)
- Asset number (customer's internal number)
- Equipment type, manufacturer, model
- Engine hours and cycles
- Optional relationship to Vehicle (for mounted equipment)

## Database Schema

```
customers
├── id (UUID, PK)
├── name
├── legal_name
├── address fields
├── usdot_number
├── mc_number
├── is_active
└── timestamps

contacts
├── id (UUID, PK)
├── customer_id (FK)
├── first_name, last_name, title
├── email, phone, mobile
├── correspondence preferences
├── is_primary
└── timestamps

vehicles
├── id (UUID, PK)
├── customer_id (FK)
├── vin (unique)
├── unit_number
├── year, make, model, vehicle_type
├── odometer_miles, engine_hours
├── vin_decode_data (JSON)
└── timestamps

equipment
├── id (UUID, PK)
├── customer_id (FK)
├── serial_number (unique)
├── asset_number
├── equipment_type, manufacturer, model
├── engine_hours, cycles
├── mounted_on_vehicle_id (FK, nullable)
└── timestamps
```

## Next Steps

### Phase 2: API Development
- REST API endpoints for CRUD operations
- JWT authentication
- API documentation

### Phase 3: Inspections
- Port inspection engine from previous build
- InspectionTemplate, InspectionRun, InspectionDefect models
- Link to Vehicle/Equipment

### Phase 4: Work Orders
- WorkOrder model
- Inspection → Work Order flow
- Defect → Work Order conversion

## Development Notes

**Why separate Customer and Contact?**
- Customer represents the business entity
- Contact represents people with specific communication preferences
- Allows proper routing: invoices to billing contact, service updates to maintenance contact
- Supports multiple contacts per customer with different roles

**Why separate Vehicle and Equipment?**
- Different identification schemes (VIN vs Serial Number)
- Different regulatory requirements
- Different inspection standards
- Clearer data model than polymorphic Asset

**Why UUID primary keys?**
- Prevents ID enumeration attacks
- Distributed-system friendly
- No sequential ID leakage
- URL-safe

**Why no tenant_root?**
- Single-tenant application
- Simpler queries, faster performance
- Easier migrations
- Less cognitive overhead

## Database Management

**Reset database (development only):**
```bash
# Drop and recreate
psql -U postgres -c "DROP DATABASE IF EXISTS service_provider;"
psql -U postgres -c "CREATE DATABASE service_provider;"
python manage.py migrate
python manage.py createsuperuser
```

**Create migration after model changes:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Shell access:**
```bash
python manage.py shell
```

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.customers
python manage.py test apps.assets

# Verbose output
python manage.py test -v 2
```

## Production Deployment

See `DEPLOYMENT.md` (to be created) for production deployment instructions.

Key considerations:
- Set DEBUG=False
- Use strong SECRET_KEY
- Configure ALLOWED_HOSTS
- Use PostgreSQL (not SQLite)
- Set up proper logging
- Configure static file serving
- Use gunicorn/uwsgi
- Set up nginx reverse proxy

---

**This is a clean slate. Build thoughtfully. Add complexity only when needed.**
