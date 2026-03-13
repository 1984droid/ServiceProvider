# ServiceProvider - Development Environment Setup

Complete guide for setting up the ServiceProvider application from a fresh git clone.

## Quick Start (Automated Setup)

### Linux/macOS

```bash
git clone <repository-url>
cd ServiceProvider
chmod +x setup_from_repo.sh
./setup_from_repo.sh
```

### Windows

```cmd
git clone <repository-url>
cd ServiceProvider

REM First, set up PostgreSQL user and database
scripts\setup_postgres_user.bat

REM Then run the main setup
setup_from_repo.bat
```

**Note:** The `setup_postgres_user.bat` script creates a dedicated database user (`service_provider_user`) with a known password (`dev_password_123`). This requires the PostgreSQL superuser password.

The automated setup script will:
1. Check all prerequisites
2. Create Python virtual environment
3. Install all dependencies (Python + Node.js)
4. Configure environment variables from `.env.dev`
5. Set up PostgreSQL database (or skip if not accessible)
6. Run migrations
7. Seed sample data
8. Prepare frontend

## Prerequisites

### Required Software

- **Python 3.14+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 18+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/downloads/)

### Verify Installation

```bash
python --version  # Should be 3.14 or higher
node --version    # Should be 18 or higher
npm --version     # Should come with Node.js
psql --version    # PostgreSQL client
```

## Manual Setup

If you prefer to set up manually or troubleshoot issues:

### 1. Clone Repository

```bash
git clone <repository-url>
cd ServiceProvider
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy dev environment file
cp .env.dev .env

# Edit .env and adjust settings if needed
# Especially database credentials and ports
```

### Environment Variables (.env)

```ini
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL 18+)
DB_NAME=service_provider_new
DB_USER=postgres
DB_PASSWORD=workAccount90!
DB_HOST=localhost
DB_PORT=8101
DJANGO_PORT=8100

# FMCSA API Key (for VIN decoding)
FMCSA_WEBKEY=85e35bc9a0e9c3290cc3ea8f2a973f54b013c1b0
```

### 4. Set Up PostgreSQL Database

#### Option A: Using psql command line

```bash
# Connect to PostgreSQL
psql -U postgres -h localhost -p 8101

# Create database
CREATE DATABASE service_provider_new;

# Exit
\q
```

#### Option B: Using pgAdmin

1. Open pgAdmin
2. Connect to your PostgreSQL server
3. Right-click "Databases" → "Create" → "Database"
4. Name: `service_provider_new`
5. Click "Save"

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Seed Sample Data

```bash
python manage.py seed_data
```

This creates:
- Admin user: `admin@example.com` / `admin123`
- Inspector user: `inspector@example.com` / `inspector123`
- Sample customers, vehicles, equipment
- Sample inspection templates

### 7. Set Up Frontend

```bash
cd frontend
npm install
cd ..
```

### 8. Create Logs Directory

```bash
mkdir logs
```

## Running the Application

### Start Backend (Django)

```bash
# Make sure virtual environment is activated
python manage.py runserver 8100
```

Backend will be available at: http://localhost:8100

### Start Frontend (React + Vite)

In a **separate terminal**:

```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

## Access Points

- **Frontend Application**: http://localhost:5173
- **Backend API**: http://localhost:8100/api/
- **Admin Panel**: http://localhost:8100/admin
- **API Documentation**: http://localhost:8100/api/docs (if enabled)

## Default Credentials

Created by `seed_data` command:

| Role | Email | Password | Permissions |
|------|-------|----------|-------------|
| Admin | admin@example.com | admin123 | Full access |
| Inspector | inspector@example.com | inspector123 | Inspection permissions |

## Development Workflow

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_models.py

# With coverage
pytest --cov=apps

# Verbose output
pytest -v
```

### Database Management

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (WARNING: Deletes all data!)
./scripts/reset_dev.sh  # Linux/macOS
scripts\reset_dev.bat   # Windows

# Django shell
python manage.py shell
```

### Code Quality

```bash
# Run linting (if configured)
flake8

# Format code (if configured)
black .

