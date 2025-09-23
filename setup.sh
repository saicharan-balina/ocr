#!/bin/bash

# Certificate OCR Setup Script

echo "🚀 Setting up Certificate OCR Application..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Python and Node.js found"

# Setup Backend
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Backend setup complete"

# Setup Frontend
echo "📦 Setting up Frontend..."
cd ../frontend

# Install Node dependencies
echo "Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete"

# Back to root
cd ..

echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Make sure Tesseract OCR is installed on your system"
echo "2. Make sure Poppler is installed for PDF support"
echo "3. Run './start.sh' to start both servers"
echo ""
echo "📚 Installation guides:"
echo "- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki"
echo "- Poppler: https://github.com/oschwartz10612/poppler-windows/releases"