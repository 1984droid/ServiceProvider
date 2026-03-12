# Quick Start Guide

Get up and running in 5 minutes.

## 1. Create Virtual Environment

```bash
cd NEW_BUILD_STARTER
python -m venv .venv
```

**Activate it:**
- Windows: `.venv\Scripts\activate`
- Mac/Linux: `source .venv/bin/activate`

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your database credentials (or leave defaults for local PostgreSQL).

## 4. Create Database

```bash
# Using psql
psql -U postgres -c "CREATE DATABASE service_provider_new;"

# Or using pgAdmin - create database named: service_provider_new
```

## 5. Run Migrations

```bash
python manage.py migrate
```

You should see:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying customers.0001_initial... OK
  Applying assets.0001_initial... OK
  ...
```

## 6. Create Superuser

```bash
python manage.py createsuperuser
```

Enter username, email, and password when prompted.

## 7. Run Server

```bash
python manage.py runserver 8100
```

Visit: http://localhost:8100/admin

Login with your superuser credentials.

**Note:** NEW_BUILD_STARTER uses port **8100** to avoid conflicts with the legacy application on port 8000.

## What You Have Now

✅ Clean Django 6.0 project (single-tenant)
✅ Customer and Contact models
✅ Vehicle and Equipment models
✅ PostgreSQL database
✅ Admin interface
✅ REST Framework setup

## Next Steps

### Add Some Data

In the admin interface:

1. **Create a Customer**
   - Name: "ABC Trucking"
   - Address info
   - USDOT/MC numbers (optional)

2. **Add Contacts**
   - Billing contact (receives invoices)
   - Maintenance contact (receives service updates)
   - Mark one as primary

3. **Add Vehicles**
   - Enter VIN
   - Unit number
   - Year/Make/Model

4. **Add Equipment**
   - Serial number
   - Asset number
   - Equipment type
   - Optionally link to a vehicle

### Explore the Code

**Models are in:**
- `apps/customers/models.py` - Customer, Contact
- `apps/assets/models.py` - Vehicle, Equipment

**Admin is in:**
- `apps/customers/admin.py`
- `apps/assets/admin.py`

**Settings are in:**
- `config/settings.py`

### Development Workflow

**Make model changes:**
```bash
# 1. Edit models.py
# 2. Create migration
python manage.py makemigrations

# 3. Apply migration
python manage.py migrate
```

**Reset database (development only):**
```bash
psql -U postgres -c "DROP DATABASE service_provider_new;"
psql -U postgres -c "CREATE DATABASE service_provider_new;"
python manage.py migrate
python manage.py createsuperuser
```

**Django shell:**
```bash
python manage.py shell
```

## Troubleshooting

**Can't connect to database:**
- Check PostgreSQL is running
- Verify credentials in `.env`
- Ensure database exists

**Import errors:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Port already in use:**
```bash
# NEW_BUILD_STARTER uses port 8100 by default
# If 8100 is in use, try another port:
python manage.py runserver 8101
```

---

**You're all set! Start building.**
