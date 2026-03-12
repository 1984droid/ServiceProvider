# Project Structure

Clean, organized structure for NEW_BUILD_STARTER inspection and work order system.

**Last Updated:** 2026-03-12

---

## Directory Overview

```
ServiceProvider/
├── apps/                          # Django applications
│   ├── assets/                    # Vehicle and Equipment management
│   ├── customers/                 # Customer and Contact management
│   ├── inspections/               # Inspection execution and defect tracking
│   │   └── templates/
│   │       └── inspection_templates/  # Inspection templates (JSON)
│   ├── organization/              # Department and Employee management
│   └── work_orders/               # Work order management
├── config/                        # Django settings and root URLconf
├── data/                          # Structured data files
│   ├── inspection_templates/      # Backup templates (use apps/inspections/templates)
│   └── work_order_catalogs/       # Work order vocabulary and mappings (JSON)
├── docs/                          # Project documentation
├── logs/                          # Application logs
├── nginx/                         # Nginx configuration for deployment
├── scripts/                       # Management and deployment scripts
├── staticfiles/                   # Collected static files for deployment
└── tests/                         # Test suite
```

---

## Core Application Structure

### apps/assets/
Vehicle and equipment asset management.

**Models:**
- `Vehicle` - Fleet vehicles with VIN, meters, tags
- `Equipment` - Mounted equipment with serial numbers, specs
- `VINDecodeData` - NHTSA VIN decode results

**Purpose:** Track customer assets that require inspection and maintenance.

---

### apps/customers/
Customer and contact relationship management.

**Models:**
- `Customer` - Business customers with USDOT/MC numbers
- `Contact` - Customer contacts with communication preferences
- `USDOTProfile` - FMCSA safety data

**Purpose:** Manage customer relationships and contact information.

---

### apps/inspections/
Inspection execution, defect detection, and tracking.

**Models:**
- `InspectionRun` - Inspection instance with immutable audit trail
- `InspectionDefect` - Defects found during inspection with severity

**Services:**
- `TemplateService` - Load and validate inspection templates
- `DefectToWorkOrderService` - Auto-generate work orders from defects

**Templates Location:**
- `apps/inspections/templates/inspection_templates/` - Active templates used by system

**Purpose:** Execute inspections, detect defects, maintain compliance records.

---

### apps/work_orders/
Work order generation, tracking, and completion.

**Models:**
- `WorkOrder` - Service work orders with approval workflow
- `WorkOrderLine` - Line items with verb/noun/location vocabulary
- `WorkOrderDefect` - Junction linking work orders to defects

**Services:**
- `VocabularyService` - Load work order vocabulary (verbs, nouns, locations)

**Purpose:** Manage maintenance and repair work with automated defect integration.

---

### apps/organization/
Internal organization structure (departments, employees).

**Models:**
- `Department` - Service departments (Hydraulics, Electrical, etc.)
- `Employee` - Employees who perform inspections and work

**Purpose:** Assign work orders and track technician certifications.

---

## Data Directory

### data/work_order_catalogs/
Work order vocabulary and defect mapping (JSON).

**Files:**
- `verbs.json` - Work order action verbs (Repair, Replace, Inspect, etc.)
- `nouns.json` - Component/part names (Hydraulic Hose, Boom Cylinder, etc.)
- `service_locations.json` - Service areas (Boom Assembly, Chassis, etc.)
- `noun_categories.json` - Component groupings (Hydraulic, Electrical, etc.)
- `location_categories.json` - Location groupings
- `inspection_defect_to_work_order_seed_map_ansi_a92_2_2021.json` - Defect to vocabulary mapping
- `work_order_line_schema.json` - Work order line structure definition

**Purpose:**
- Standardize work order vocabulary across system
- Map inspection defects to structured work tasks
- Enable consistent reporting and analytics

**Used By:**
- `apps/work_orders/services/vocabulary_service.py`
- `apps/inspections/services/defect_to_work_order_service.py`

---

### data/inspection_templates/ (Backup)
Backup copy of inspection templates. **Active templates are in `apps/inspections/templates/inspection_templates/`**.

**Purpose:**
- Backup and version control for templates
- Template development and testing

---

## Documentation Directory

### docs/
Complete project documentation.

**Files:**
- `README.md` - Project overview and quick start
- `API_REFERENCE.md` - Complete API documentation
- `USER_WORKFLOWS.md` - User workflow guides (11 workflows)
- `ADMIN_GUIDE.md` - Admin interface documentation
- `PERFORMANCE_OPTIMIZATION.md` - Performance optimization guide
- `DEPLOYMENT.md` - Deployment instructions
- `DATA_CONTRACT.md` - Data structure contracts
- `IMPLEMENTATION_PLAN.md` - Development roadmap (Phases 1-6)
- `PHASE_6_COMPLETION.md` - Phase 6 completion summary
- `PROJECT_STRUCTURE.md` - This document

---

## Configuration

### config/
Django project configuration.

**Files:**
- `settings.py` - Django settings (database, apps, middleware)
- `urls.py` - Root URL configuration
- `wsgi.py` - WSGI application entry point
- `asgi.py` - ASGI application entry point (async)

---

## Deployment

### nginx/
Nginx configuration for production deployment.

**Files:**
- `nginx.conf` - Nginx server configuration
- `ssl/` - SSL certificate location (if using HTTPS)

**Purpose:** Reverse proxy, static file serving, load balancing.

---

### scripts/
Deployment and management scripts.

