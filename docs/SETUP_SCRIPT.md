# Setup Script Documentation

**NEW_BUILD_STARTER** includes a comprehensive setup script that automates database creation, dependency installation, migrations, and more.

---

## Quick Start

### First Time Setup
```bash
python setup.py setup
```

This will:
1. ✅ Check Python version (3.10+ required)
2. ✅ Check PostgreSQL installation
3. ✅ Create `.env` file from `.env.example`
4. ✅ Install dependencies from `requirements.txt`
5. ✅ Create PostgreSQL database
6. ✅ Run migrations
7. ✅ Prompt to create superuser
8. ✅ Collect static files

---

## Commands

### `setup` - Initial Setup
```bash
python setup.py setup
```

**Use when:** Setting up the project for the first time.

**What it does:**
- Validates Python 3.10+ is installed
- Validates PostgreSQL is installed and accessible
- Checks if running in virtual environment (warns if not)
- Creates `.env` file from `.env.example` if missing
- Updates `.env` with correct database name (`service_provider_new`)
- Installs all dependencies from `requirements.txt`
- Creates PostgreSQL database
- Runs all Django migrations
- Prompts to create superuser (interactive)
- Collects static files

**Example output:**
```
================================================================================
                         NEW_BUILD_STARTER - Initial Setup
================================================================================

ℹ Checking Python version...
✓ Python 3.14.0
ℹ Checking PostgreSQL...
✓ PostgreSQL found: psql (PostgreSQL) 15.2
✓ Running in virtual environment
ℹ Checking .env file...
✓ Created .env from .env.example
✓ Updated .env with DB_NAME=service_provider_new
ℹ Installing dependencies...
✓ Dependencies installed
ℹ Creating database 'service_provider_new'...
✓ Database 'service_provider_new' created
ℹ Running migrations...
✓ Migrations applied
ℹ Creating superuser...
Username: admin
Email: admin@example.com
Password: ********
✓ Superuser created
✓ Static files collected

================================================================================
                              Setup Complete!
================================================================================

✓ NEW_BUILD_STARTER is ready to use
ℹ Start server: python manage.py runserver 8100
ℹ Admin interface: http://localhost:8100/admin
ℹ API root: http://localhost:8100/api/
```

---

### `update` - Update Existing Installation
```bash
python setup.py update
```

**Use when:** Pulling latest code changes, updating dependencies, or applying new migrations.

**What it does:**
- Upgrades pip to latest version
- Installs/updates dependencies from `requirements.txt`
- Runs new migrations
- Collects static files
- Cleans `__pycache__` directories

**Example output:**
```
================================================================================
                          NEW_BUILD_STARTER - Update
================================================================================

ℹ Installing dependencies...
✓ Dependencies installed
ℹ Running migrations...
✓ Migrations applied
✓ Static files collected
ℹ Cleaning __pycache__ directories...
✓ Removed 23 __pycache__ directories

================================================================================
                             Update Complete!
================================================================================

✓ NEW_BUILD_STARTER is up to date
```

**Common use cases:**
- After `git pull` to get latest code
- After modifying `requirements.txt`
- After creating new migrations
- After modifying models

---

### `wipe` - Wipe Database and Migrations
```bash
python setup.py wipe
```

**Use when:** You need to start completely fresh (development only).

**What it does:**
- Drops the PostgreSQL database (all data lost!)
- Removes all migration files (except `__init__.py`)
- Cleans `__pycache__` directories

**Confirmation required:**
```
⚠ This will:
⚠   1. Drop the database (all data will be lost)
⚠   2. Remove all migration files
⚠   3. Clean __pycache__ directories

Are you sure? Type 'yes' to confirm: yes
```

