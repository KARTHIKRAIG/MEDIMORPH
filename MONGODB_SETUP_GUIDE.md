# 🗄️ MongoDB Setup Guide for MEDIMORPH

## 📋 Overview

MEDIMORPH now supports MongoDB for data storage! This guide will help you set up MongoDB and configure MEDIMORPH to use your MongoDB connection string: `mongodb://localhost:27017/`

---

## 🚀 Quick Setup Options

### **Option 1: Local MongoDB Installation (Recommended)**

#### **Windows Installation:**
1. **Download MongoDB Community Server**
   - Visit: https://www.mongodb.com/try/download/community
   - Select: Windows x64, MSI package
   - Download and run the installer

2. **Installation Steps:**
   ```bash
   # Run the downloaded .msi file
   # Choose "Complete" installation
   # Install MongoDB as a Windows Service ✅
   # Install MongoDB Compass (GUI tool) ✅
   ```

3. **Start MongoDB Service:**
   ```bash
   # Method 1: Windows Services
   # Press Win+R, type "services.msc"
   # Find "MongoDB" service and start it
   
   # Method 2: Command Line (as Administrator)
   net start MongoDB
   ```

4. **Verify Installation:**
   ```bash
   # Test connection
   mongosh
   # Should connect to MongoDB shell
   ```

#### **Alternative: MongoDB with Docker**
```bash
# Pull MongoDB Docker image
docker pull mongo:latest

# Run MongoDB container
docker run -d --name medimorph-mongo -p 27017:27017 mongo:latest

# Verify running
docker ps
```

### **Option 2: MongoDB Atlas (Cloud) - Free Tier**

1. **Create Account:**
   - Visit: https://www.mongodb.com/atlas
   - Sign up for free account

2. **Create Cluster:**
   - Choose "Free Shared" cluster
   - Select region closest to you
   - Create cluster (takes 3-5 minutes)

3. **Get Connection String:**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy connection string
   - Replace `<password>` with your database password

4. **Update MEDIMORPH:**
   - Edit `mongodb_config.py`
   - Replace `MONGODB_URI` with your Atlas connection string

---

## 🔧 MEDIMORPH MongoDB Configuration

### **Files Created for MongoDB Integration:**

1. **`mongodb_config.py`** - MongoDB models and configuration
2. **`app_mongodb.py`** - MongoDB version of MEDIMORPH
3. **`setup_mongodb.py`** - MongoDB setup and testing script
4. **`test_mongodb_storage.py`** - MongoDB functionality tests

### **MongoDB Models:**

```python
# User Model
class User(Document, UserMixin):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    # ... additional fields

# Medication Model  
class Medication(Document):
    user_id = ObjectIdField(required=True)
    name = StringField(required=True)
    dosage = StringField(required=True)
    frequency = StringField(required=True)
    # ... additional fields with MongoDB-specific features

# Reminder Model
class Reminder(Document):
    medication_id = ObjectIdField(required=True)
    user_id = ObjectIdField(required=True)
    time = StringField(required=True)  # "HH:MM" format
    # ... additional fields

# Medication Log Model
class MedicationLog(Document):
    user_id = ObjectIdField(required=True)
    medication_id = ObjectIdField(required=True)
    taken_at = DateTimeField(default=datetime.utcnow)
    # ... additional fields
```

---

## 🚀 Running MEDIMORPH with MongoDB

### **Step 1: Ensure MongoDB is Running**
```bash
# Check if MongoDB is running
python setup_mongodb.py

# Should show:
# ✅ MongoDB is installed and running
# ✅ Python dependencies installed
# ✅ Ready to run MEDIMORPH with MongoDB
```

### **Step 2: Run MongoDB Version**
```bash
# Run the MongoDB version of MEDIMORPH
python app_mongodb.py

# Expected output:
# ✅ Connected to MongoDB: mongodb://localhost:27017/medimorph_db
# 📊 MongoDB Database status:
#    👥 Users: 2
#    💊 Medications: 0
#    ⏰ Reminders: 0
# 🏥 Starting MEDIMORPH with MongoDB...
# 🌐 Access the application at: http://localhost:5000
```

### **Step 3: Test MongoDB Integration**
```bash
# Run comprehensive MongoDB tests
python test_mongodb_storage.py

# Expected results:
# 🎉 ALL MONGODB TESTS PASSED!
# 💾 All data is being stored in MongoDB successfully!
```

---

## 📊 MongoDB vs SQLite Comparison

