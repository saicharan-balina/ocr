# MongoDB Migration Guide

This document explains the migration from TinyDB (JSON files) to MongoDB for a more professional, scalable database solution.

## What Changed

### 🗄️ Database Technology
- **Before**: TinyDB with JSON files (`certificates.json`)
- **After**: MongoDB (professional NoSQL database)

### 🚀 Benefits
- **Professional**: Industry-standard database used by major applications
- **Scalable**: Handles large datasets efficiently with proper indexing
- **Performance**: Faster queries with MongoDB's optimization
- **Reliability**: ACID compliance and better data integrity
- **Features**: Advanced querying, aggregation, and analytics
- **Deployment**: Easy to deploy in cloud environments

### 🔧 Technical Improvements
- Automatic indexing for fast lookups
- Better search capabilities with normalized fields
- Aggregation pipelines for statistics
- Connection pooling and health checks
- Proper error handling and logging

## Installation & Setup

### 1. Install MongoDB

#### Windows
```bash
# Download from https://www.mongodb.com/try/download/community
# Or use Chocolatey
choco install mongodb
```

#### macOS
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

#### Linux (Ubuntu/Debian)
```bash
# Import key and add repository
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start service
sudo systemctl start mongod
sudo systemctl enable mongod
```

### 2. Run Setup Script
```bash
cd backend
python setup_mongodb.py
```

This script will:
- Check if MongoDB is installed and running
- Install Python dependencies (pymongo, python-dotenv)
- Create `.env` configuration file
- Test the database connection

### 3. Migrate Existing Data
If you have existing data in `certificates.json`:

```bash
python migrate_to_mongodb.py
```

This will transfer all your certificates and verification logs to MongoDB.

## Configuration

### Environment Variables (`.env` file)
```bash
# Local MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=certificate_verification_db

# MongoDB Atlas (Cloud) - Optional
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
# MONGODB_DATABASE=certificate_verification_db

FLASK_ENV=development
```

### MongoDB Connection Options

#### Local Development
- Default: `mongodb://localhost:27017/`
- Custom port: `mongodb://localhost:27018/`
- With authentication: `mongodb://username:password@localhost:27017/`

#### Production (MongoDB Atlas)
1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create cluster and get connection string
3. Update `MONGODB_URI` in `.env` file

## Database Schema

### Collections

#### `certificates`
```javascript
{
  "_id": ObjectId("..."),
  "certificate_id": "CERT1234567890",
  "certificate_id_lower": "cert1234567890",  // For case-insensitive search
  "name": "John Doe",
  "name_normalized": "johndoe",             // For better search
  "roll_number": "20CS001",
  "roll_number_normalized": "20cs001",
  "course": "Computer Science",
  "course_normalized": "computerscience",
  "issue_date": "2024-01-15",
  "issuer": "University XYZ",
  "file_hash": "sha256hash...",
  "file_name": "certificate.pdf",
  "file_ext": "pdf",
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "updated_at": ISODate("2024-01-15T10:30:00Z")
}
```

#### `verifications`
```javascript
{
  "_id": ObjectId("..."),
  "type": "registration",
  "admin_role": "superadmin",
  "certificate_id": "CERT1234567890",
  "file_hash": "sha256hash...",
  "inserted": true,
  "timestamp": ISODate("2024-01-15T10:30:00Z")
}
```

### Indexes
- `certificate_id_lower` (unique lookups)
- `file_hash` (duplicate detection)
- `timestamp` (verification logs)
- Compound index on normalized name, roll, course (candidate search)

## API Changes

### Response Format
- MongoDB `_id` fields are automatically converted to strings
- All existing endpoints work the same way
- Enhanced statistics with aggregation

### New Health Check
```json
GET /
{
  "status": "healthy",
  "message": "Certificate OCR API is running",
  "version": "2.0.0",
  "database": {
    "type": "MongoDB",
    "status": "connected"
  }
}
```

## Development

### Starting the Application
```bash
# Make sure MongoDB is running
# Linux/macOS: sudo systemctl status mongod
# Windows: net start MongoDB

# Start the Flask app
python app.py
```

### Database Operations

#### Connect to MongoDB Shell
```bash
# Local
mongosh

# Select database
use certificate_verification_db

# View collections
show collections

# Query certificates
db.certificates.find().limit(5)

# View indexes
db.certificates.getIndexes()
```

#### Backup and Restore
```bash
# Backup
mongodump --db certificate_verification_db --out ./backup

# Restore
mongorestore --db certificate_verification_db ./backup/certificate_verification_db
```

## Monitoring & Maintenance

### Performance Monitoring
- Use MongoDB Compass (GUI tool) for visual monitoring
- Monitor slow queries: `db.setProfilingLevel(2)`
- Check index usage: `db.certificates.explain("executionStats").find(...)`

### Regular Maintenance
- Monitor disk usage
- Review and optimize indexes
- Backup data regularly
- Update MongoDB version periodically

## Troubleshooting

### Common Issues

#### "Connection refused"
```bash
# Check if MongoDB is running
# Linux/macOS: sudo systemctl status mongod
# Windows: net start MongoDB

# Check if port 27017 is open
netstat -an | grep 27017
```

#### "Import errors"
```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install pymongo python-dotenv
```

#### "Authentication failed"
```bash
# For MongoDB with auth enabled, update .env:
MONGODB_URI=mongodb://username:password@localhost:27017/
```

### Logs and Debugging
- Application logs show MongoDB connection status
- MongoDB logs: `/var/log/mongodb/mongod.log` (Linux)
- Enable debug mode in Flask for detailed error messages

## Migration Rollback

If you need to rollback to JSON files:

1. Export data from MongoDB:
```bash
mongoexport --db certificate_verification_db --collection certificates --out certificates_export.json
mongoexport --db certificate_verification_db --collection verifications --out verifications_export.json
```

2. Convert back to TinyDB format (you'll need to write a conversion script)

3. Update `requirements.txt` to use `tinydb` instead of `pymongo`

## Security Considerations

### Production Deployment
- Use authentication: `mongod --auth`
- Create dedicated database user
- Use SSL/TLS connections
- Configure firewall rules
- Regular security updates

### Connection Security
```bash
# Example secure connection string
MONGODB_URI=mongodb://appuser:strongpassword@localhost:27017/certificate_verification_db?authSource=admin&ssl=true
```

This migration provides a solid foundation for scaling your certificate verification system!