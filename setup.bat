@echo off
REM Certificate OCR Setup Script for Windows

echo 🚀 Setting up Certificate OCR Application...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo ✅ Python and Node.js found

REM Setup Backend
echo 📦 Setting up Backend...
cd backend

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

echo ✅ Backend setup complete

REM Setup Frontend
echo 📦 Setting up Frontend...
cd ..\frontend

REM Install Node dependencies
echo Installing Node.js dependencies...
npm install

echo ✅ Frontend setup complete

REM Back to root
cd ..

echo 🎉 Setup complete!
echo.
echo 📋 Next steps:
echo 1. Make sure Tesseract OCR is installed on your system
echo 2. Make sure Poppler is installed for PDF support
echo 3. Run 'start.bat' to start both servers
echo.
echo 📚 Installation guides:
echo - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
echo - Poppler: https://github.com/oschwartz10612/poppler-windows/releases

pause