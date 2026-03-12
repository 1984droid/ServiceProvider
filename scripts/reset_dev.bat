@echo off
REM Reset development database (DESTRUCTIVE)
REM This script drops and recreates the database, then runs migrations

REM Change to project root directory
cd /d "%~dp0\.."

echo ============================================
echo WARNING: DATABASE RESET
echo ============================================
echo.
echo This will:
echo   - Drop the entire database
echo   - Delete all data
echo   - Recreate the database
echo   - Run migrations
echo   - Require you to create a new superuser
echo.
set /p CONFIRM="Are you sure? Type 'yes' to continue: "

if not "%CONFIRM%"=="yes" (
    echo.
    echo Reset cancelled
    exit /b 0
)

echo.
echo Proceeding with database reset...
echo.

if not exist "venv\" (
    echo ERROR: Virtual environment not found. Run scripts\setup_dev.bat first
    exit /b 1
)

REM Load environment variables
for /f "tokens=1,2 delims==" %%a in ('type .env ^| findstr /v "^#"') do set %%a=%%b

REM Activate virtual environment
call venv\Scripts\activate.bat

echo [1/4] Dropping database...
psql -U postgres -c "DROP DATABASE IF EXISTS %DB_NAME%;"
psql -U postgres -c "DROP USER IF EXISTS %DB_USER%;"
echo Database dropped
echo.

echo [2/4] Creating fresh database...
psql -U postgres -c "CREATE DATABASE %DB_NAME%;"
psql -U postgres -c "CREATE USER %DB_USER% WITH PASSWORD '%DB_PASSWORD%';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;"
psql -U postgres -c "ALTER DATABASE %DB_NAME% OWNER TO %DB_USER%;"
echo Database created
echo.

echo [3/4] Running migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to run migrations
    exit /b 1
)
echo Migrations completed
echo.

echo [4/4] Creating superuser...
python manage.py createsuperuser
echo.

echo ============================================
echo Database Reset Complete!
echo ============================================
echo.
echo You can now start the development server:
echo   scripts\run_dev.bat
echo.

pause
