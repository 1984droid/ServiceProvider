@echo off
REM Development environment setup script for Windows
REM This script sets up a complete development environment including:
REM - Virtual environment creation
REM - Dependency installation
REM - Database creation
REM - Initial migrations
REM - Superuser creation

REM Change to project root directory
cd /d "%~dp0\.."

echo ============================================
echo Service Provider - Development Setup
echo ============================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [1/7] Generating .env file with secure credentials...
    python scripts\generate_env.py
    if errorlevel 1 (
        echo ERROR: Failed to generate .env file
        exit /b 1
    )
    echo .env file created successfully
    echo.
) else (
    echo .env file already exists, skipping generation
    echo.
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo [2/7] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        exit /b 1
    )
    echo Virtual environment created
    echo.
) else (
    echo Virtual environment already exists
    echo.
)

REM Activate virtual environment and continue setup
echo [3/7] Installing Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Load environment variables
echo [4/7] Loading environment configuration...
for /f "tokens=1,2 delims==" %%a in ('type .env ^| findstr /v "^#"') do set %%a=%%b
echo Configuration loaded
echo.

echo [5/7] Creating PostgreSQL database...
REM Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE %DB_NAME%;" 2>nul
if errorlevel 1 (
    echo Database might already exist, continuing...
) else (
    echo Database created successfully
)

REM Create database user if not exists
psql -U postgres -c "CREATE USER %DB_USER% WITH PASSWORD '%DB_PASSWORD%';" 2>nul
if errorlevel 1 (
    echo User might already exist, continuing...
) else (
    echo Database user created successfully
)

REM Grant privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;"
psql -U postgres -c "ALTER DATABASE %DB_NAME% OWNER TO %DB_USER%;"
echo Database setup complete
echo.

echo [6/7] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to run migrations
    exit /b 1
)
echo Migrations completed successfully
echo.

echo [7/7] Creating superuser account...
echo You'll be prompted to create an admin account
python manage.py createsuperuser
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Your development environment is ready!
echo.
echo Next steps:
echo   1. Start the dev server: scripts\run_dev.bat
echo   2. Visit: http://localhost:8000/admin
echo   3. Log in with the superuser account you just created
echo.
echo Other useful commands:
echo   - scripts\shell.bat          : Django shell
echo   - scripts\make_migrations.bat : Create new migrations
echo   - scripts\reset_dev.bat      : Reset database (DESTRUCTIVE)
echo.

pause
