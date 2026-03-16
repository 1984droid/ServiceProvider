# Service Provider Application - Clean Build

Single-tenant service provider application for equipment inspection and work order management.

## Design Principles

**Clean and Focused:**
- Single-tenant (no multi-tenant complexity)
- Simple models with clear responsibilities
- Customer → Contact → Assets → Inspections → Work Orders flow
- No premature optimization - add complexity only when needed

**Key Models:**
- **Authentication**: JWT-based auth with role-based access control (7 roles)
- **Organization**: Company info, departments, and employees
- **Customer**: Business entity only (NO contact info)
- **Contact**: All communication details (multiple per customer)
- **Vehicle**: VIN-based assets (trucks, trailers) with tag-based routing
- **Equipment**: Serial number-based assets (aerial devices, cranes) with tag-based routing
- **Inspections**: Template-driven inspection execution with immutability
- **Work Orders**: Multi-department work order management with employee assignments

**Security:**
- All API endpoints require authentication
- JWT tokens (15-min access, 7-day refresh)
- Role-based permissions (SUPER_ADMIN, ADMIN, INSPECTOR, SERVICE_TECH, DISPATCHER, CUSTOMER_SERVICE, VIEWER)
- Object-level permissions for sensitive operations

## Quick Start

### Prerequisites
- Python 3.14+
- PostgreSQL 18+
- pip

### Automated Setup (Recommended)

**One command setup:**
```bash
python scripts/setup/setup.py setup
```

Visit: http://localhost:8100/admin

**That's it!** The setup script:
- Validates Python 3.10+ and PostgreSQL
- Creates `.env` file from `.env.example`
- Installs all dependencies from `requirements.txt`
- Creates PostgreSQL database (`service_provider_new`)
- Runs all migrations (including JWT token blacklist tables)
- Prompts to create superuser
- Creates roles and permissions
- Collects static files

**After setup, create roles:**
```bash
python manage.py create_roles
```

**Other commands:**
```bash
python scripts/setup/setup.py update    # Update after pulling changes
python scripts/setup/setup.py wipe      # Wipe database and migrations (dev only)
python scripts/setup/setup.py reset     # Full reset (wipe + setup)
python scripts/setup/setup.py status    # Check system status
```

See [docs/SETUP.md](docs/SETUP.md) for complete setup documentation.

### Manual Setup (Alternative)

See [docs/SETUP_SUMMARY.md](docs/SETUP_SUMMARY.md) for manual setup instructions.

## Project Structure

```
service-provider/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── config/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/                   # Django applications
│   ├── authentication/     # JWT auth, roles, permissions
│   │   ├── views.py         # Login, logout, refresh, me endpoints
│   │   ├── serializers.py   # User, token serializers
│   │   ├── permissions.py   # Custom permission classes
│   │   ├── urls.py
│   │   └── management/
│   │       └── commands/
│   │           └── create_roles.py  # Role creation command
│   ├── organization/       # Company, Department, Employee models
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── apps.py
│   ├── customers/          # Customer and Contact models
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── apps.py
│   ├── assets/             # Vehicle and Equipment models
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── apps.py
│   ├── inspections/        # Inspection models
│   │   ├── models.py
│   │   ├── admin.py
│   │   └── apps.py
│   └── work_orders/        # Work Order models
│       ├── models.py
│       ├── admin.py
│       └── apps.py
│
├── docs/                   # Documentation
│   ├── README.md           # Documentation index
│   ├── SETUP.md            # Development setup guide
│   ├── SETUP_SUMMARY.md    # Setup quick reference
│   ├── DEPLOYMENT.md       # Production deployment guide
│   ├── DEPLOY_QUICK_START.md  # Deployment quick reference
│   ├── DATA_CONTRACT.md    # Complete API/data specification
│   ├── API_SUMMARY.md      # API endpoint reference
│   ├── FRONTEND_ROADMAP.md # Frontend development roadmap
│   ├── ansi_standard_integration/  # ANSI standard text docs
│   │   ├── STANDARD_TEXT_INTEGRATION_SUMMARY.md
│   │   ├── STANDARD_TEXT_REFERENCE_DESIGN.md
│   │   └── STANDARD_TEXT_USAGE_EXAMPLE.md
│   └── archive/            # Historical documentation
│
├── scripts/                # Development and setup scripts
│   ├── README.md           # Scripts documentation
│   ├── setup/              # Setup and deployment scripts
│   │   ├── setup.py        # Main setup script
│   │   ├── deploy.py       # Deployment script
│   │   ├── setup_from_repo.sh/bat  # Clone and setup
│   ├── archive/            # Completed migration scripts
│   ├── extract_standard_text.py  # ANSI text extraction
│   ├── generate_sample_pdfs.py   # PDF generation testing
│   ├── reset_database.py  # Database reset utility
│   ├── setup_dev.sh/bat   # Development environment setup
│   ├── run_dev.sh/bat     # Start development server
│   ├── shell.sh/bat       # Django shell
│   ├── make_migrations.sh/bat  # Create migrations
│   └── reset_dev.sh/bat   # Reset database
│
└── static/                # Static assets and reference files
    └── inspection_references/  # ANSI standard references
        └── ansi_a92_2_2021/
            ├── ANSI A92.2-2021.docx  # Source document
            ├── standard_text.json     # Extracted excerpts
            ├── figures/               # Standard diagrams
            ├── tables/                # Standard tables
            ├── symbols/               # Equipment symbols
            └── logos/                 # ANSI/SAIA logos
```

