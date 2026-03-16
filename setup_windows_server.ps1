# ServiceProvider Windows Server Setup Script
# This script installs all dependencies and sets up the application on a fresh Windows Server

[CmdletBinding()]
param(
    [string]$DatabaseUrl = "postgresql://postgres:postgres@localhost:5432/service_provider",
    [string]$SecretKey = "",
    [string]$AllowedHosts = "localhost,127.0.0.1",
    [switch]$SkipDocker,
    [switch]$SkipPostgreSQL
)

# Require Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ServiceProvider Setup for Windows Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install Chocolatey (if not installed)
Write-Host "[1/7] Checking Chocolatey installation..." -ForegroundColor Yellow
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Green
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    refreshenv
} else {
    Write-Host "Chocolatey already installed" -ForegroundColor Green
}

# Step 2: Install Git (if not installed)
Write-Host "`n[2/7] Checking Git installation..." -ForegroundColor Yellow
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Git..." -ForegroundColor Green
    choco install git -y
    refreshenv
} else {
    Write-Host "Git already installed: $(git --version)" -ForegroundColor Green
}

# Step 3: Install Python 3.14 (if not installed)
Write-Host "`n[3/7] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0 -or $pythonVersion -notmatch "3\.14") {
    Write-Host "Installing Python 3.14..." -ForegroundColor Green
    choco install python314 -y
    refreshenv
} else {
    Write-Host "Python already installed: $pythonVersion" -ForegroundColor Green
}

# Step 4: Install Node.js 22 (if not installed)
Write-Host "`n[4/7] Checking Node.js installation..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0 -or $nodeVersion -notmatch "v22") {
    Write-Host "Installing Node.js 22..." -ForegroundColor Green
    choco install nodejs --version=22.0.0 -y
    refreshenv
} else {
    Write-Host "Node.js already installed: $nodeVersion" -ForegroundColor Green
}

# Step 5: Install PostgreSQL 18 (if not skipped)
if (!$SkipPostgreSQL) {
    Write-Host "`n[5/7] Checking PostgreSQL installation..." -ForegroundColor Yellow
    if (!(Get-Service postgresql* -ErrorAction SilentlyContinue)) {
        Write-Host "Installing PostgreSQL 18..." -ForegroundColor Green
        choco install postgresql18 --params '/Password:postgres' -y
        refreshenv

        # Wait for PostgreSQL service to start
        Start-Sleep -Seconds 10

        # Create database
        Write-Host "Creating service_provider database..." -ForegroundColor Green
        & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "CREATE DATABASE service_provider;" 2>$null
    } else {
        Write-Host "PostgreSQL already installed" -ForegroundColor Green
    }
} else {
    Write-Host "`n[5/7] Skipping PostgreSQL installation (--SkipPostgreSQL)" -ForegroundColor Yellow
}

# Step 6: Install Docker (if not skipped)
if (!$SkipDocker) {
    Write-Host "`n[6/7] Checking Docker installation..." -ForegroundColor Yellow
    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "Installing Docker Engine for Windows Server..." -ForegroundColor Green

        # Download and run Microsoft's Docker CE installer
        Invoke-WebRequest -UseBasicParsing "https://raw.githubusercontent.com/microsoft/Windows-Containers/Main/helpful_tools/Install-DockerCE/install-docker-ce.ps1" -OutFile install-docker-ce.ps1
        .\install-docker-ce.ps1
        Remove-Item install-docker-ce.ps1

        Write-Host "Docker installed. You may need to restart the server." -ForegroundColor Yellow
    } else {
        Write-Host "Docker already installed: $(docker --version)" -ForegroundColor Green
    }
} else {
    Write-Host "`n[6/7] Skipping Docker installation (--SkipDocker)" -ForegroundColor Yellow
}

# Step 7: Clone and setup the application
Write-Host "`n[7/7] Setting up ServiceProvider application..." -ForegroundColor Yellow

$repoPath = "$PSScriptRoot"
if (!(Test-Path "$repoPath\.git")) {
    Write-Host "Git repository not found. Please clone the repository first." -ForegroundColor Red
    exit 1
}

Write-Host "Repository found at: $repoPath" -ForegroundColor Green

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Green
Set-Location $repoPath
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Green
Set-Location "$repoPath\frontend"
npm install

# Build frontend
Write-Host "Building frontend..." -ForegroundColor Green
npm run build

# Generate SECRET_KEY if not provided
if ($SecretKey -eq "") {
    Write-Host "Generating Django SECRET_KEY..." -ForegroundColor Green
    Set-Location $repoPath
    $SecretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
}

# Create .env file
Write-Host "Creating .env file..." -ForegroundColor Green
Set-Location $repoPath
@"
DATABASE_URL=$DatabaseUrl
SECRET_KEY=$SecretKey
DEBUG=False
ALLOWED_HOSTS=$AllowedHosts
DJANGO_SETTINGS_MODULE=config.settings
"@ | Out-File -FilePath .env -Encoding UTF8

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Green
python manage.py migrate

# Create superuser prompt
Write-Host "`nDatabase migrations complete!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create superuser: python manage.py createsuperuser" -ForegroundColor White
Write-Host "2. Load initial data: python manage.py seed_data" -ForegroundColor White
Write-Host "3. Run development server: python manage.py runserver 0.0.0.0:8100" -ForegroundColor White
Write-Host ""
Write-Host "Or build and run with Docker:" -ForegroundColor Yellow
Write-Host "1. docker build -t service-provider:latest ." -ForegroundColor White
Write-Host "2. docker run -d -p 8100:8100 --env-file .env service-provider:latest" -ForegroundColor White
Write-Host ""
Write-Host "Environment file created at: $repoPath\.env" -ForegroundColor Green
Write-Host "Update DATABASE_URL and other settings as needed." -ForegroundColor Yellow
