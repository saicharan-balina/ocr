#!/bin/bash

# Certificate OCR Start Script

echo "🚀 Starting Certificate OCR Application..."

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if ports are available
if check_port 5000; then
    echo "⚠️  Port 5000 is already in use. Please stop the service using this port."
    exit 1
fi

if check_port 3000; then
    echo "⚠️  Port 3000 is already in use. Please stop the service using this port."
    exit 1
fi

# Start Backend
echo "🐍 Starting Flask Backend on port 5000..."
cd backend

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Start Flask in background
python app.py &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"

# Start Frontend
echo "⚛️  Starting Next.js Frontend on port 3000..."
cd ../frontend

# Start Next.js in background
npm run dev &
FRONTEND_PID=$!

echo "✅ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "🎉 Application is running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for background processes
wait