## Models Overview

### Company
Single-tenant company information. Contains:
- Company name and DBA name
- Contact information (phone, email, fax)
- Physical address
- Business details (tax ID, business type)
- Status

**Only one company record allowed** - single-tenant enforcement.

### Department
Organizational departments. Contains:
- Department name and code (unique)
- Description and manager
- Active status and floating employee flag
- Employee count tracking

Supports base and floating employee assignments.

### Employee
Staff members with department assignments. Contains:
- Employee number (unique)
- Personal information (name, email, phone)
- Base department (required)
- Floating departments (optional M2M)
- Hire/termination dates
- Active status
- Certifications and skills (JSON)
- Optional link to User account

Employees can work in their base department plus any floating departments.

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
company
├── id (UUID, PK)
├── name
├── dba_name
├── contact fields (phone, email, fax)
├── address fields
├── business details (tax_id, business_type)
├── is_active
└── timestamps

departments
├── id (UUID, PK)
├── name (unique)
├── code (unique)
├── description
├── manager_id (FK to Employee)
├── is_active
├── allows_floating
└── timestamps

employees
├── id (UUID, PK)
├── employee_number (unique)
├── first_name, last_name
├── email, phone, mobile
├── base_department_id (FK)
├── floating_departments (M2M)
├── hire_date, termination_date
├── is_active
├── title
├── certifications (JSON)
├── skills (JSON)
├── user_id (FK to auth.User)
└── timestamps

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

## Current Status

### ✅ Phase 1: Database Foundation - COMPLETE
- Organization models (Company, Department, Employee)
- Customer and Contact models
- Vehicle and Equipment models
- InspectionRun, InspectionDefect models
- WorkOrder model foundation
- Admin interfaces
- REST API endpoints
- Test configuration
- Migrations ready

### ✅ Phase 2: Template System - COMPLETE
- JSON-based inspection template system
- Pydantic 2.x validation
- Template registry and loading
- Module and step definitions
- Field type validation (15+ types)
- See [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)

### ✅ Phase 3: Inspection Runtime - COMPLETE
- Step completion tracking
- Data collection and validation
- Completion percentage calculation
- Finalization workflow with signatures
- Template immutability via snapshot
- 267 tests passing (100%)

### ✅ Phase 4: Defect Rule Evaluation Engine - COMPLETE
- RuleEvaluator with 14 assertion types
- Path resolution (simple, nested, array indices)
- DefectGenerator with idempotent defect creation
- Severity mapping
- API endpoints: `/evaluate_rules/`, `/defects/`
- Admin UI with color-coded defects
- 92 tests passing (100%)
- See [docs/PHASE_4_COMPLETION.md](docs/PHASE_4_COMPLETION.md)

### 🔄 Phase 5: Inspection-to-Work Order Integration - IN PROGRESS
- Automated work order generation from defects
- Defect-to-task mapping using vocabulary catalog
- Work order line item construction
- Status synchronization
- See [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)

