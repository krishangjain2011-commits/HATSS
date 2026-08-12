# HATSS Development Environment Startup Script
# PowerShell script for Windows
# Usage: .\start-hatss.ps1

param(
    [switch]$Backend = $false,
    [switch]$Frontend = $false,
    [switch]$Both = $true
)

# Colors
$Green = "Green"
$Blue = "Cyan"
$Red = "Red"
$Yellow = "Yellow"

function Write-Status {
    param([string]$Message, [string]$Color = $Green)
    Write-Host $Message -ForegroundColor $Color
}

function Write-Error-Status {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

function Write-Warning-Status {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Yellow
}

# Get script directory
$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$HatssDir = $ScriptDir

Write-Status "╔══════════════════════════════════════════════════════════════╗" $Blue
Write-Status "║           HATSS Development Environment Startup             ║" $Blue
Write-Status "╚══════════════════════════════════════════════════════════════╝" $Blue
Write-Host ""

# Check if Node.js is installed
Write-Status "[CHECK] Verifying Node.js..." $Blue
$NodeVersion = node -v 2>$null
if (-not $NodeVersion) {
    Write-Error-Status "Node.js not found. Please install Node.js 22.x or later"
    exit 1
}
Write-Status "✓ Node.js: $NodeVersion" $Green

# Check if Python is installed
Write-Status "[CHECK] Verifying Python..." $Blue
$PythonVersion = python --version 2>$null
if (-not $PythonVersion) {
    Write-Error-Status "Python not found. Please install Python 3.11 or later"
    exit 1
}
Write-Status "✓ Python: $PythonVersion" $Green

# Check if frontend dependencies are installed
Write-Status "[CHECK] Verifying frontend dependencies..." $Blue
if (-not (Test-Path "$HatssDir\frontend\node_modules")) {
    Write-Warning-Status "node_modules not found. Installing dependencies..."
    Push-Location "$HatssDir\frontend"
    npm install
    Pop-Location
}
Write-Status "✓ Frontend dependencies ready" $Green

# Check if backend dependencies are installed
Write-Status "[CHECK] Verifying backend dependencies..." $Blue
$VenvPath = "$HatssDir\backend\.venv"
if (-not (Test-Path $VenvPath)) {
    Write-Warning-Status "Virtual environment not found. Creating..."
    Push-Location "$HatssDir\backend"
    python -m venv .venv
    Pop-Location
}
Write-Status "✓ Backend virtual environment ready" $Green

Write-Host ""
Write-Status "════════════════════════════════════════════════════════════════" $Blue
Write-Status "Starting HATSS Services..." $Blue
Write-Status "════════════════════════════════════════════════════════════════" $Blue
Write-Host ""

$StartBothServices = $Both -or ($Backend -and $Frontend)
$StartBackendOnly = $Backend -and -not $Frontend -and -not $Both
$StartFrontendOnly = $Frontend -and -not $Backend -and -not $Both

# Start Backend
if ($StartBothServices -or $StartBackendOnly) {
    Write-Status "[1/2] Starting Backend Server..." $Blue
    Write-Status "      Port: 8000" $Green
    Write-Status "      Location: $HatssDir\backend" $Green
    
    Push-Location "$HatssDir\backend"
    
    # Activate virtual environment and start server
    if (Test-Path ".\.venv\Scripts\Activate.ps1") {
        & ".\.venv\Scripts\Activate.ps1"
    } else {
        Write-Warning-Status "Virtual environment activation script not found"
    }
    
    # Start uvicorn in a new window
    Start-Process -NoNewWindow -FilePath "python" -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload") `
        -PassThru | Out-Null
    
    Pop-Location
    
    Write-Status "✓ Backend starting on http://localhost:8000" $Green
    Start-Sleep -Seconds 2
}

# Start Frontend
if ($StartBothServices -or $StartFrontendOnly) {
    Write-Status "[2/2] Starting Frontend Server..." $Blue
    Write-Status "      Port: 5173" $Green
    Write-Status "      Location: $HatssDir\frontend" $Green
    
    Push-Location "$HatssDir\frontend"
    Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run", "dev" `
        -PassThru | Out-Null
    Pop-Location
    
    Write-Status "✓ Frontend starting on http://localhost:5173" $Green
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Status "════════════════════════════════════════════════════════════════" $Blue
Write-Status "✓ HATSS Started Successfully!" $Green
Write-Status "════════════════════════════════════════════════════════════════" $Blue
Write-Host ""

# Display URLs
Write-Status "📍 Access Points:" $Blue
Write-Status "   • Frontend:     http://localhost:5173" $Green
Write-Status "   • Backend API:  http://localhost:8000" $Green
Write-Status "   • API Docs:     http://localhost:8000/docs" $Green
Write-Status "   • ESP32 (AP):   http://192.168.4.1 (when connected)" $Green
Write-Host ""

# Display helpful info
Write-Status "📝 Hot Reload: Both servers support auto-reload on file changes" $Blue
Write-Status "🔄 Frontend: Vite HMR enabled" $Green
Write-Status "🔄 Backend: Uvicorn auto-reload enabled" $Green
Write-Host ""

Write-Status "📖 Documentation:" $Blue
Write-Status "   • Tech Stack: ./TECH_STACK_SUMMARY.txt" $Green
Write-Status "   • App Summary: ./APP_SUMMARY.md" $Green
Write-Status "   • ESP32 Setup: ./backend/ESP32_SETUP.md" $Green
Write-Host ""

Write-Status "🛑 To stop the servers:" $Yellow
Write-Status "   Press Ctrl+C in each terminal or close the windows" $Yellow
Write-Host ""

# Keep script alive
Write-Status "════════════════════════════════════════════════════════════════" $Blue
Write-Status "Press Ctrl+C to stop all services" $Yellow
Write-Status "════════════════════════════════════════════════════════════════" $Blue

# Wait indefinitely
while ($true) {
    Start-Sleep -Seconds 1
}
