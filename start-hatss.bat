@echo off
REM HATSS Development Environment Startup Script
REM Batch script for Windows CMD
REM Usage: start-hatss.bat [backend] [frontend] [both]

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "HATSS_DIR=%SCRIPT_DIR%"

REM Parse arguments
set "START_BACKEND=0"
set "START_FRONTEND=0"
set "START_BOTH=1"

if "%1"=="backend" (
    set "START_BACKEND=1"
    set "START_BOTH=0"
)
if "%1"=="frontend" (
    set "START_FRONTEND=1"
    set "START_BOTH=0"
)
if "%1"=="both" (
    set "START_BOTH=1"
)

REM Colors (using color command)
cls
color 0B

echo.
echo ════════════════════════════════════════════════════════════════
echo            HATSS Development Environment Startup
echo ════════════════════════════════════════════════════════════════
echo.

REM Check Node.js
echo [CHECK] Verifying Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ Node.js not found. Please install Node.js 22.x or later
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set "NODE_VERSION=%%i"
color 0A
echo ✓ Node.js: !NODE_VERSION!

REM Check Python
echo [CHECK] Verifying Python...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ Python not found. Please install Python 3.11 or later
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set "PYTHON_VERSION=%%i"
color 0A
echo ✓ Python: !PYTHON_VERSION!

REM Check frontend dependencies
echo [CHECK] Verifying frontend dependencies...
if not exist "%HATSS_DIR%frontend\node_modules" (
    color 0E
    echo ⚠️  node_modules not found. Installing dependencies...
    color 0B
    cd /d "%HATSS_DIR%frontend"
    call npm install
    cd /d "%HATSS_DIR%"
)
color 0A
echo ✓ Frontend dependencies ready

REM Check backend virtual environment
echo [CHECK] Verifying backend virtual environment...
if not exist "%HATSS_DIR%backend\.venv" (
    color 0E
    echo ⚠️  Virtual environment not found. Creating...
    color 0B
    python -m venv "%HATSS_DIR%backend\.venv"
)
color 0A
echo ✓ Backend virtual environment ready

echo.
echo ════════════════════════════════════════════════════════════════
echo Starting HATSS Services...
echo ════════════════════════════════════════════════════════════════
echo.

REM Determine which services to start
if !START_BOTH! equ 1 (
    set "START_BACKEND=1"
    set "START_FRONTEND=1"
)

REM Start Backend
if !START_BACKEND! equ 1 (
    color 0B
    echo [1/2] Starting Backend Server...
    echo       Port: 8000
    echo       Location: %HATSS_DIR%backend
    echo.
    
    cd /d "%HATSS_DIR%backend"
    
    REM Activate virtual environment and start server in new window
    start "HATSS Backend" cmd /k "!HATSS_DIR!backend\.venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    
    cd /d "%HATSS_DIR%"
    
    color 0A
    echo ✓ Backend starting on http://localhost:8000
    timeout /t 2 /nobreak
)

REM Start Frontend
if !START_FRONTEND! equ 1 (
    color 0B
    echo [2/2] Starting Frontend Server...
    echo       Port: 5173
    echo       Location: %HATSS_DIR%frontend
    echo.
    
    cd /d "%HATSS_DIR%frontend"
    start "HATSS Frontend" cmd /k "npm run dev"
    cd /d "%HATSS_DIR%"
    
    color 0A
    echo ✓ Frontend starting on http://localhost:5173
    timeout /t 2 /nobreak
)

echo.
color 0A
echo ════════════════════════════════════════════════════════════════
echo ✓ HATSS Started Successfully!
echo ════════════════════════════════════════════════════════════════
echo.

color 0B
echo 📍 Access Points:
echo    • Frontend:     http://localhost:5173
echo    • Backend API:  http://localhost:8000
echo    • API Docs:     http://localhost:8000/docs
echo    • ESP32 (AP):   http://192.168.4.1 (when connected)
echo.

echo 📝 Hot Reload:
echo    • Frontend: Vite HMR enabled
echo    • Backend: Uvicorn auto-reload enabled
echo.

echo 📖 Documentation:
echo    • Tech Stack: TECH_STACK_SUMMARY.txt
echo    • App Summary: APP_SUMMARY.md
echo    • ESP32 Setup: backend\ESP32_SETUP.md
echo.

color 0E
echo ════════════════════════════════════════════════════════════════
echo ⚠️  Press any key in each terminal to stop the servers
echo ════════════════════════════════════════════════════════════════
echo.

pause

endlocal
