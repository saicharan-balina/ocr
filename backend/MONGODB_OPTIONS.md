# MongoDB Setup Options

You have several options for setting up MongoDB:

## Option 1: MongoDB Atlas (Cloud) - RECOMMENDED for quick setup

1. **Sign up for MongoDB Atlas** (free tier available):
   - Go to https://www.mongodb.com/cloud/atlas
   - Create a free account
   - Create a new cluster (free M0 tier)

2. **Get your connection string**:
   - In Atlas dashboard, click "Connect"
   - Choose "Connect your application"
   - Copy the connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

3. **Update your .env file**:
   ```
   MONGODB_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/
   MONGODB_DATABASE=certificate_verification_db
   ```

## Option 2: Local MongoDB Installation

### Windows
1. Download from: https://www.mongodb.com/try/download/community
2. Install as Windows Service
3. Start with: `net start MongoDB`

### Alternative: Use Docker
```bash
# Install Docker Desktop first
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## Option 3: In-Memory Development (Fallback)

If you want to test without MongoDB, I can create a hybrid solution that uses MongoDB when available and falls back to JSON storage.

## Quick Test with MongoDB Atlas

1. Create free Atlas account: https://www.mongodb.com/cloud/atlas
2. Update `.env` file with your connection string
3. Run: `python app.py`

Which option would you prefer?