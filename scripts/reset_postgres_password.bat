@echo off
REM Reset PostgreSQL password on Windows
REM This script resets the postgres user password

echo ========================================
echo PostgreSQL Password Reset
echo ========================================
echo.
echo This will reset the 'postgres' user password.
echo.
set /p NEW_PASSWORD="Enter new password for postgres user: "
echo.

REM Find PostgreSQL data directory
set PGDATA=C:\Program Files\PostgreSQL\18\data
if not exist "%PGDATA%" (
    set PGDATA=C:\Program Files\PostgreSQL\17\data
)
if not exist "%PGDATA%" (
    set PGDATA=C:\Program Files\PostgreSQL\16\data
)

if not exist "%PGDATA%" (
    echo X PostgreSQL data directory not found
    echo   Please locate your PostgreSQL installation and update PGDATA in this script
    pause
    exit /b 1
)

echo Found PostgreSQL data at: %PGDATA%
echo.

REM Restart PostgreSQL in single-user mode is complex on Windows
REM Easier approach: Use pg_hba.conf to allow trust authentication temporarily

echo This requires administrator access to modify PostgreSQL configuration.
echo.
echo MANUAL STEPS:
echo 1. Open: %PGDATA%\pg_hba.conf
echo 2. Find the line: host    all             all             127.0.0.1/32            scram-sha-256
echo 3. Change 'scram-sha-256' to 'trust'
echo 4. Restart PostgreSQL service (Services app or: net stop postgresql-x64-18 then net start postgresql-x64-18)
echo 5. Run: psql -U postgres -h localhost
echo 6. In psql, run: ALTER USER postgres WITH PASSWORD '%NEW_PASSWORD%';
echo 7. Revert pg_hba.conf back to 'scram-sha-256'
echo 8. Restart PostgreSQL service again
echo.
pause
