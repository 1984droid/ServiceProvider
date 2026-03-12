@echo off
REM Create new Django migrations for model changes
REM Usage: scripts\make_migrations.bat [app_name]

REM Change to project root directory
cd /d "%~dp0\.."

if not exist "venv\" (
    echo ERROR: Virtual environment not found. Run scripts\setup_dev.bat first
    exit /b 1
)

call venv\Scripts\activate.bat

if "%1"=="" (
    echo Creating migrations for all apps...
    python manage.py makemigrations
) else (
    echo Creating migrations for %1...
    python manage.py makemigrations %1
)

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create migrations
    exit /b 1
) else (
    echo.
    echo Migrations created successfully!
    echo Don't forget to run 'python manage.py migrate' to apply them
)
