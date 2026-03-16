# Windows Server Setup Guide

Complete setup guide for deploying ServiceProvider on a fresh Windows Server installation.

## Quick Start

Run this single PowerShell command as Administrator:

```powershell
# Download and run the setup script
Invoke-WebRequest -UseBasicParsing "https://raw.githubusercontent.com/YOUR_ORG/ServiceProvider/master/setup_windows_server.ps1" -OutFile setup.ps1
.\setup.ps1
```

Or if you already have the repository cloned:

```powershell
# Navigate to the repository
cd C:\path\to\ServiceProvider

# Run the setup script as Administrator
.\setup_windows_server.ps1
```

## What the Script Does

The automated setup script (`setup_windows_server.ps1`) performs the following:

1. ✅ **Installs Chocolatey** - Windows package manager
2. ✅ **Installs Git** - Version control
3. ✅ **Installs Python 3.14** - Backend runtime
4. ✅ **Installs Node.js 22** - Frontend build tool
5. ✅ **Installs PostgreSQL 18** - Database (optional, use `-SkipPostgreSQL` to skip)
6. ✅ **Installs Docker Engine** - Containerization (optional, use `-SkipDocker` to skip)
7. ✅ **Installs Python dependencies** - Backend packages
8. ✅ **Installs frontend dependencies** - npm packages
9. ✅ **Builds frontend** - Production React build
10. ✅ **Creates .env file** - Environment configuration
11. ✅ **Runs database migrations** - Sets up database schema

## Script Parameters

```powershell
# Custom database URL
.\setup_windows_server.ps1 -DatabaseUrl "postgresql://user:pass@server:5432/dbname"

# Custom Django secret key
.\setup_windows_server.ps1 -SecretKey "your-secret-key-here"

# Custom allowed hosts
.\setup_windows_server.ps1 -AllowedHosts "yourdomain.com,www.yourdomain.com"

# Skip PostgreSQL installation (if using external database)
.\setup_windows_server.ps1 -SkipPostgreSQL

# Skip Docker installation (if not using containers)
.\setup_windows_server.ps1 -SkipDocker

# Combine parameters
.\setup_windows_server.ps1 -SkipDocker -DatabaseUrl "postgresql://user:pass@external-db:5432/db"
```

## Manual Installation Steps

If you prefer manual installation or need to troubleshoot:

### 1. Install Prerequisites

**Install Chocolatey:**
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

**Install dependencies:**
```powershell
choco install git python314 nodejs --version=22.0.0 postgresql18 -y
```

**Install Docker Engine (Windows Server native):**
```powershell
Invoke-WebRequest -UseBasicParsing "https://raw.githubusercontent.com/microsoft/Windows-Containers/Main/helpful_tools/Install-DockerCE/install-docker-ce.ps1" -OutFile install-docker-ce.ps1
.\install-docker-ce.ps1
```

### 2. Clone Repository

```powershell
git clone https://github.com/YOUR_ORG/ServiceProvider.git
cd ServiceProvider
```

### 3. Setup Backend

```powershell
# Install Python dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
@"
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/service_provider
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
"@ | Out-File -FilePath .env -Encoding UTF8

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data
python manage.py seed_data
```

### 4. Setup Frontend

```powershell
cd frontend
npm install
npm run build
cd ..
```

### 5. Run the Application

**Option A: Development Server**
```powershell
python manage.py runserver 0.0.0.0:8100
```

**Option B: Production with Gunicorn (requires WSL or Linux)**
```powershell
gunicorn config.wsgi:application --bind 0.0.0.0:8100 --workers 4
```

**Option C: Docker Container**
```powershell
# Build the image
docker build -t service-provider:latest .

# Run the container
docker run -d `
  -p 8100:8100 `
  --env-file .env `
  --name service-provider `
  service-provider:latest
```

## Troubleshooting

### Docker Installation Issues

If Docker Desktop winget package doesn't exist, use Docker Engine for Windows Server instead:

```powershell
# Native Docker Engine installation (no Desktop required)
Invoke-WebRequest -UseBasicParsing "https://raw.githubusercontent.com/microsoft/Windows-Containers/Main/helpful_tools/Install-DockerCE/install-docker-ce.ps1" -OutFile install-docker-ce.ps1
.\install-docker-ce.ps1
```

This installs Docker as a Windows service - no GUI, no login required.

### PostgreSQL Connection Issues

Check if PostgreSQL service is running:
```powershell
Get-Service postgresql*
```

If not running:
```powershell
Start-Service postgresql-x64-18
```

Test connection:
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d service_provider
```

### Frontend Build Issues

If npm install fails with peer dependency errors:
```powershell
cd frontend
npm install --legacy-peer-deps
```

The `.npmrc` file should handle this automatically, but the flag can be used manually if needed.

### Python Package Issues

If pip install fails:
```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

## Firewall Configuration

Allow inbound traffic on port 8100:
```powershell
New-NetFirewallRule -DisplayName "ServiceProvider API" -Direction Inbound -LocalPort 8100 -Protocol TCP -Action Allow
```

## Running as a Windows Service

To run the application as a Windows service, use NSSM (Non-Sucking Service Manager):

```powershell
# Install NSSM
choco install nssm -y

# Create service
nssm install ServiceProvider "C:\Python314\python.exe" "C:\path\to\ServiceProvider\manage.py runserver 0.0.0.0:8100"

# Set working directory
nssm set ServiceProvider AppDirectory "C:\path\to\ServiceProvider"

# Start service
nssm start ServiceProvider
```

## Environment Variables Reference

Create or edit `.env` file in the project root:

```env
# Database connection
DATABASE_URL=postgresql://user:password@host:port/database

# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Optional settings
DJANGO_SETTINGS_MODULE=config.settings
```

## Production Checklist

- [ ] PostgreSQL installed and running
- [ ] Database created and migrated
- [ ] Superuser account created
- [ ] Initial data loaded (`python manage.py seed_data`)
- [ ] `.env` file configured with production values
- [ ] `DEBUG=False` in .env
- [ ] `SECRET_KEY` is unique and secure
- [ ] `ALLOWED_HOSTS` contains your domain
- [ ] Firewall rules configured
- [ ] SSL certificate configured (use IIS or nginx as reverse proxy)
- [ ] Application running as a Windows service
- [ ] Backups configured for database

## Next Steps

After setup completes:

1. **Access the application:** http://localhost:8100
2. **Access admin panel:** http://localhost:8100/admin
3. **Run tests:** `python -m pytest tests/`
4. **Configure reverse proxy** (IIS, nginx, or Caddy) for SSL termination
5. **Setup automated backups** for PostgreSQL database
6. **Configure monitoring** and logging

## Support

For issues or questions:
- Check the main [DEPLOYMENT.md](./DEPLOYMENT.md) for Docker-specific guidance
- Check application logs in the console or service logs
- Verify all services are running: PostgreSQL, Docker (if used)