# Type checking (if configured)
mypy apps/
```

## Project Structure

```
ServiceProvider/
├── apps/                          # Django applications
│   ├── assets/                    # Vehicles & Equipment
│   ├── customers/                 # Customer management
│   ├── inspections/               # Inspection templates & execution
│   ├── organization/              # Users, roles, permissions
│   └── work_orders/               # Work order management
├── config/                        # Django settings
├── frontend/                      # React + TypeScript frontend
│   ├── src/
│   │   ├── api/                   # API client
│   │   ├── components/            # Reusable components
│   │   ├── features/              # Feature modules
│   │   └── ...
│   └── package.json
├── scripts/                       # Utility scripts
├── tests/                         # Test files
├── .env.dev                       # Development environment template
├── requirements.txt               # Python dependencies
├── manage.py                      # Django management
└── setup_from_repo.sh/.bat        # Automated setup scripts
```

## Common Issues & Solutions

### Issue: PostgreSQL Connection Failed

**Symptoms**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
1. Verify PostgreSQL is running:
   ```bash
   # Linux
   sudo systemctl status postgresql

   # macOS
   brew services list

   # Windows
   # Check Services app for "postgresql-x64-xx"
   ```

2. Check connection settings in `.env`:
   - `DB_HOST` (usually `localhost`)
   - `DB_PORT` (default `5432`, yours is `8101`)
   - `DB_USER` and `DB_PASSWORD`

3. Test connection:
   ```bash
   psql -h localhost -p 8101 -U postgres -d service_provider_new
   ```

### Issue: Port Already in Use

**Symptoms**: `Error: That port is already in use`

**Solutions**:
1. Change `DJANGO_PORT` in `.env`
2. Or kill process using the port:
   ```bash
   # Linux/macOS
   lsof -ti:8100 | xargs kill -9

   # Windows
   netstat -ano | findstr :8100
   taskkill /PID <PID> /F
   ```

### Issue: Migration Errors

**Symptoms**: `django.db.migrations.exceptions.InconsistentMigrationHistory`

**Solutions**:
1. Reset database:
   ```bash
   ./scripts/reset_dev.sh  # Linux/macOS
   scripts\reset_dev.bat   # Windows
   ```

2. Or manually:
   ```bash
   python manage.py migrate --fake-initial
   ```

### Issue: Frontend Build Errors

**Symptoms**: `Module not found` or TypeScript errors

**Solutions**:
1. Delete node_modules and reinstall:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json  # Linux/macOS
   # or
   rmdir /s /q node_modules && del package-lock.json  # Windows

   npm install
   ```

2. Clear Vite cache:
   ```bash
   rm -rf node_modules/.vite  # Linux/macOS
   rmdir /s /q node_modules\.vite  # Windows
   ```

### Issue: Virtual Environment Not Activating

**Symptoms**: Commands still use system Python

**Solutions**:

**Linux/macOS**:
```bash
source .venv/bin/activate
```

**Windows CMD**:
```cmd
.venv\Scripts\activate.bat
```

**Windows PowerShell**:
```powershell
.venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Useful Commands Reference

### Django Management

```bash
# Create superuser
python manage.py createsuperuser

# Collect static files (production)
python manage.py collectstatic

# Show migrations status
python manage.py showmigrations

# Open Django shell with models loaded
python manage.py shell

# Create new app
python manage.py startapp app_name
```

### Database Commands

```bash
# Export data
python manage.py dumpdata > backup.json

# Import data
python manage.py loaddata backup.json

# Database shell
python manage.py dbshell
```

### Frontend Commands

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint

# Type check
npm run type-check
```

## Getting Help

- Check existing issues in the repository
- Review Django documentation: https://docs.djangoproject.com/
- Review React documentation: https://react.dev/
- Ask team members

## Development Notes

### For Production Deployment

⚠️ **Before deploying to production**:

1. Remove `.env.dev` from repository
2. Generate new `SECRET_KEY`
3. Set `DEBUG=False`
4. Configure proper `ALLOWED_HOSTS`
5. Use environment-specific database credentials
6. Set up proper static file serving
7. Configure HTTPS/SSL
8. Remove development user credentials from seed data

### Database Considerations

- PostgreSQL 18+ required
- Uses custom port `8101` to avoid conflicts
- Sample data includes ~5 customers, ~10 vehicles
- Inspection templates are production-ready

### API Integration

- FMCSA API key included for VIN decoding
- Rate limits may apply to free tier
- Consider upgrading key for production use

## License

[Your License Here]
