#!/bin/bash

# HATSS Development Environment Startup Script
# Bash script for Unix/Linux/macOS
# Usage: chmod +x start-hatss.sh && ./start-hatss.sh [--backend] [--frontend] [--both]

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
BACKEND=false
FRONTEND=false
BOTH=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            BACKEND=true
            BOTH=false
            shift
            ;;
        --frontend)
            FRONTEND=true
            BOTH=false
            shift
            ;;
        --both)
            BOTH=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Helper functions
write_status() {
    echo -e "${GREEN}✓ $1${NC}"
}

write_error() {
    echo -e "${RED}❌ $1${NC}"
}

write_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

write_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

write_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HATSS_DIR="$SCRIPT_DIR"

write_header "HATSS Development Environment Startup"
echo ""

# Check Node.js
write_info "Checking Node.js..."
if ! command -v node &> /dev/null; then
    write_error "Node.js not found. Please install Node.js 22.x or later"
    exit 1
fi
NODE_VERSION=$(node -v)
write_status "Node.js: $NODE_VERSION"

# Check Python
write_info "Checking Python..."
if ! command -v python3 &> /dev/null; then
    write_error "Python 3 not found. Please install Python 3.11 or later"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
write_status "Python: $PYTHON_VERSION"

# Check npm dependencies
write_info "Checking frontend dependencies..."
if [ ! -d "$HATSS_DIR/frontend/node_modules" ]; then
    write_warning "node_modules not found. Installing dependencies..."
    cd "$HATSS_DIR/frontend"
    npm install
    cd "$HATSS_DIR"
fi
write_status "Frontend dependencies ready"

# Check Python venv
write_info "Checking backend virtual environment..."
if [ ! -d "$HATSS_DIR/backend/venv" ]; then
    write_warning "Virtual environment not found. Creating..."
    python3 -m venv "$HATSS_DIR/backend/venv"
fi
write_status "Backend virtual environment ready"

echo ""
write_header "Starting HATSS Services"
echo ""

# Determine which services to start
START_BOTH=$BOTH
START_BACKEND_ONLY=$BACKEND
START_FRONTEND_ONLY=$FRONTEND

# If both flags are set
if [ "$START_BOTH" = true ]; then
    START_BACKEND_ONLY=false
    START_FRONTEND_ONLY=false
fi

# Start Backend
if [ "$START_BOTH" = true ] || [ "$START_BACKEND_ONLY" = true ]; then
    write_info "[1/2] Starting Backend Server..."
    echo "      Port: 8000"
    echo "      Location: $HATSS_DIR/backend"
    echo ""
    
    cd "$HATSS_DIR/backend"
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    
    # Start uvicorn in background
    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    cd "$HATSS_DIR"
    
    write_status "Backend starting on http://localhost:8000"
    sleep 2
fi

# Start Frontend
if [ "$START_BOTH" = true ] || [ "$START_FRONTEND_ONLY" = true ]; then
    write_info "[2/2] Starting Frontend Server..."
    echo "      Port: 5173"
    echo "      Location: $HATSS_DIR/frontend"
    echo ""
    
    cd "$HATSS_DIR/frontend"
    npm run dev &
    FRONTEND_PID=$!
    cd "$HATSS_DIR"
    
    write_status "Frontend starting on http://localhost:5173"
    sleep 2
fi

echo ""
write_header "✓ HATSS Started Successfully!"
echo ""

# Display URLs
write_info "Access Points:"
echo "   • Frontend:     http://localhost:5173"
echo "   • Backend API:  http://localhost:8000"
echo "   • API Docs:     http://localhost:8000/docs"
echo "   • ESP32 (AP):   http://192.168.4.1 (when connected)"
echo ""

# Display helpful info
write_info "Hot Reload: Both servers support auto-reload on file changes"
echo "   • Frontend: Vite HMR enabled"
echo "   • Backend: Uvicorn auto-reload enabled"
echo ""

write_info "Documentation:"
echo "   • Tech Stack: ./TECH_STACK_SUMMARY.txt"
echo "   • App Summary: ./APP_SUMMARY.md"
echo "   • ESP32 Setup: ./backend/ESP32_SETUP.md"
echo ""

write_header "Running HATSS Servers"
echo ""
write_warning "Press Ctrl+C to stop all services"
echo ""

# Trap Ctrl+C to cleanup
trap cleanup INT

cleanup() {
    echo ""
    write_warning "Stopping HATSS services..."
    
    if [ ! -z "$BACKEND_PID" ] 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$FRONTEND_PID" ] 2>/dev/null; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn app.main:app" 2>/dev/null
    pkill -f "npm run dev" 2>/dev/null
    
    write_status "HATSS services stopped"
    exit 0
}

# Wait for all background jobs
wait
