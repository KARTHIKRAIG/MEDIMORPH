# 🚀 MEDIMORPH Installation Guide

## 📋 Prerequisites

### **System Requirements**
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux Ubuntu 18.04+
- **Python**: Version 3.11 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free disk space
- **Network**: Internet connection for initial setup

### **Required Software**

#### **1. Python 3.11+**
```bash
# Check current Python version
python --version

# Windows: Download from https://python.org
# macOS: brew install python@3.11
# Linux: sudo apt-get install python3.11 python3.11-venv python3.11-pip
```

#### **2. Tesseract OCR Engine**
```bash
# Windows: Download installer from
https://github.com/UB-Mannheim/tesseract/wiki

# macOS:
brew install tesseract

# Linux Ubuntu/Debian:
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Verify installation
tesseract --version
```

#### **3. Git (Optional but recommended)**
```bash
# Windows: Download from https://git-scm.com
# macOS: brew install git
# Linux: sudo apt-get install git
```

---

## 📥 Installation Methods

### **Method 1: Clone from GitHub (Recommended)**

```bash
# Clone the repository
git clone https://github.com/KARTHIKRAIG/MEDIMORPH.git

# Navigate to project directory
cd MEDIMORPH

# Continue with setup steps below
```

### **Method 2: Download ZIP**

1. Visit: https://github.com/KARTHIKRAIG/MEDIMORPH
2. Click "Code" → "Download ZIP"
3. Extract to desired location
4. Open terminal in extracted folder

---

## 🔧 Setup Process

### **Step 1: Create Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
which python
```

### **Step 2: Install Dependencies**

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### **Step 3: Configure Tesseract Path (Windows)**

If Tesseract is not in your system PATH:

```python
# Edit prescription_ocr.py (around line 15)
# Update the path to match your Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### **Step 4: Initialize Database**

```bash
# Run the application once to create database
python app.py

# Stop with Ctrl+C after seeing "Starting MEDIMORPH application..."
# Database file will be created at: instance/medications.db
```

### **Step 5: Verify Installation**

```bash
# Run health check
python quick_health_check.py

# Run comprehensive system check
python final_system_check.py

# Expected output: All checks should pass ✅
```

---

## 🚀 Running the Application

### **Development Mode**

```bash
# Activate virtual environment (if not already active)
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Start the application
python app.py

# Access at: http://localhost:5000
```

### **Using Start Script (Windows)**

```bash
# Double-click start.bat or run:
start.bat

# This script will:
# 1. Check Python installation
# 2. Create/activate virtual environment
# 3. Install dependencies
# 4. Run tests
# 5. Start the application
```

### **Production Mode**

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn (Linux/macOS)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Windows production (using waitress)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

---

## 🔧 Configuration

### **Environment Variables**

Create a `.env` file in the project root:

```bash
# .env file
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///medications.db
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
FLASK_ENV=development
FLASK_DEBUG=True
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
```

### **Application Configuration**

Edit `app.py` for custom settings:

```python
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medications.db'

# File upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = 'uploads'

# Security settings
app.config['SECRET_KEY'] = 'your-secret-key-here'
```

---

## 🧪 Testing Installation

### **Quick Health Check**

```bash
python quick_health_check.py
```

**Expected Output:**
```
🔍 MEDIMORPH Quick Health Check
========================================
✅ Health Check: 200
✅ Login Page: 200
✅ Login Test: SUCCESS - User: testuser
✅ Dashboard: 200
✅ Medications API: 0 medications found
🎉 MEDIMORPH is working perfectly!
```

### **Comprehensive System Check**

```bash
python final_system_check.py
```

