@echo off
REM Complete dev environment setup script from fresh git clone
REM This sets up ServiceProvider application from scratch on Windows

setlocal enabledelayedexpansion

echo =======================================
echo ServiceProvider - Dev Setup from Repo
echo =======================================
echo.
echo This script will:
echo   1. Check prerequisites
echo   2. Set up Python virtual environment
echo   3. Install dependencies (Python + Node)
echo   4. Configure environment (.env)
echo   5. Set up PostgreSQL database
echo   6. Run migrations
echo   7. Seed initial data
echo   8. Set up frontend
echo.
set /p CONFIRM="Continue? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Setup cancelled.
    exit /b 1
)
echo.

REM ============================================================================
REM 1. CHECK PREREQUISITES
REM ============================================================================
echo ========================================
echo 1. Checking Prerequisites
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "manage.py" (
    echo X Error: manage.py not found. Are you in the project root?
    exit /b 1
)
echo + Found project root

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.11+
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo + Python %PYTHON_VERSION% found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo X Node.js not found. Please install Node.js 18+
    exit /b 1
)
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo + Node.js %NODE_VERSION% found

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo X npm not found. Please install npm
    exit /b 1
)
for /f %%i in ('npm --version') do set NPM_VERSION=%%i
echo + npm %NPM_VERSION% found

REM Check PostgreSQL client
psql --version >nul 2>&1
if errorlevel 1 (
    echo ! psql client not found - PostgreSQL setup will be manual
    set HAVE_PSQL=false
) else (
    for /f "tokens=3" %%i in ('psql --version') do set PSQL_VERSION=%%i
    echo + PostgreSQL client %PSQL_VERSION% found
    set HAVE_PSQL=true
)

echo.
echo All prerequisites met!
echo.

REM ============================================================================
REM 2. SET UP PYTHON VIRTUAL ENVIRONMENT
REM ============================================================================
echo ========================================
echo 2. Setting Up Python Virtual Environment
echo ========================================
echo.

if exist ".venv" (
    echo ! .venv already exists
    set /p RECREATE="Delete and recreate? (y/n): "
    if /i "!RECREATE!"=="y" (
        rmdir /s /q .venv
        echo + Removed existing .venv
    ) else (
        echo - Using existing .venv
    )
)

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo + Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo X Could not activate virtual environment
    exit /b 1
)
echo + Virtual environment activated
echo.

REM ============================================================================
REM 3. INSTALL DEPENDENCIES
REM ============================================================================
echo ========================================
echo 3. Installing Dependencies
echo ========================================
echo.

echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo + pip upgraded

echo Installing Python dependencies...
pip install -r requirements.txt --quiet
echo + Python dependencies installed

echo Installing Node.js dependencies...
cd frontend
call npm install --silent
cd ..
echo + Node.js dependencies installed
echo.

REM ============================================================================
REM 4. CONFIGURE ENVIRONMENT
REM ============================================================================
echo ========================================
echo 4. Configuring Environment
echo ========================================
echo.

if exist ".env" (
    echo ! .env file already exists
    set /p OVERWRITE="Overwrite with .env.dev? (y/n): "
    if /i "!OVERWRITE!"=="y" (
        copy /y .env.dev .env >nul
        echo + .env copied from .env.dev
    ) else (
        echo - Using existing .env
    )
) else (
    if exist ".env.dev" (
        copy .env.dev .env >nul
        echo + .env copied from .env.dev
    ) else (
        echo X .env.dev not found. Please create .env manually.
        exit /b 1
    )
)

REM Load environment variables
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
    set "%%a=%%b"
)
echo + Environment variables loaded
echo.

REM ============================================================================
REM 5. SET UP POSTGRESQL DATABASE
REM ============================================================================
echo ========================================
echo 5. Setting Up PostgreSQL Database
echo ========================================
echo.

if "%HAVE_PSQL%"=="true" (
    echo Checking PostgreSQL connection...
    set PGPASSWORD=%DB_PASSWORD%
    psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d postgres -c "\q" >nul 2>&1
    if errorlevel 1 (
        echo X Cannot connect to PostgreSQL
        echo   Host: %DB_HOST%:%DB_PORT%
        echo   User: %DB_USER%
        echo.
        echo Please ensure PostgreSQL is running and credentials in .env are correct.
        exit /b 1
    )
    echo + PostgreSQL connection successful

    REM Check if database exists
    psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '%DB_NAME%'" | findstr "1" >nul
    if not errorlevel 1 (
        echo ! Database '%DB_NAME%' already exists
        set /p DROP_DB="Drop and recreate? (y/n): "
        if /i "!DROP_DB!"=="y" (
            echo Dropping database...
            psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d postgres -c "DROP DATABASE IF EXISTS %DB_NAME%"
            echo + Database dropped
        ) else (
            echo - Using existing database
        )
    )

    REM Create database if needed
    psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '%DB_NAME%'" | findstr "1" >nul
    if errorlevel 1 (
        echo Creating database '%DB_NAME%'...
        psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d postgres -c "CREATE DATABASE %DB_NAME%"
        echo + Database created
    )
) else (
    echo ! PostgreSQL client not available
    echo Please manually:
    echo   1. Start PostgreSQL server
    echo   2. Create database: CREATE DATABASE %DB_NAME%;
    echo.
    pause
)
echo.

REM ============================================================================
REM 6. RUN MIGRATIONS
REM ============================================================================
echo ========================================
echo 6. Running Database Migrations
echo ========================================
echo.

echo Running migrations...
python manage.py migrate
echo + Migrations complete
echo.

REM ============================================================================
REM 7. SEED INITIAL DATA
REM ============================================================================
echo ========================================
echo 7. Seeding Initial Data
echo ========================================
echo.

echo Seeding development data...
python manage.py seed_data
echo + Sample data created
echo.

REM ============================================================================
REM 8. SET UP FRONTEND
REM ============================================================================
echo ========================================
echo 8. Setting Up Frontend
echo ========================================
echo.

echo + Frontend dependencies already installed
echo + Frontend ready
echo.

REM ============================================================================
REM 9. CREATE LOGS DIRECTORY
REM ============================================================================
echo Creating logs directory...
if not exist "logs" mkdir logs
echo + Logs directory created
echo.

REM ============================================================================
REM SETUP COMPLETE
REM ============================================================================
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Summary:
echo    * Virtual environment: .venv\
echo    * Database: %DB_NAME%
echo    * Django port: %DJANGO_PORT%
echo    * Sample data loaded
echo.
echo Next Steps:
echo.
echo    1. Start the backend:
echo       python manage.py runserver %DJANGO_PORT%
echo.
echo    2. In another terminal, start the frontend:
echo       cd frontend
echo       npm run dev
echo.
echo    3. Access the application:
echo       * Frontend: http://localhost:5173
echo       * Backend API: http://localhost:%DJANGO_PORT%
echo       * Admin: http://localhost:%DJANGO_PORT%/admin
echo.
echo    4. Login credentials (from seed data):
echo       * Admin: admin@example.com / admin123
echo       * Inspector: inspector@example.com / inspector123
echo.
echo Useful commands:
echo    * Run tests: pytest
echo    * Django shell: python manage.py shell
echo    * Reset database: scripts\reset_dev.bat
echo.
echo Your virtual environment is active.
echo To deactivate: deactivate
echo.
pause