## Development Notes

**Why Organization module?**
- Company represents our organization (single-tenant)
- Department enables multi-department work order tracking
- Employee supports base + floating department assignments
- Enables proper work assignment and capacity planning

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

### Backend Tests

```bash
# Run all Django tests
python manage.py test

# Run specific app tests
python manage.py test apps.organization
python manage.py test apps.customers
python manage.py test apps.assets
python manage.py test apps.inspections
python manage.py test apps.work_orders
python manage.py test apps.authentication

# Verbose output
python manage.py test -v 2

# Test authentication system
python scripts/test_auth.py
```

### Frontend Tests

```bash
# Navigate to frontend
cd frontend

# Run E2E tests (headless)
npm run test:e2e

# Run E2E tests (UI mode for debugging)
npm run test:ui

# Run specific test file
npx playwright test e2e/auth.spec.ts

# Show test report
npx playwright show-report
```

### Seed Test Data

```bash
# Create realistic test data
python manage.py seed_data

# Clear and reseed
python manage.py seed_data --clear
```

**Creates:**
- 1 Company, 4 Departments, 6 Employees
- 6 Users (all password: `admin`)
  - admin (ADMIN)
  - inspector1, inspector2 (INSPECTOR)
  - service1, service2 (SERVICE_TECH)
  - support1 (CUSTOMER_SERVICE)
- 3 Customers with contacts
- Multiple Vehicles, Trailers, Equipment

## Frontend Development

### ⚠️ HARD RULES - Port Configuration

**NON-NEGOTIABLE PORT REQUIREMENTS:**
- **Backend MUST run on port 8001** (no exceptions)
- **Frontend MUST run on port 5174** (no exceptions)

These ports are enforced by `strictPort: true` in vite.config.ts. If the ports are unavailable, servers will fail to start.

### Quick Start

```bash
# 1. Check ports are available (REQUIRED)
node scripts/check-ports.js

# 2. Start backend on port 8001
python manage.py runserver 8001

# 3. Start frontend on port 5174
cd frontend
npm install
npm run dev

# Access:
# Frontend: http://localhost:5174
# Backend API: http://localhost:8001/api
```

### Frontend Structure

```
frontend/
├── src/
│   ├── api/              # API clients (auth, customers, etc.)
│   ├── components/       # Reusable components (atomic design)
│   ├── features/         # Feature modules
│   ├── hooks/            # Custom React hooks (useAuth, etc.)
│   ├── store/            # Zustand stores (auth state)
│   ├── lib/              # Utilities (axios, queryClient)
│   ├── config/           # Config (API endpoints, theme)
│   └── styles/           # Global styles + themes
└── e2e/                  # Playwright tests
```

### Tech Stack

- **React 19.2.4** - Latest stable with new features
- **Vite 8.0.0** - Ultra-fast build tool
- **TypeScript 5.9.3** - Full type safety
- **Tailwind CSS v4.2.1** - Utility-first CSS with theming
- **TanStack Query v5.90+** - Server state management
- **TanStack Router v1.166+** - Type-safe routing
- **Axios** - HTTP client with JWT interceptors
- **Zustand** - Client state management
- **Playwright** - E2E testing

### Key Features

✅ JWT authentication with auto-refresh
✅ Runtime theme switching (default/dark)
✅ Component reusability (atomic design)
✅ Type-safe API layer
✅ No hardcoded data (all from API)
✅ E2E testing with Playwright

**See `frontend/README.md` for complete frontend documentation.**

## Production Deployment

See `DEPLOYMENT.md` for production deployment instructions.

**Backend considerations:**
- Set DEBUG=False
- Use strong SECRET_KEY
- Configure ALLOWED_HOSTS
- Use PostgreSQL (not SQLite)
- Set up proper logging
- Configure static file serving
- Use gunicorn/uwsgi
- Set up nginx reverse proxy

**Frontend considerations:**
- Build for production: `npm run build`
- Serve from `frontend/dist/`
- Configure environment variables
- Set up CDN for static assets
- Enable compression (gzip/brotli)
- Configure caching headers

---

**This is a clean slate. Build thoughtfully. Add complexity only when needed.**
