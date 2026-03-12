# 17 Seed Data and Demo Scenarios

Tags: seed, demo, staging, reproducible

Use seed data to:
- exercise workflows in the UI
- reproduce tricky bugs
- demo to stakeholders

The embedded seed package includes:
- seed_plan.yaml (tenants/assets/parts/locations)
- loader/reset/verify script skeletons
- repro scenarios aligned to gold standard flows

## References
- packages/seed_data_gold_standard_package_v1.zip

---

## Implementation Status - ✅ COMPLETE

### Quick Start - One Command Setup

**Single command creates entire demo environment:**

```bash
python manage.py seed_all
```

**That's it!** This command sets up everything needed for development and demos.

---

### What Gets Created

#### ✅ Tenant
- **Name**: ACME Utility Services
- **Slug**: `acme`
- **Type**: Multi-tenant enabled
- **Database**: Isolated tenant data

#### ✅ Users (all password: `demo1234`)

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `owner` | `demo1234` | OWNER | Full system access |
| `admin` | `demo1234` | MANAGER | Operations management |
| `tech` | `demo1234` | TECH | Field technician |

**Authentication**:
- All users are active and ready to login
- Password reset functionality available
- Multi-tenant context automatically applied

#### ✅ Asset Subtypes - 132 types imported from v2.2 templates

**Fleet Vehicles** (37 types):
- Service trucks, pickup trucks, bucket trucks
- Dump trucks, tandem axle trucks, tri-axle trucks
- Box trucks, flatbed trucks, stake trucks
- Tractor units (day cab, sleeper), trailers
- Specialty vehicles

**Equipment** (11 types):
- Excavators, backhoes, loaders
- Skid steers, forklifts
- Aerial lifts, scissor lifts

**Shop Equipment** (25 types):
- Lifts, hoists, jacks
- Air compressors, welders
- Diagnostic tools, test equipment

**Tools** (6 types):
- Power tools, hand tools
- Specialty tools, diagnostic scanners

**Safety Assets** (8 types):
- Fire extinguishers, first aid kits
- Safety barriers, PPE storage

**Facilities** (27 types):
- Shops, warehouses, yards
- Office buildings, storage units
- Fuel stations, wash bays

**Real Estate** (4 types):
- Land, buildings, parking lots

**IT Assets** (9 types):
- Computers, servers, network equipment
- Tablets, mobile devices

**Containers** (5 types):
- Storage containers, tool boxes
- Parts bins, waste containers

#### ✅ Sample Assets (3 demo assets)

**1. Service Truck #42**
- **Type**: Service Truck with Utility Body
- **ID**: DEMO-TRUCK-001
- **Status**: Active
- **Purpose**: Mobile service operations
- **Configured**: Ready for inspections and work orders

**2. Forklift #7**
- **Type**: Warehouse Forklift
- **ID**: DEMO-FORKLIFT-001
- **Status**: Active
- **Purpose**: Material handling operations

**3. Shop Compressor**
- **Type**: Air Compressor (Shop Equipment)
- **ID**: DEMO-COMPRESSOR-001
- **Status**: Active
- **Purpose**: Shop operations

#### ✅ Permissions
- All roles configured with appropriate permissions
- RBAC (Role-Based Access Control) enforced
- Tenant-level isolation active

---

### Login Credentials

**API Endpoint**: `http://localhost:2700/api/auth/login/`

**Login Request**:
```json
{
  "username": "owner",
  "password": "demo1234"
}
```

**Available Users**:
```json
{
  "owner": {"password": "demo1234", "role": "OWNER"},
  "admin": {"password": "demo1234", "role": "MANAGER"},
  "tech": {"password": "demo1234", "role": "TECH"}
}
```

**Tenant Information**:
- Name: ACME Utility Services
- Slug: `acme`
- Tenant ID: Returned in API response after login

---

### Command Options

#### Basic Usage
```bash
# Standard seeding (everything)
python manage.py seed_all
```

#### Skip Sample Assets
If you don't want the 3 sample assets:
```bash
python manage.py seed_all --no-assets
```

#### Reset Passwords
If users already exist and you want to force reset passwords to `demo1234`:
```bash
python manage.py seed_all --reset-passwords
```

---

### After Seeding - Complete Setup

#### 1. Start the Backend
```bash
# From project root
python manage.py runserver 0.0.0.0:2700
```

**Backend runs on**: `http://localhost:2700`

#### 2. Start the Frontend
```bash
# From frontend directory
cd frontend
npm run dev
```

**Frontend runs on**: `http://localhost:5173`

#### 3. Login
- Navigate to `http://localhost:5173`
- Login with `owner / demo1234`
- Explore the demo environment

#### 4. Add Your First Asset
- Go to **Assets** → **Add Asset**
- Search for asset type (e.g., "service truck")
- Fill in the details:
  - Asset ID/Name
  - Status (Active)
  - Location
  - Notes