**Expected Output:**
```
🔍 PYTHON ENVIRONMENT CHECK
✅ Python 3.11.x
✅ Virtual environment active
✅ All required packages installed

🔍 DATABASE CONNECTIVITY CHECK
✅ Database connection successful
✅ All tables created successfully

🔍 APPLICATION ENDPOINTS CHECK
✅ Health endpoint: 200
✅ Login endpoint: 200
✅ Dashboard endpoint: 200

📊 RESULTS: 15/15 checks passed
✅ ALL SYSTEMS GO! Ready for deployment!
```

### **Manual Testing**

1. **Open browser**: http://localhost:5000
2. **Login**: Username: `testuser`, Password: `testpass123`
3. **Upload prescription**: Use sample image from `uploads/` folder
4. **Check extraction**: Verify medications are detected
5. **Set reminder**: Add a medication reminder
6. **Test notifications**: Wait for reminder notification

---

## 🐳 Docker Installation (Alternative)

### **Using Docker Compose**

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  medimorph:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/uploads
      - ./instance:/app/instance
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-production-secret-key
```

```bash
# Build and run
docker-compose up --build

# Access at: http://localhost:5000
```

### **Using Docker**

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

```bash
# Build image
docker build -t medimorph .

# Run container
docker run -p 5000:5000 medimorph
```

---

## 🚨 Troubleshooting

### **Common Issues**

#### **1. Python Version Error**
```
Error: Python 3.11+ required
Solution: Install Python 3.11 or higher from python.org
```

#### **2. Tesseract Not Found**
```
Error: TesseractNotFoundError
Solution: 
1. Install Tesseract OCR
2. Add to system PATH or update pytesseract.tesseract_cmd
```

#### **3. Port Already in Use**
```
Error: Address already in use
Solution: 
1. Kill existing process: netstat -ano | findstr :5000
2. Change port in app.py: socketio.run(app, port=5001)
```

#### **4. Permission Denied (Linux/macOS)**
```
Error: Permission denied
Solution: 
1. Check file permissions: chmod +x start.sh
2. Use sudo if needed: sudo python app.py
```

#### **5. Database Locked**
```
Error: database is locked
Solution:
1. Close all application instances
2. Delete instance/medications.db
3. Restart application to recreate database
```

#### **6. Module Not Found**
```
Error: ModuleNotFoundError
Solution:
1. Activate virtual environment
2. Reinstall requirements: pip install -r requirements.txt
```

### **Debug Mode**

Enable detailed error messages:

```python
# In app.py
app.config['DEBUG'] = True
app.config['TESTING'] = True

# Run with verbose output
python app.py --debug
```

### **Log Files**

Check application logs:

```bash
# Enable logging in app.py
import logging
logging.basicConfig(level=logging.DEBUG)

# View logs
tail -f app.log  # Linux/macOS
type app.log     # Windows
```

---

## 🔄 Updates and Maintenance

### **Updating MEDIMORPH**

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run system check
python final_system_check.py

# Restart application
python app.py
```

### **Database Backup**

```bash
# Backup database
cp instance/medications.db instance/medications_backup_$(date +%Y%m%d).db

# Restore database
cp instance/medications_backup_20240115.db instance/medications.db
```

### **Cleaning Up**

```bash
# Remove cache files
rm -rf __pycache__/
rm -rf *.pyc

# Clean uploads (keep structure)
rm uploads/*.jpg uploads/*.png uploads/*.jpeg

# Reset database (WARNING: Deletes all data)
rm instance/medications.db
python app.py  # Recreates empty database
```

---

## 📞 Support

### **Getting Help**

1. **Check Documentation**: Review all .md files in the project
2. **Run System Check**: `python final_system_check.py`
3. **Check Logs**: Enable debug mode for detailed errors
4. **GitHub Issues**: Report bugs at repository issues page
5. **Community**: Check discussions and wiki

### **Reporting Issues**

When reporting issues, include:
- Operating system and version
- Python version (`python --version`)
- Error messages (full traceback)
- Steps to reproduce
- System check output

---

**🎉 Congratulations! MEDIMORPH is now installed and ready to help manage medications with AI-powered prescription digitization!**
