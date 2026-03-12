# Development Scripts Guide

Quick reference for all development helper scripts.

---

## Initial Setup

### `generate_env.py` / `generate_env.sh` / `generate_env.bat`

**What it does:**
- Generates `.env` file from `.env.example`
- Creates cryptographically secure Django SECRET_KEY (50 characters)
- Generates strong random database password (32 characters)
- Preserves all other settings from .env.example

**When to use:**
- First time setup (auto-called by `setup_dev.sh`)
- Regenerating credentials after security incident
- Setting up new environment (staging, production)

**Usage:**

**Any platform:**
```bash
python generate_env.py
```

**Or with wrapper:**
```bash
./generate_env.sh  # Linux/Mac
generate_env.bat   # Windows
```

**Safety:** Prompts for confirmation if .env already exists

---

### `setup_dev.sh` / `setup_dev.bat`

**What it does:**
- Creates Python virtual environment (`.venv`)
- Installs all dependencies from `requirements.txt`
- **Auto-generates `.env` with secure random values** (if not exists)
- Creates PostgreSQL database
- Runs initial migrations
- Creates logs directory

**When to use:** First time setting up the project on a new machine

**Usage:**

**Linux/Mac:**
```bash
chmod +x setup_dev.sh
./setup_dev.sh
```

**Windows:**
```cmd
setup_dev.bat
```

**After running:**
```bash
python manage.py createsuperuser
./run_dev.sh  # or run_dev.bat on Windows
```

---

## Daily Development

### `run_dev.sh` / `run_dev.bat`

**What it does:**
- Activates virtual environment
- Starts Django development server on port 8000

**When to use:** Every time you want to run the dev server

**Usage:**

**Linux/Mac:**
```bash
./run_dev.sh
```

**Windows:**
```cmd
run_dev.bat
```

**Shortcut:** Press `Ctrl+C` to stop

---

## Model Changes

### `make_migrations.sh` / `make_migrations.bat`

**What it does:**
- Detects model changes
- Creates migration files
- Optionally applies migrations immediately
- Reminds you to review migrations before committing

**When to use:** After changing any model in `apps/*/models.py`

**Usage:**

**Linux/Mac:**
```bash
./make_migrations.sh
```

**Windows:**
```cmd
make_migrations.bat
```

**Example workflow:**
```bash
# 1. Edit models
vim apps/customers/models.py

# 2. Create migrations
./make_migrations.sh
# Review: apps/customers/migrations/0002_customer_add_field.py

# 3. Apply (if you said 'n' to auto-apply)
python manage.py migrate

# 4. Commit
git add apps/customers/models.py apps/customers/migrations/
git commit -m "Add new_field to Customer model"
```

---

## Database Reset

### `reset_dev.sh` / `reset_dev.bat`

**⚠️ DESTRUCTIVE - Development only!**

**What it does:**
- Drops entire database
- Recreates fresh database
- Runs all migrations from scratch
- **DELETES ALL DATA**

**When to use:**
- Database is corrupted
- Want to start fresh with clean schema
- Testing migrations from scratch
- After pulling major schema changes

**Usage:**

**Linux/Mac:**
```bash
./reset_dev.sh
```

**Windows:**
```cmd
reset_dev.bat
```

**After reset:**
```bash
python manage.py createsuperuser
# Load fixtures if you have them
python manage.py loaddata fixtures/customers.json
```

**⚠️ DO NOT USE IN PRODUCTION!**

---

## Django Shell

### `shell.sh` / `shell.bat`

**What it does:**
- Activates virtual environment
- Opens Django shell (iPython if available)

**When to use:**
- Testing queries
- Debugging
- Data exploration
- Manual data fixes

**Usage:**

**Linux/Mac:**
```bash
./shell.sh
```

**Windows:**
```cmd
shell.bat
```

**Example session:**
```python
>>> from apps.customers.models import Customer
>>> customers = Customer.objects.all()
>>> customers.count()
5
>>> c = Customer.objects.first()
>>> c.name
'ABC Trucking'
>>> c.primary_contact
<Contact: John Doe>
```

---

## Script Permissions (Linux/Mac)

After copying NEW_BUILD_STARTER, make scripts executable:

```bash
chmod +x setup_dev.sh
chmod +x reset_dev.sh
chmod +x run_dev.sh
chmod +x make_migrations.sh
chmod +x shell.sh
```

Or all at once:
```bash
chmod +x *.sh
```

---

## Typical Development Workflow

### First Day Setup
```bash
# 1. Copy project to new location
cp -r NEW_BUILD_STARTER ~/projects/ServiceProvider
cd ~/projects/ServiceProvider

# 2. Make scripts executable (Linux/Mac only)
chmod +x *.sh

# 3. Run setup
./setup_dev.sh

# 4. Create admin user
python manage.py createsuperuser

# 5. Start server
./run_dev.sh

# 6. Visit http://localhost:8000/admin
```

### Daily Development
```bash
# Start working
cd ~/projects/ServiceProvider
./run_dev.sh

# In another terminal: make model changes
vim apps/customers/models.py
./make_migrations.sh

# Test in shell
./shell.sh
>>> from apps.customers.models import Customer
>>> Customer.objects.create(name="Test")

# All good? Commit
git add .
git commit -m "Add new feature"
```

### After Pulling Major Changes
```bash
git pull

# If migrations were added:
python manage.py migrate

# If there are conflicts or issues:
./reset_dev.sh  # Nuclear option
python manage.py createsuperuser
```

---

## Troubleshooting

### "Permission denied" on Linux/Mac
```bash
chmod +x script_name.sh
```

### "Virtual environment not found"
```bash
./setup_dev.sh  # Creates .venv
```

### "Database does not exist"
```bash
# Check .env file has correct database name
cat .env | grep DB_NAME

# Create database manually:
createdb service_provider

# Or run setup again:
./setup_dev.sh
```

### "Module not found" errors
```bash
# Activate venv and reinstall
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Database is corrupted
```bash
./reset_dev.sh  # Start fresh
```

---

## Advanced: Custom Management Commands

**Create custom command:**
```bash
mkdir -p apps/customers/management/commands
touch apps/customers/management/commands/__init__.py
```

**Example:** `apps/customers/management/commands/import_customers.py`
```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Import customers from CSV'

    def handle(self, *args, **options):
        self.stdout.write('Importing customers...')
        # Your import logic here
        self.stdout.write(self.style.SUCCESS('Done!'))
```

**Run:**
```bash
python manage.py import_customers
```

---

## Quick Reference

| Task | Command |
|------|---------|
| First setup | `./setup_dev.sh` or `setup_dev.bat` |
| Start server | `./run_dev.sh` or `run_dev.bat` |
| Make migrations | `./make_migrations.sh` or `make_migrations.bat` |
| Reset database | `./reset_dev.sh` or `reset_dev.bat` |
| Django shell | `./shell.sh` or `shell.bat` |
| Create superuser | `python manage.py createsuperuser` |
| Run tests | `python manage.py test` |
| Collect static | `python manage.py collectstatic` |

---

**These scripts are for DEVELOPMENT only. Do not use in production.**