- For vehicles, use **VIN decoder** (if available)

#### 5. Create Work Orders
- Navigate to an asset
- Click **Create Work Order**
- Use intelligent search to find nouns
- System suggests verbs and locations
- Submit work order

#### 6. Run Inspections
- Navigate to **Inspections**
- Select inspection template (ANSI A92.2-2021 for aerial devices)
- Execute inspection with Crown Jewel v2 interface
- System auto-generates defects based on rules
- Create work orders from defects

---

### Deprecated Commands - DO NOT USE

⚠️ **These old commands are deprecated and will show warnings:**

❌ `python manage.py seed_dev_users` - Creates different users (admin/devuser)
❌ `python manage.py seed_demo_demo` - Old demo seeding (deprecated)
❌ `python manage.py seed_demo` - Older version
❌ `create_test_user.py` - Standalone script (deleted)
❌ `setup_demo.py` - Standalone script (deleted)

**Use `seed_all` instead!**

---

### Re-Seeding / Clean Start

#### Option 1: Reset Database (Nuclear Option)

**Complete fresh start:**
```bash
# Stop the server first (Ctrl+C)

# Delete database
rm db.sqlite3

# Recreate database with migrations
python manage.py migrate

# Re-seed everything
python manage.py seed_all
```

**Result**: Brand new database with fresh seed data

#### Option 2: Just Reset Passwords

**If users exist but passwords don't work:**
```bash
python manage.py seed_all --reset-passwords
```

**Result**: All user passwords reset to `demo1234`

---

### Troubleshooting

#### "User already exists" but password doesn't work

**Solution**:
```bash
python manage.py seed_all --reset-passwords
```

This resets all user passwords to `demo1234` without recreating users.

#### Asset subtypes not showing up

**Solution**:
The command should import them automatically. If not, manually import:
```bash
python manage.py import_asset_subtypes_v2 \
  asset_templates_v2_2/asset_subtypes.json \
  --tenant=acme \
  --update
```

#### Can't login with owner/demo1234

**Checklist**:
1. ✅ Check that seeding completed successfully (no errors in terminal)
2. ✅ Try resetting passwords: `python manage.py seed_all --reset-passwords`
3. ✅ Check backend is running on port 2700: `http://localhost:2700/admin`
4. ✅ Check frontend is pointing to correct API URL (check `.env` or config)
5. ✅ Check browser console for frontend errors

#### "No tenant found" error

**Solution**:
Make sure you're sending the `X-Tenant-ID` header with API requests:
```bash
curl -H "X-Tenant-ID: <tenant_id>" http://localhost:2700/api/assets/
```

The frontend handles this automatically after login.

#### Database migration errors

**Solution**:
```bash
# If migrations are out of sync
python manage.py migrate --fake-initial

# Or start fresh
rm db.sqlite3
python manage.py migrate
python manage.py seed_all
```

---

### Development vs Production

#### Development/Demo (Use seed_all)
```bash
python manage.py seed_all
```

**Perfect for**:
- Local development
- Testing
- Demos
- Proof of concepts

#### Production (Manual Setup)

**DO NOT use `seed_all` in production!** Instead:

1. **Create tenant manually** via Django admin
   - Navigate to `/admin/core_tenant/tenant/`
   - Create new tenant with real company name
   - Set slug, timezone, settings

2. **Create users with strong passwords**
   - Use Django admin or registration flow
   - Set strong passwords (not `demo1234`!)
   - Assign appropriate roles

3. **Import only needed asset subtypes**
   - Import specific types for your organization
   - Don't import all 132 types if not needed

4. **Set up proper authentication**
   - Configure OAuth2/SAML if needed
   - Enable MFA (multi-factor authentication)
   - Set password policies

5. **Configure tenant settings**
   - Tax rates
   - Business rules
   - Integration credentials (QBO, etc.)

---

### What's Next After Seeding?

**1. Login** ✅
- Use `owner / demo1234`
- Verify all features are accessible

**2. Add Real Assets** ✅
- Add assets for your organization
- Import from CSV if you have many
- Use VIN decoder for vehicles

**3. Import Inspection Templates** ✅
- Crown Jewel v2 with ANSI A92.2-2021 templates
- Custom inspection templates for your assets
- Import via management commands

**4. Create Work Orders** ✅
- Create work orders for maintenance
- Use intelligent search for nouns
- Track costs and pricing

**5. Run Inspections** ✅
- Execute inspections on assets
- System auto-generates defects
- Create work orders from defects

**6. Set Up Inventory** ✅
- Add parts to inventory system
- Configure locations (warehouses, trucks, bins)
- Set up reorder policies

**7. Configure Financial System** ✅
- Set up customer accounts
- Configure tax rates
- Set up payment terms

**8. Set Up Recurring Billing** ✅ (if using leasing)
- Create recurring billing schedules
- Configure lease charge templates
- Enable auto-issue for hands-off billing

