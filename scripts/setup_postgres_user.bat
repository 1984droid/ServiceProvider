@echo off
REM Setup PostgreSQL database and user for ServiceProvider
REM This creates a dedicated database user (not using postgres superuser)

echo ========================================
echo PostgreSQL Database Setup
echo ========================================
echo.
echo This will create:
echo   - Database user: service_provider_user
echo   - Database: service_provider_new
echo   - Password: dev_password_123
echo.
echo This requires the postgres superuser password.
echo If you don't know it, you can find it in pgAdmin or reset it.
echo.
pause

REM Find PostgreSQL bin directory
set PGBIN=C:\Program Files\PostgreSQL\18\bin
if not exist "%PGBIN%\psql.exe" (
    set PGBIN=C:\Program Files\PostgreSQL\17\bin
)
if not exist "%PGBIN%\psql.exe" (
    set PGBIN=C:\Program Files\PostgreSQL\16\bin
)

if not exist "%PGBIN%\psql.exe" (
    echo X PostgreSQL not found
    echo   Please install PostgreSQL 18+ first
    pause
    exit /b 1
)

echo Found PostgreSQL at: %PGBIN%
echo.

REM Add to PATH for this session
set PATH=%PATH%;%PGBIN%

echo Enter the postgres superuser password when prompted...
echo.

REM Create the database user
echo Creating database user 'service_provider_user'...
psql -h localhost -p 5432 -U postgres -d postgres -c "CREATE USER service_provider_user WITH PASSWORD 'dev_password_123';"
if errorlevel 1 (
    echo.
    echo Note: User might already exist, continuing...
)

REM Create the database
echo Creating database 'service_provider_new'...
psql -h localhost -p 5432 -U postgres -d postgres -c "CREATE DATABASE service_provider_new OWNER service_provider_user;"
if errorlevel 1 (
    echo.
    echo Note: Database might already exist, continuing...
)

REM Grant privileges
echo Granting privileges...
psql -h localhost -p 5432 -U postgres -d service_provider_new -c "GRANT ALL PRIVILEGES ON DATABASE service_provider_new TO service_provider_user;"
psql -h localhost -p 5432 -U postgres -d service_provider_new -c "GRANT ALL ON SCHEMA public TO service_provider_user;"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Database credentials:
echo   Host: localhost
echo   Port: 5432
echo   Database: service_provider_new
echo   User: service_provider_user
echo   Password: dev_password_123
echo.
echo Update your .env file with these credentials:
echo   DB_NAME=service_provider_new
echo   DB_USER=service_provider_user
echo   DB_PASSWORD=dev_password_123
echo   DB_HOST=localhost
echo   DB_PORT=5432
echo.
pause