**Example output:**
```
================================================================================
                      NEW_BUILD_STARTER - Wipe Database
================================================================================

⚠ This will:
⚠   1. Drop the database (all data will be lost)
⚠   2. Remove all migration files
⚠   3. Clean __pycache__ directories

Are you sure? Type 'yes' to confirm: yes
ℹ Dropping database 'service_provider_new'...
✓ Database 'service_provider_new' dropped
ℹ Cleaning migration files...
✓ Removed 12 migration files
ℹ Cleaning __pycache__ directories...
✓ Removed 23 __pycache__ directories

================================================================================
                             Wipe Complete!
================================================================================

✓ Database and migrations removed
ℹ Run 'python setup.py setup' to start fresh
```

⚠️ **WARNING:** This is destructive! Only use in development.

---

### `reset` - Full Reset (Wipe + Setup)
```bash
python setup.py reset
```

**Use when:** You want to completely reset to a fresh state.

**What it does:**
- Runs `wipe` (drops database, removes migrations)
- Runs `setup` (recreates everything from scratch)

This is equivalent to:
```bash
python setup.py wipe
python setup.py setup
```

**Confirmation required:** (same as `wipe`)

⚠️ **WARNING:** This is destructive! Only use in development.

---

### `status` - Check System Status
```bash
python setup.py status
```

**Use when:** Checking current state of the installation.

**What it shows:**
- Python version
- Virtual environment status
- PostgreSQL version
- `.env` file existence
- Database existence
- Migration status (applied/unapplied)

**Example output:**
```
================================================================================
                              System Status
================================================================================

Python Version: 3.14.0
Virtual Environment: Yes
PostgreSQL: psql (PostgreSQL) 15.2
.env file: Exists
Database (service_provider_new): Exists
Migrations: 45 applied, 0 unapplied
```

---

## Configuration

The setup script uses these default values (from `.env` file):

```bash
# Database Configuration
DB_NAME=service_provider_new
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
DJANGO_PORT=8100
```

To change these:
1. Edit `.env` file before running setup
2. Or manually edit after setup and run `python setup.py update`

---

## Requirements

### Python
- **Version:** 3.10 or higher
- **Check:** `python --version`

### PostgreSQL
- **Version:** 12 or higher
- **Check:** `psql --version`
- **Must be running:** `pg_ctl status` or check services

### Virtual Environment (Recommended)
```bash
# Create
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate
```

The setup script will warn if not in a virtual environment but will continue if you confirm.

---

## Troubleshooting

### "PostgreSQL not found or not in PATH"

**Problem:** `psql` command is not accessible.

**Solutions:**
1. Ensure PostgreSQL is installed
2. Add PostgreSQL bin directory to PATH
   - Windows: `C:\Program Files\PostgreSQL\15\bin`
   - Mac: Usually in PATH after installation
   - Linux: `sudo apt install postgresql-client`

### "Failed to create database"

**Problem:** Insufficient permissions or database already exists.

**Solutions:**
1. Run with postgres user: `sudo -u postgres python setup.py setup`
2. Create manually:
   ```bash
   psql -U postgres -c "CREATE DATABASE service_provider_new;"
   ```
3. Check if database exists: `psql -U postgres -l`

### "Connection refused" during migrations

**Problem:** PostgreSQL server is not running.

**Solutions:**
1. Start PostgreSQL:
   - Windows: Check Services app
   - Mac: `brew services start postgresql`
   - Linux: `sudo systemctl start postgresql`
2. Check status: `pg_ctl status`

### "Permission denied" errors

**Problem:** Database user lacks permissions.

**Solutions:**
1. Update `.env` with correct `DB_USER` and `DB_PASSWORD`
2. Grant permissions:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE service_provider_new TO your_user;
   ```

### "No module named 'django'"

**Problem:** Dependencies not installed or wrong Python environment.

**Solutions:**
1. Ensure virtual environment is activated
2. Run: `python -m pip install -r requirements.txt`
3. Verify Python: `which python` (should show venv path)

---

## Best Practices

### Development Workflow

**Initial Setup:**
```bash
# 1. Clone repository
git clone <repo_url>
cd NEW_BUILD_STARTER

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 3. Run setup
python setup.py setup

# 4. Start development
python manage.py runserver 8100
```

**After Pulling Changes:**
```bash
# 1. Pull latest code
git pull

