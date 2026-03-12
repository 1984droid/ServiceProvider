@echo off
REM Wrapper script to generate .env file with secure credentials
REM This ensures the Python script runs from the correct directory

REM Change to project root directory
cd /d "%~dp0\.."

python scripts\generate_env.py
