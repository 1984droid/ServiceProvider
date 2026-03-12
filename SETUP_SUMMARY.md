# Setup Script Summary

## Overview

NEW_BUILD_STARTER now includes a comprehensive `setup.py` script that automates all aspects of development environment setup, updates, and database management.

---

## Quick Reference

### First Time Setup
```bash
python setup.py setup
```

### After Pulling Changes
```bash
python setup.py update
```

### Check System Status
```bash
python setup.py status
```

### Reset Everything (Development Only)
```bash
python setup.py reset
```

---

## What the Setup Script Does

### ✅ `setup` Command
1. Validates Python 3.10+ installed
2. Validates PostgreSQL installed and accessible
3. Warns if not in virtual environment (optional)
4. Creates `.env` file from `.env.example`
5. Updates `.env` with correct database name (`service_provider_new`)
6. Installs all dependencies from `requirements.txt`
7. Creates PostgreSQL database
8. Runs all Django migrations
9. Prompts to create superuser (interactive)
10. Collects static files

**Result:** Fully functional development environment ready to use

### ✅ `update` Command
1. Upgrades pip to latest
2. Installs/updates dependencies
3. Runs new migrations
4. Collects static files
5. Cleans `__pycache__` directories

**Result:** Environment updated with latest code

### ✅ `wipe` Command (Requires confirmation)
1. Drops PostgreSQL database (ALL DATA LOST)
2. Removes all migration files (except `__init__.py`)
3. Cleans `__pycache__` directories

**Result:** Clean slate for fresh start

### ✅ `reset` Command (Requires confirmation)
Runs `wipe` then `setup` (full reset)

**Result:** Completely fresh installation

### ✅ `status` Command
Shows:
- Python version
- Virtual environment status
- PostgreSQL version
- `.env` file existence
- Database existence
- Migration status (applied/unapplied)

**Result:** System health check

---

## Features

### 🎨 User-Friendly Output
- ✓ Green checkmarks for success
- ✗ Red X for errors
- ⚠ Yellow warnings
- ℹ Blue info messages
- Clear progress indicators

### 🛡️ Safety Features
- Requires confirmation for destructive operations
- Validates prerequisites before proceeding
- Terminates database connections before dropping
- Warns if not in virtual environment
- Idempotent (can run multiple times safely)

### 🖥️ Cross-Platform
- Works on Windows, Mac, and Linux
- Uses `sys.executable` (respects virtual environment)
- Uses `Path` for filesystem operations
- Shell commands work cross-platform

---

## Configuration

Default settings (from `.env`):

```bash
DB_NAME=service_provider_new
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DJANGO_PORT=8100
```

To customize:
1. Edit `.env` before running setup
2. Or edit after setup and run `python setup.py update`

---

## Requirements

**Python:**
- Version 3.10 or higher
- Check: `python --version`

**PostgreSQL:**
- Version 12 or higher
- Check: `psql --version`
- Must be running

**Virtual Environment (Recommended):**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux
```

---

## Common Workflows

### Initial Setup
```bash
# 1. Clone repository
git clone <repo_url>
cd NEW_BUILD_STARTER

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Run setup
python setup.py setup

# 4. Start server
python manage.py runserver 8100
```

### After Pulling Changes
```bash
git pull
python setup.py update
python manage.py runserver 8100
```

### When Things Break
```bash
python setup.py reset  # Nuclear option
```

### Checking System Health
```bash
python setup.py status
```

---

## Documentation

**Complete documentation:** [docs/SETUP_SCRIPT.md](docs/SETUP_SCRIPT.md)

Includes:
- Detailed command reference
- Troubleshooting guide
- Best practices
- Advanced usage
- CI/CD integration examples

---

## Files Created/Modified

### Created by Setup Script
- `.env` (if missing)

### Modified by Setup Script
- None directly (only through Django commands)

### Deleted by Wipe Command
- PostgreSQL database (all data)
- All migration files (except `__init__.py`)
- All `__pycache__` directories

---

## Safety Notes

⚠️ **NEVER use `wipe` or `reset` in production!**

These commands are for development only:
- `python setup.py wipe`
- `python setup.py reset`

They DESTROY all data in the database!

For production:
- Use proper database backups
- Run migrations carefully
- Use environment variables for sensitive data

---

## Script Location

**File:** `setup.py` (project root)

**Source:** Self-contained Python script with no external dependencies (uses stdlib only)

**Lines of Code:** ~650 lines

**Maintainable:** Easy to update as project grows

---

## What Makes This Setup Script Great

### 1. **Self-Documenting**
- Clear docstrings and comments
- Help text built into the script
- Colored output explains what's happening

### 2. **Safe by Default**
- Validates prerequisites first
- Requires confirmation for destructive operations
- Warns before potentially dangerous actions

### 3. **Developer-Friendly**
- One command setup (`python setup.py setup`)
- Clear error messages with solutions
- Status command to check health

### 4. **Maintainable**
- Self-contained (no external dependencies)
- Easy to extend with new commands
- Cross-platform compatible

### 5. **Production-Ready Path**
- Same script for dev and CI/CD
- Environment variable driven
- Non-interactive mode support

---

## Comparison with Manual Setup

| Task | Manual | With setup.py |
|------|--------|---------------|
| Initial setup | 10+ commands, 15 minutes | 1 command, 2 minutes |
| Update after git pull | 3-5 commands | 1 command |
| Database reset | 5+ commands | 1 command |
| Check system health | Multiple commands | 1 command |
| Error-prone? | Yes (easy to skip steps) | No (automated) |
| Documentation needed? | Yes (must refer to docs) | Minimal (self-documenting) |

---

## Future Enhancements (Possible)

- [ ] Docker support (`python setup.py docker`)
- [ ] Test data seeding (`python setup.py seed`)
- [ ] Backup/restore (`python setup.py backup`)
- [ ] Environment switching (`python setup.py switch prod`)
- [ ] Health checks (`python setup.py check`)

---

## Success Criteria

After running `python setup.py setup`, you should be able to:

1. ✅ Visit http://localhost:8100/admin
2. ✅ Log in with your superuser credentials
3. ✅ See all models in admin (Company, Department, Employee, Customer, Contact, Vehicle, Equipment, InspectionRun, WorkOrder)
4. ✅ Create test data through admin
5. ✅ Run `python manage.py test` successfully

---

## Conclusion

The setup script eliminates the pain of manual environment setup and provides a consistent, repeatable way to set up, update, and manage NEW_BUILD_STARTER.

**One command to rule them all:** `python setup.py setup`

See [docs/SETUP_SCRIPT.md](docs/SETUP_SCRIPT.md) for complete documentation.
