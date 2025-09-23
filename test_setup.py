#!/usr/bin/env python3
"""
Test script to verify Certificate OCR setup
"""

import sys
import subprocess
import requests
import time
import os

def check_python_packages():
    """Check if required Python packages are installed"""
    print("🔍 Checking Python packages...")
    
    required_packages = [
        'flask', 'flask_cors', 'pytesseract', 
        'pillow', 'werkzeug', 'fitz'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All Python packages installed")
    return True

def check_tesseract():
    """Check if Tesseract OCR is available"""
    print("\n🔍 Checking Tesseract OCR...")
    
    try:
        import pytesseract
        from PIL import Image
        
        # Try to get Tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"  ✅ Tesseract version: {version}")
        return True
        
    except Exception as e:
        print(f"  ❌ Tesseract not found: {e}")
        print("Please install Tesseract OCR:")
        print("  - Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  - macOS: brew install tesseract")
        print("  - Linux: sudo apt-get install tesseract-ocr")
        return False

def check_pymupdf():
    """Check if PyMuPDF is available for PDF text and rendering support"""
    print("\n🔍 Checking PyMuPDF (PDF support)...")
    try:
        import fitz
        v = fitz.VersionBind
        print(f"  ✅ PyMuPDF version: {v}")
        return True
    except Exception as e:
        print(f"  ❌ PyMuPDF not available: {e}")
        print("Please ensure PyMuPDF is installed: pip install PyMuPDF")
        return False

def check_opencv_optional():
    """Check if OpenCV is available (optional, improves OCR)"""
    print("\n🔍 Checking OpenCV (optional)...")
    try:
        import cv2  # noqa: F401
        import numpy  # noqa: F401
        print("  ✅ OpenCV + NumPy available")
    except Exception:
        print("  ℹ️ OpenCV not installed; OCR will still work but may be less accurate.")
    return True

def test_flask_imports():
    """Test Flask application imports"""
    print("\n🔍 Testing Flask application...")
    
    try:
        sys.path.append('backend')
        from utils.ocr_processor import OCRProcessor
        from utils.file_handler import allowed_file, ALLOWED_EXTENSIONS
        
        print("  ✅ OCR processor import successful")
        print("  ✅ File handler import successful")
        print(f"  ✅ Supported extensions: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # Test OCR processor initialization
        ocr = OCRProcessor()
        print("  ✅ OCR processor initialization successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Flask import error: {e}")
        return False

def test_backend_server():
    """Test if backend server can start"""
    print("\n🔍 Testing backend server startup...")
    
    try:
        # Change to backend directory
        original_dir = os.getcwd()
        os.chdir('backend')
        
        # Try to start Flask server briefly
        proc = subprocess.Popen([
            sys.executable, 'app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Test health endpoint
        try:
            response = requests.get('http://localhost:5000/', timeout=5)
            if response.status_code == 200:
                print("  ✅ Backend server started successfully")
                print("  ✅ Health endpoint responding")
                success = True
            else:
                print(f"  ❌ Health endpoint returned status {response.status_code}")
                success = False
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Could not connect to backend: {e}")
            success = False
        
        # Stop the server
        proc.terminate()
        proc.wait(timeout=5)
        
        # Return to original directory
        os.chdir(original_dir)
        
        return success
        
    except Exception as e:
        print(f"  ❌ Backend server test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Certificate OCR Setup Test\n")
    
    tests = [
        check_python_packages,
        check_tesseract,
        check_pymupdf,
        check_opencv_optional,
        test_flask_imports,
        test_backend_server
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run the backend: cd backend && python app.py")
        print("2. Run the frontend: cd frontend && npm run dev")
        print("3. Open http://localhost:3000 in your browser")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()