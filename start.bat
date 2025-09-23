@echo off
REM Certificate OCR Start Script for Windows

echo 🚀 Starting Certificate OCR Application...

REM Start Backend
echo 🐍 Starting Flask Backend on port 5000...
cd backend

REM Activate virtual environment and start Flask
start "Flask Backend" cmd /k "venv\Scripts\activate.bat && python app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend
echo ⚛️  Starting Next.js Frontend on port 3000...
cd ..\frontend

REM Start Next.js
start "Next.js Frontend" cmd /k "npm run dev"

echo.
echo 🎉 Application is starting!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:5000
echo.
echo Two command windows have been opened.
echo Close both windows to stop the servers.

pause