---

### Need Different Data?

#### Customize the Seed Command

**Edit the seed command**:
```
apps/common/management/commands/seed_all.py
```

**You can customize**:
- Tenant name and slug
- User names and roles
- Sample assets (types, IDs, status)
- Default passwords (change `demo1234` to something else)

**Example Customization**:
```python
# In seed_all.py
TENANT_NAME = "Your Company Name"
TENANT_SLUG = "yourcompany"

USERS = [
    {"username": "admin", "role": "OWNER", "password": "your_password"},
    {"username": "manager", "role": "MANAGER", "password": "your_password"},
    # ... more users
]

SAMPLE_ASSETS = [
    {"name": "Truck 1", "subtype": "service_truck", "id": "TRUCK-001"},
    # ... more assets
]
```

---

### Command Reference

**Primary Command**:
```bash
python manage.py seed_all                    # Full seeding
python manage.py seed_all --no-assets       # Skip sample assets
python manage.py seed_all --reset-passwords # Reset passwords
```

**Import Commands** (Manual):
```bash
# Import asset subtypes
python manage.py import_asset_subtypes_v2 \
  asset_templates_v2_2/asset_subtypes.json \
  --tenant=acme --update

# Import work order vocabulary
python manage.py import_work_order_vocabulary_v2_3 \
  asset_templates_v2_3/work_order_vocabulary/nouns.json \
  --tenant=acme --update

# Import inspection templates (Crown Jewel v2)
python manage.py import_inspection_template_v4 \
  asset_templates_v2_4/inspections/ansi_a92_2_2021/ \
  --tenant=acme --update
```

**Utility Commands**:
```bash
# Check migrations
python manage.py showmigrations

# Create superuser (for admin access)
python manage.py createsuperuser

# Clear cache (if using Redis)
python manage.py clear_cache
```

---

### Data Structure After Seeding

**Database Tables Populated**:
- `core_tenant_tenant` - 1 tenant (ACME Utility Services)
- `users_membership` - 3 users (owner, admin, tech)
- `assets_assetsubtype` - 132 asset subtypes
- `assets_asset` - 3 sample assets (optional)
- `work_orders_nounitem` - 686 nouns (if vocabulary imported)
- `work_orders_verb` - 89 verbs (if vocabulary imported)
- `work_orders_servicelocation` - 69 service locations (if vocabulary imported)
- `inspections_inspectionprogram` - N inspection programs (if templates imported)

**File System**:
- SQLite database: `db.sqlite3`
- Media files: `media/` (if any uploads)
- Logs: `logs/` (if logging configured)

---

### Testing the Seeded Environment

#### 1. API Test (Backend)
```bash
# Test login
curl -X POST http://localhost:2700/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"owner","password":"demo1234"}'

# Test assets endpoint (requires auth token)
curl http://localhost:2700/api/assets/ \
  -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: <tenant_id>"
```

#### 2. Frontend Test
- Navigate to `http://localhost:5173`
- Login with `owner / demo1234`
- Check dashboard loads
- Navigate to Assets → Should see 3 sample assets
- Create a work order → System should show intelligent suggestions

#### 3. Admin Test
- Navigate to `http://localhost:2700/admin/`
- Login with `owner / demo1234`
- Check all models are accessible
- Verify data is populated correctly

---

### Seed Data Package Structure

**Package**: `packages/seed_data_gold_standard_package_v1.zip`

**Contents**:
```
seed_data_gold_standard_package_v1/
├── seed_plan.yaml              # Seed data configuration
├── loader.py                   # Data loader script skeleton
├── reset.py                    # Database reset script skeleton
├── verify.py                   # Data verification script
├── scenarios/
│   ├── scenario_01_basic.yaml       # Basic demo scenario
│   ├── scenario_02_inspection.yaml  # Inspection workflow
│   ├── scenario_03_work_order.yaml  # Work order creation
│   └── scenario_04_billing.yaml     # Billing workflow
└── README.md                   # Package documentation
```

**Use Cases**:
- Exercise workflows in the UI
- Reproduce tricky bugs with consistent data
- Demo to stakeholders with realistic scenarios
- Integration testing with predictable data

---

## Success Criteria

**✅ Seeding Complete**:
- [x] Single command creates entire demo environment
- [x] Tenant created (ACME Utility Services)
- [x] 3 users created with demo password
- [x] 132 asset subtypes imported
- [x] 3 sample assets created (optional)
- [x] All permissions configured
- [x] Idempotent (can re-run safely)
- [x] Password reset option available
- [x] Comprehensive documentation

**✅ Ready For**:
- Development work with realistic data
- UI/UX testing with full workflow
- Stakeholder demos with professional data
- Integration testing with predictable state

---

**Seed System Status**: ✅ **Complete & Production-Ready**
**Command**: `python manage.py seed_all`
**Documentation**: Comprehensive guide for development and production
