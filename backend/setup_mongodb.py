#!/usr/bin/env python3
"""
MongoDB setup script for Certificate Verification System.
This script helps set up MongoDB for development and production environments.
"""

import os
import sys
import subprocess
import platform


def check_mongodb_installed():
    """Check if MongoDB is installed and accessible."""
    try:
        result = subprocess.run(['mongod', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ MongoDB is installed")
            return True
        else:
            print("❌ MongoDB is not installed or not in PATH")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ MongoDB is not installed or not accessible")
        return False


def check_mongodb_running():
    """Check if MongoDB is currently running."""
    try:
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        client.close()
        print("✅ MongoDB is running")
        return True
    except Exception:
        print("❌ MongoDB is not running")
        return False


def start_mongodb():
    """Start MongoDB service."""
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # Try to start MongoDB as a service on Windows
            result = subprocess.run(['net', 'start', 'MongoDB'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ MongoDB service started successfully")
                return True
            else:
                print("⚠️  Could not start MongoDB service automatically")
                print("   Please start MongoDB manually or install it as a service")
                return False
        
        elif system in ["linux", "darwin"]:  # Linux or macOS
            # Try to start MongoDB with systemctl (Linux) or brew (macOS)
            if system == "linux":
                result = subprocess.run(['sudo', 'systemctl', 'start', 'mongod'], 
                                      capture_output=True, text=True)
            else:  # macOS
                result = subprocess.run(['brew', 'services', 'start', 'mongodb-community'], 
                                      capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ MongoDB started successfully")
                return True
            else:
                print("⚠️  Could not start MongoDB automatically")
                print("   Please start MongoDB manually")
                return False
        
        else:
            print(f"⚠️  Unsupported system: {system}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting MongoDB: {e}")
        return False


def install_dependencies():
    """Install Python dependencies."""
    try:
        print("📦 Installing Python dependencies...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                              check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = '.env'
    
    if os.path.exists(env_file):
        print(f"✅ {env_file} already exists")
        return True
    
    try:
        with open(env_file, 'w') as f:
            f.write("""# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=certificate_verification_db

# Alternative for MongoDB Atlas (cloud)
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
# MONGODB_DATABASE=certificate_verification_db

# Flask Configuration
FLASK_ENV=development
""")
        print(f"✅ Created {env_file} with default settings")
        return True
    except Exception as e:
        print(f"❌ Failed to create {env_file}: {e}")
        return False


def test_connection():
    """Test MongoDB connection with the application."""
    try:
        print("🧪 Testing MongoDB connection...")
        
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from db.store import CertificateStore
        
        store = CertificateStore()
        if store.health_check():
            print("✅ MongoDB connection test successful")
            
            # Test basic operations
            test_record = {
                'certificate_id': 'TEST_SETUP_' + str(int(os.times().elapsed * 1000)),
                'name': 'Test Setup',
                'course': 'Setup Test',
                'test_record': True
            }
            
            inserted, stored = store.upsert_record(test_record)
            if inserted:
                print("✅ Database write test successful")
                
                # Clean up test record
                if '_id' in stored:
                    store.certificates.delete_one({'_id': stored['_id']})
                    print("✅ Database cleanup successful")
            
            store.close_connection()
            return True
        else:
            print("❌ MongoDB connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


def print_installation_instructions():
    """Print MongoDB installation instructions for different platforms."""
    system = platform.system().lower()
    
    print("\n📖 MongoDB Installation Instructions:")
    print("=" * 50)
    
    if system == "windows":
        print("""
Windows:
1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community
2. Run the installer and follow the setup wizard
3. Install MongoDB as a Windows Service (recommended)
4. Or download and extract the ZIP file, then start manually with:
   mongod --dbpath C:\\data\\db
""")
    
    elif system == "linux":
        print("""
Ubuntu/Debian:
1. Import the public key:
   wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

2. Add MongoDB repository:
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

3. Install MongoDB:
   sudo apt-get update
   sudo apt-get install -y mongodb-org

4. Start MongoDB:
   sudo systemctl start mongod
   sudo systemctl enable mongod

CentOS/RHEL/Fedora:
1. Create repository file:
   sudo vi /etc/yum.repos.d/mongodb-org-7.0.repo

2. Add repository configuration and install:
   sudo yum install -y mongodb-org
   sudo systemctl start mongod
""")
    
    elif system == "darwin":  # macOS
        print("""
macOS:
1. Install using Homebrew (recommended):
   brew tap mongodb/brew
   brew install mongodb-community

2. Start MongoDB:
   brew services start mongodb-community

Alternative - Download manually:
1. Download from: https://www.mongodb.com/try/download/community
2. Extract and add to PATH
3. Create data directory: mkdir -p /usr/local/var/mongodb
4. Start: mongod --dbpath /usr/local/var/mongodb
""")
    
    print("\n💡 For cloud deployment, consider MongoDB Atlas:")
    print("   https://www.mongodb.com/cloud/atlas")


def main():
    """Main setup function."""
    print("🚀 Certificate Verification System - MongoDB Setup")
    print("=" * 55)
    
    # Step 1: Check if MongoDB is installed
    mongodb_installed = check_mongodb_installed()
    
    if not mongodb_installed:
        print_installation_instructions()
        print("\n⚠️  Please install MongoDB first, then run this script again.")
        return False
    
    # Step 2: Check if MongoDB is running
    mongodb_running = check_mongodb_running()
    
    if not mongodb_running:
        print("🔄 Attempting to start MongoDB...")
        if not start_mongodb():
            print("\n💡 Please start MongoDB manually and run this script again.")
            print("   Common commands:")
            print("   - Windows: net start MongoDB")
            print("   - Linux: sudo systemctl start mongod")
            print("   - macOS: brew services start mongodb-community")
            print("   - Manual: mongod --dbpath /path/to/data")
            return False
        
        # Wait a moment for MongoDB to fully start
        import time
        time.sleep(3)
        
        # Check again
        if not check_mongodb_running():
            print("❌ MongoDB still not running after start attempt")
            return False
    
    # Step 3: Install Python dependencies
    if not install_dependencies():
        return False
    
    # Step 4: Create .env file
    if not create_env_file():
        return False
    
    # Step 5: Test connection
    if not test_connection():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. If you have existing data in certificates.json, run:")
    print("   python migrate_to_mongodb.py")
    print("\n2. Start the application:")
    print("   python app.py")
    print("\n3. The API will be available at: http://localhost:5000")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)