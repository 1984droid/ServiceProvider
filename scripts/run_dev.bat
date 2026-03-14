@echo off
REM Start the Django development server
REM This script activates the virtual environment and starts runserver

REM Change to project root directory
cd /d "%~dp0\.."

if not exist ".venv\" (
    echo ERROR: Virtual environment not found. Run scripts\setup_dev.bat first
    exit /b 1
)

echo Starting development server...
echo Server will be available at: http://localhost:8100
echo Admin interface at: http://localhost:8100/admin
echo.
echo Press Ctrl+C to stop the server
echo.

call .venv\Scripts\activate.bat
python manage.py runserver 8100
