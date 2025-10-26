#!/bin/bash

# Morgan Legal Tender - Stop All Services

echo "Stopping Morgan Legal Tender services..."

# Get directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Read PIDs if they exist
if [ -f "$DIR/.backend.pid" ]; then
    BACKEND_PID=$(cat "$DIR/.backend.pid")
    kill $BACKEND_PID 2>/dev/null && echo "✓ Backend stopped (PID: $BACKEND_PID)"
    rm "$DIR/.backend.pid"
fi

if [ -f "$DIR/.frontend.pid" ]; then
    FRONTEND_PID=$(cat "$DIR/.frontend.pid")
    kill $FRONTEND_PID 2>/dev/null && echo "✓ Frontend stopped (PID: $FRONTEND_PID)"
    rm "$DIR/.frontend.pid"
fi

# Fallback: kill by process name
pkill -f "python main.py" 2>/dev/null
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null

# Kill processes on ports
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "All services stopped."
