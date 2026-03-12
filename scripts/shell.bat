@echo off
REM Start Django shell with IPython if available
REM This script activates the virtual environment and starts Django shell

REM Change to project root directory
cd /d "%~dp0\.."

if not exist "venv\" (
    echo ERROR: Virtual environment not found. Run scripts\setup_dev.bat first
    exit /b 1
)

echo Starting Django shell...
echo.

call venv\Scripts\activate.bat
python manage.py shell
