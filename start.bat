@echo off
REM HATSS - Home Automated Threat Security System
REM Startup script for Windows

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   HATSS Startup Script
echo ========================================
echo.

REM Check if backend venv exists
if not exist "backend\.venv" (
    echo [*] Creating Python virtual environment...
    cd backend
    py -m venv .venv
    cd ..
)

REM Activate backend venv and install dependencies
echo [*] Setting up backend...
call backend\.venv\Scripts\activate.bat
cd backend
pip install -e . > nul 2>&1
cd ..

REM Start backend
echo [*] Starting backend server on http://localhost:8000...
start cmd /k "cd backend && .venv\Scripts\activate.bat && py -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start frontend
echo [*] Starting frontend server on http://localhost:5173...
start cmd /k "cd frontend && npm install > nul 2>&1 && npm run dev"

REM Wait a moment
timeout /t 2 /nobreak

echo.
echo ========================================
echo   HATSS Started Successfully!
echo ========================================
echo.
echo Frontend:  http://localhost:5173
echo Backend:   http://localhost:8000
echo.
echo Press Ctrl+C in each terminal to stop
echo.
pause
