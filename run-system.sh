#!/bin/bash

# Morgan Legal Tender - Complete System Startup
# Starts both backend and frontend

echo "======================================"
echo "Morgan Legal Tender - System Startup"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Kill any existing instances
echo -e "${YELLOW}Cleaning up existing processes...${NC}"
pkill -f "python main.py" 2>/dev/null
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 2

# Start Backend
echo ""
echo -e "${BLUE}Starting Backend Server...${NC}"
cd "$DIR/backend"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install/update dependencies
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Start backend in background
python main.py > "$DIR/backend.log" 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}✗ Backend failed to start. Check backend.log${NC}"
    exit 1
fi

# Start Frontend
echo ""
echo -e "${BLUE}Starting Frontend Server...${NC}"
cd "$DIR/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || echo "VITE_API_BASE_URL=http://localhost:8000" > .env
fi

# Start frontend in background
npm run dev > "$DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

# Wait a bit
sleep 3

# Check if frontend is running
if ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}✗ Frontend failed to start. Check frontend.log${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Save PIDs
echo "$BACKEND_PID" > "$DIR/.backend.pid"
echo "$FRONTEND_PID" > "$DIR/.frontend.pid"

# Display success message
echo ""
echo "======================================"
echo -e "${GREEN}✓ System Started Successfully!${NC}"
echo "======================================"
echo ""
echo -e "${BLUE}Access the application:${NC}"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo "  Backend: $DIR/backend.log"
echo "  Frontend: $DIR/frontend.log"
echo ""
echo -e "${YELLOW}To stop the system:${NC}"
echo "  ./stop-system.sh"
echo "  Or: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "======================================"