**Files:**
- `deploy.sh` - Automated deployment script
- `backup.sh` - Database backup script
- `restore.sh` - Database restore script

---

## Tests

### tests/
Comprehensive test suite (154 tests).

**Structure:**
- Unit tests for models, services, signals
- Integration tests for workflows
- API endpoint tests
- End-to-end workflow tests

**Coverage:** 95%+

**Run:** `python manage.py test`

---

## Key Design Decisions

### 1. Inspection Templates Location
**Decision:** Templates stored in `apps/inspections/templates/inspection_templates/`

**Rationale:**
- Django convention: templates live with their app
- Version control alongside code
- Easy access for TemplateService
- Clear ownership

### 2. Work Order Catalogs Location
**Decision:** Catalogs stored in `data/work_order_catalogs/`

**Rationale:**
- Data-driven configuration (not code)
- Shared across multiple services
- Easy to update without code changes
- Clear separation from application logic

### 3. No Duplicate Organization App
**Decision:** Removed root-level `organization/` folder, kept only `apps/organization/`

**Rationale:**
- Eliminate confusion
- Single source of truth
- Follow Django app structure convention

### 4. No ZIP Files in Repository
**Decision:** Removed `asset_templates_v2_3.zip` and extracted folders

**Rationale:**
- Git tracks files, not compressed archives
- Easier to diff and review changes
- Faster cloning and operations
- Clearer project structure

---

## File Naming Conventions

### Python Files
- `snake_case.py` - All Python files
- `models.py` - Django models
- `views.py` - API views/viewsets
- `serializers.py` - DRF serializers
- `admin.py` - Django admin configuration
- `urls.py` - URL routing
- `services/` - Business logic services

### JSON Data Files
- `lowercase_with_underscores.json` - All JSON files
- Template files include standard/version in name
- Catalog files are descriptive (verbs.json, nouns.json)

### Documentation
- `UPPERCASE_WITH_UNDERSCORES.md` - Major documentation files
- `lowercase_with_underscores.md` - Supporting documentation

---

## Data Flow

### Inspection to Work Order Flow

```
1. Inspection Template (apps/inspections/templates/)
   ↓
2. InspectionRun (apps/inspections/models.py)
   ↓
3. Defect Detection (rule evaluation)
   ↓
4. InspectionDefect (apps/inspections/models.py)
   ↓
5. Defect Mapping (data/work_order_catalogs/inspection_defect_to_work_order_seed_map_*.json)
   ↓
6. Work Order Generation (apps/work_orders/models.py)
   ↓
7. Work Order Vocabulary (data/work_order_catalogs/verbs.json, nouns.json, service_locations.json)
   ↓
8. WorkOrder + WorkOrderLine (apps/work_orders/models.py)
   ↓
9. Work Completion
   ↓
10. Asset Meter Update (apps/assets/models.py)
```

---

## Adding New Components

### Adding New Inspection Template

1. Create JSON file in `apps/inspections/templates/inspection_templates/<standard>/`
2. Follow AF_INSPECTION_TEMPLATE schema
3. Validate with TemplateService.load_template()
4. Add to SUPPORTED_STANDARDS in TemplateService
5. Create corresponding defect mapping in `data/work_order_catalogs/`

### Adding New Work Order Vocabulary

1. Edit JSON files in `data/work_order_catalogs/`
2. Add to verbs.json, nouns.json, or service_locations.json
3. Follow existing structure (id, label, category, metadata)
4. Clear vocabulary cache: VocabularyService.load_vocabulary(force_reload=True)
5. Update defect mappings if needed

### Adding New Django App

1. Create app: `python manage.py startapp <app_name>`
2. Move to `apps/` directory
3. Add to INSTALLED_APPS in config/settings.py
4. Create models, views, serializers
5. Register URLs in config/urls.py
6. Add tests in tests/

---

## Maintenance

### Regular Tasks

**Weekly:**
- Review logs in `logs/` directory
- Check for failed inspections or work orders
- Monitor test coverage

**Monthly:**
- Update inspection templates if standards change
- Review work order vocabulary for new components
- Backup database
- Update documentation

**Quarterly:**
- Review Django and dependency versions
- Performance optimization review
- User feedback incorporation
- Security audit

---

## Troubleshooting

### Templates Not Loading
**Issue:** TemplateService cannot find templates

**Check:**
1. Templates exist in `apps/inspections/templates/inspection_templates/`
2. File permissions are correct
3. JSON syntax is valid
4. TEMPLATE_BASE_DIR setting is correct

### Vocabulary Not Loading
**Issue:** VocabularyService returns empty lists

**Check:**
1. JSON files exist in `data/work_order_catalogs/`
2. Files are not corrupted
3. _base_path is correct in VocabularyService
4. Clear cache: force_reload=True

### Work Orders Not Generating
**Issue:** Defects don't create work orders

**Check:**
1. Defect mapping exists in defect_to_work_order_seed_map_*.json
2. Vocabulary exists for verb/noun/location
3. Defect status is OPEN
4. Severity meets min_severity threshold

---

## Version History

**2026-03-12:** Project reorganization - consolidated folders, removed duplicates
**2026-03-12:** Phase 6 completion - all tests passing (154/154)
**Previous:** Phases 1-5 implementation

---

**For More Information:**
- [API Reference](API_REFERENCE.md)
- [User Workflows](USER_WORKFLOWS.md)
- [Admin Guide](ADMIN_GUIDE.md)
- [Deployment Guide](DEPLOYMENT.md)