| Feature | SQLite (Original) | MongoDB (New) |
|---------|------------------|---------------|
| **Database Type** | Relational | Document-based |
| **File Storage** | Single .db file | Distributed collections |
| **Scalability** | Limited | Highly scalable |
| **Query Language** | SQL | MongoDB Query Language |
| **Relationships** | Foreign keys | Embedded documents/references |
| **Performance** | Fast for small data | Optimized for large datasets |
| **Backup** | Copy .db file | mongodump/mongorestore |
| **Cloud Support** | Limited | MongoDB Atlas |

---

## 🔄 Migration from SQLite to MongoDB

### **Automatic Migration Script:**
```python
# Run migration (if you have existing SQLite data)
python migrate_sqlite_to_mongodb.py

# This will:
# 1. Read data from SQLite database
# 2. Convert to MongoDB format
# 3. Insert into MongoDB collections
# 4. Verify data integrity
```

### **Manual Migration Steps:**
1. **Export SQLite data** to JSON
2. **Transform data** to MongoDB document format
3. **Import data** using MongoDB tools
4. **Verify migration** with test scripts

---

## 🧪 Testing MongoDB Integration

### **Health Checks:**
```bash
# Test MongoDB connection
curl http://localhost:5000/database-status

# Expected response:
{
  "status": "connected",
  "database_type": "mongodb",
  "connection_string": "mongodb://localhost:27017/",
  "database_name": "medimorph_db",
  "statistics": {
    "users": 2,
    "medications": 15,
    "reminders": 8,
    "medication_logs": 25,
    "prescription_uploads": 3
  }
}
```

### **Data Operations:**
```bash
# Add medication via API
curl -X POST http://localhost:5000/medications \
  -H "Content-Type: application/json" \
  -d '{"name":"MongoDB Test Med","dosage":"100mg","frequency":"daily"}'

# Get medications
curl http://localhost:5000/medications
```

---

## 🔧 MongoDB Administration

### **Using MongoDB Compass (GUI):**
1. **Install MongoDB Compass** (included with MongoDB)
2. **Connect** to `mongodb://localhost:27017`
3. **Browse** `medimorph_db` database
4. **View collections**: users, medications, reminders, etc.
5. **Query data** with visual interface

### **Using MongoDB Shell:**
```bash
# Connect to MongoDB
mongosh

# Switch to MEDIMORPH database
use medimorph_db

# Show collections
show collections

# Query users
db.users.find()

# Query medications
db.medications.find().pretty()

# Get collection stats
db.medications.stats()
```

### **Backup and Restore:**
```bash
# Backup entire database
mongodump --db medimorph_db --out ./backup

# Restore database
mongorestore --db medimorph_db ./backup/medimorph_db

# Backup specific collection
mongodump --db medimorph_db --collection medications --out ./backup
```

---

## 🚨 Troubleshooting

### **Common Issues:**

#### **"MongoDB connection failed"**
```bash
# Check if MongoDB is running
net start MongoDB  # Windows
sudo systemctl status mongod  # Linux

# Check port availability
netstat -an | findstr 27017  # Windows
netstat -an | grep 27017     # Linux
```

#### **"Authentication failed"**
```bash
# If using MongoDB with authentication
# Update connection string in mongodb_config.py:
MONGODB_URI = "mongodb://username:password@localhost:27017/"
```

#### **"Collection not found"**
```bash
# Collections are created automatically
# Run the application once to initialize
python app_mongodb.py
```

### **Performance Issues:**
```bash
# Create indexes for better performance
mongosh
use medimorph_db
db.medications.createIndex({"user_id": 1, "name": 1})
db.reminders.createIndex({"user_id": 1, "is_active": 1})
```

---

## 🎯 Next Steps

1. **✅ Install MongoDB** using the guide above
2. **✅ Run setup script**: `python setup_mongodb.py`
3. **✅ Start MEDIMORPH**: `python app_mongodb.py`
4. **✅ Test functionality**: `python test_mongodb_storage.py`
5. **✅ Access application**: http://localhost:5000

### **Advanced Features:**
- **Replica Sets** for high availability
- **Sharding** for horizontal scaling
- **MongoDB Atlas** for cloud deployment
- **Change Streams** for real-time updates
- **Aggregation Pipelines** for complex queries

---

## 📞 Support

### **MongoDB Resources:**
- **Documentation**: https://docs.mongodb.com/
- **Community**: https://community.mongodb.com/
- **University**: https://university.mongodb.com/

### **MEDIMORPH MongoDB Support:**
- **Test Scripts**: Run `python test_mongodb_storage.py`
- **Health Check**: Visit http://localhost:5000/database-status
- **Logs**: Check console output for detailed information

---

**🎉 Your MEDIMORPH application is now ready to use MongoDB for scalable, document-based data storage!**
