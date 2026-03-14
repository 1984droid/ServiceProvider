@echo off
REM Start the Vite development server for React frontend
REM This script runs npm dev in the frontend directory

REM Change to project root directory
cd /d "%~dp0\.."

if not exist "frontend\node_modules\" (
    echo ERROR: Node modules not found. Run 'npm install' in frontend directory first
    exit /b 1
)

echo Starting frontend development server...
echo Frontend will be available at: http://localhost:5174
echo.
echo Press Ctrl+C to stop the server
echo.

cd frontend
npm run dev -- --port 5174