# 2. Update installation
python setup.py update

# 3. Restart server
python manage.py runserver 8100
```

**When Models Change:**
```bash
# 1. Create migrations
python manage.py makemigrations

# 2. Apply migrations
python manage.py migrate

# Or use update command
python setup.py update
```

**When Things Break:**
```bash
# Nuclear option - full reset
python setup.py reset
```

### Production Deployment

⚠️ **DO NOT use `wipe` or `reset` in production!**

For production:
1. Use proper database backups
2. Run migrations carefully: `python manage.py migrate`
3. Use environment variables for sensitive data
4. Use proper static file serving (nginx, whitenoise, S3)
5. Set `DEBUG=False` in production

---

## Script Features

### ✅ Safety Features
- Requires confirmation for destructive operations (`wipe`, `reset`)
- Warns if not in virtual environment
- Validates Python version before proceeding
- Checks PostgreSQL availability before database operations
- Terminates database connections before dropping

### ✅ User-Friendly
- Colored terminal output (✓ success, ✗ error, ⚠ warning, ℹ info)
- Progress messages for all operations
- Clear error messages with solutions
- Status command to check system state

### ✅ Idempotent
- Can run `setup` multiple times safely
- Checks if database exists before creating
- Checks if `.env` exists before copying
- Updates can be run repeatedly

### ✅ Cross-Platform
- Works on Windows, Mac, and Linux
- Uses `sys.executable` for Python commands (respects virtual environment)
- Uses `Path` for filesystem operations (cross-platform paths)

---

## Files Modified by Setup Script

### Created Files
- `.env` - Environment configuration (if missing)

### Modified Files
- None directly (only through Django commands)

### Created Directories
- `staticfiles/` - Collected static files (if configured)

### Deleted Files (wipe command)
- All migration files in `apps/*/migrations/*.py` (except `__init__.py`)
- All `__pycache__` directories

---

## Environment Variables

The script reads from `.env` file:

```bash
# Required
DB_NAME=service_provider_new    # Database name
DB_USER=postgres                 # Database user
DB_PASSWORD=postgres             # Database password
DB_HOST=localhost                # Database host
DB_PORT=5432                     # Database port

# Optional
DJANGO_PORT=8100                 # Django development server port
SECRET_KEY=<random-key>          # Django secret key
DEBUG=True                       # Debug mode (False in production)
ALLOWED_HOSTS=localhost,127.0.0.1  # Allowed hosts
```

---

## Advanced Usage

### Custom Database Name
```bash
# Edit .env before setup
DB_NAME=my_custom_db

# Then run setup
python setup.py setup
```

### Non-Interactive Mode
```python
# In your deployment scripts
import subprocess

# Setup without superuser prompt
subprocess.run(["python", "setup.py", "setup"])
# Then create superuser separately
subprocess.run([
    "python", "manage.py", "createsuperuser",
    "--noinput",
    "--username=admin",
    "--email=admin@example.com"
])
```

### CI/CD Integration
```yaml
# Example GitHub Actions workflow
- name: Setup Database
  run: |
    python setup.py setup
  env:
    DB_NAME: service_provider_test
    DB_USER: postgres
    DB_PASSWORD: postgres
```

---

## Maintenance

### Keeping Setup Script Updated

When adding new Django apps:
- No changes needed (migrations run automatically)

When adding new dependencies:
- Update `requirements.txt`
- Run `python setup.py update`

When adding new environment variables:
- Update `.env.example`
- Document in this file
- Existing installations: manually add to `.env`

---

## Summary

| Command | Use Case | Destructive | Interactive |
|---------|----------|-------------|-------------|
| `setup` | First time setup | No | Yes (superuser) |
| `update` | After code changes | No | No |
| `wipe` | Clean slate (dev) | **YES** | Yes (confirmation) |
| `reset` | Full reset (dev) | **YES** | Yes (confirmation) |
| `status` | Check system | No | No |

**Golden Rule:** Use `setup` once, then use `update` for everything else (in production).
