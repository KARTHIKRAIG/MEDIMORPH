# 🔧 MEDIMORPH Troubleshooting & FAQ

## 🚨 Common Issues & Solutions

### **🐍 Python & Environment Issues**

#### **Q: "Python is not recognized as an internal or external command"**
**A: Python Installation Issue**
```bash
# Solution 1: Install Python from python.org
# Make sure to check "Add Python to PATH" during installation

# Solution 2: Add Python to PATH manually
# Windows: Add C:\Python311\ to system PATH
# Verify: python --version
```

#### **Q: "No module named 'flask'" after installation**
**A: Virtual Environment Not Activated**
```bash
# Activate virtual environment first
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Then install requirements
pip install -r requirements.txt
```

#### **Q: Virtual environment creation fails**
**A: Missing venv module**
```bash
# Windows:
python -m pip install virtualenv
python -m virtualenv venv

# Linux/macOS:
sudo apt-get install python3-venv  # Ubuntu
python3 -m venv venv
```

---

### **🔍 OCR & Tesseract Issues**

#### **Q: "TesseractNotFoundError: tesseract is not installed"**
**A: Tesseract OCR Not Installed**

**Windows:**
```bash
# Download and install from:
https://github.com/UB-Mannheim/tesseract/wiki

# Add to PATH or update prescription_ocr.py:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

#### **Q: OCR returns empty or incorrect text**
**A: Image Quality Issues**

**Solutions:**
1. **Use high-resolution images** (minimum 300 DPI)
2. **Ensure good lighting** when taking photos
3. **Avoid shadows and glare**
4. **Keep prescription flat** and fully visible
5. **Use supported formats**: JPG, PNG, TIFF

**Image Preprocessing Tips:**
```python
# Manual image enhancement (if needed)
from PIL import Image, ImageEnhance

# Increase contrast
enhancer = ImageEnhance.Contrast(image)
image = enhancer.enhance(2.0)

# Increase sharpness
enhancer = ImageEnhance.Sharpness(image)
image = enhancer.enhance(2.0)
```

#### **Q: "Permission denied" when accessing Tesseract**
**A: File Permissions Issue**
```bash
# Linux/macOS: Fix permissions
sudo chmod +x /usr/bin/tesseract

# Windows: Run as administrator or check antivirus settings
```

---

### **🌐 Web Application Issues**

#### **Q: "Address already in use" error**
**A: Port 5000 is occupied**

**Find and kill process:**
```bash
# Windows:
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# macOS/Linux:
lsof -ti:5000 | xargs kill -9

# Or use different port:
# Edit app.py: socketio.run(app, port=5001)
```

#### **Q: Application starts but can't access in browser**
**A: Firewall or Network Issues**

**Solutions:**
1. **Check firewall settings** - Allow Python/Flask
2. **Try different browsers** - Clear cache
3. **Use 127.0.0.1:5000** instead of localhost:5000
4. **Disable VPN** temporarily
5. **Check proxy settings**

#### **Q: "Internal Server Error" (500)**
**A: Application Error**

**Debug Steps:**
```python
# Enable debug mode in app.py
app.config['DEBUG'] = True

# Check console output for detailed error
# Common causes:
# - Database connection issues
# - Missing files or directories
# - Import errors
```

---

### **🗄️ Database Issues**

#### **Q: "Database is locked" error**
**A: SQLite Database Lock**

**Solutions:**
```bash
# 1. Close all application instances
# 2. Check for zombie processes
ps aux | grep python  # Linux/macOS
tasklist | findstr python  # Windows

# 3. Delete lock file (if exists)
rm instance/medications.db-wal
rm instance/medications.db-shm

# 4. Restart application
python app.py
```

#### **Q: "No such table" error**
**A: Database Not Initialized**

**Solution:**
```bash
# Delete existing database
rm instance/medications.db

# Restart application to recreate tables
python app.py
```

#### **Q: Lost all medication data**
**A: Database Corruption or Deletion**

**Recovery:**
```bash
# Check for backup files
ls instance/medications_backup_*.db

# Restore from backup
cp instance/medications_backup_20240115.db instance/medications.db

# Prevention: Regular backups
cp instance/medications.db instance/medications_backup_$(date +%Y%m%d).db
```

---

### **🔐 Authentication Issues**

#### **Q: Can't login with default credentials**
**A: User Not Created or Wrong Credentials**

**Default Credentials:**
- Username: `testuser` | Password: `testpass123`
- Username: `karthikrai390@gmail.com` | Password: `123456`

**Create New User:**
```python
# Run in Python console
from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    user = User(
        username='newuser',
        email='newuser@example.com',
        password_hash=generate_password_hash('newpassword')
    )
    db.session.add(user)
    db.session.commit()
```

#### **Q: "Session expired" messages**
**A: Session Configuration Issue**

**Solution:**
```python
# In app.py, increase session lifetime
from datetime import timedelta
app.permanent_session_lifetime = timedelta(hours=24)
```

---

### **📱 File Upload Issues**

#### **Q: "File too large" error**
**A: Upload Size Limit Exceeded**

**Solution:**
```python
# In app.py, increase limit
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

#### **Q: Upload fails silently**
**A: Upload Directory Issues**

**Check:**
```bash
# Verify uploads directory exists and is writable
ls -la uploads/
chmod 755 uploads/  # Linux/macOS

# Windows: Check folder permissions in Properties
```

#### **Q: "Unsupported file type" error**
**A: File Format Not Allowed**

**Supported Formats:**
- JPG/JPEG
- PNG
- TIFF
- BMP
- GIF (static)

---

### **🔔 Notification Issues**

#### **Q: Not receiving medication reminders**
**A: Reminder Service Not Running**

**Check:**
```python
# Verify reminder service in console output
# Should see: "🔔 Medication reminder service started"

# Check browser notifications are enabled
# Allow notifications when prompted
```

#### **Q: WebSocket connection fails**
**A: Network or Browser Issues**

**Solutions:**
1. **Check browser console** for WebSocket errors
2. **Disable ad blockers** temporarily
3. **Try different browser**
4. **Check firewall settings**

---

## 🔍 Diagnostic Commands

### **System Health Check**
```bash
# Quick health check
python quick_health_check.py

# Comprehensive system check
python final_system_check.py

# Manual component testing
python -c "import pytesseract; print('Tesseract OK')"
python -c "import flask; print('Flask OK')"
python -c "from app import db; print('Database OK')"
```

### **Debug Information**
```bash
# Python environment info
python --version
pip list
which python

# System info
# Windows:
systeminfo | findstr "OS Name"
# Linux/macOS:
uname -a
```

### **Log Analysis**
```python
# Enable detailed logging in app.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('medimorph.log'),
        logging.StreamHandler()
    ]
)
```

---

## 📊 Performance Issues

### **Q: Application is slow**
**A: Performance Optimization**

**Solutions:**
1. **Reduce image size** before upload
2. **Close unused browser tabs**
3. **Increase system RAM**
4. **Use SSD storage**
5. **Update Python and packages**

### **Q: OCR processing takes too long**
**A: Image Processing Optimization**

**Tips:**
```python
# Optimize image before OCR
from PIL import Image

def optimize_image(image_path):
    with Image.open(image_path) as img:
        # Resize if too large
        if img.width > 2000:
            ratio = 2000 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((2000, new_height))
        
        # Convert to grayscale
        img = img.convert('L')
        return img
```

---

## 🛡️ Security Concerns

### **Q: Is my medical data secure?**
**A: Security Measures**

**MEDIMORPH Security Features:**
- ✅ **Password hashing** with Werkzeug
- ✅ **Session-based authentication**
- ✅ **User data isolation**
- ✅ **Input validation and sanitization**
- ✅ **Local database storage** (no cloud by default)

**Additional Security:**
```python
# Use strong secret key in production
app.config['SECRET_KEY'] = 'your-very-long-random-secret-key'

# Enable HTTPS in production
# Use reverse proxy (nginx) with SSL certificate
```

### **Q: Can others access my prescriptions?**
**A: User Isolation**

**Each user sees only their own data:**
- Database queries filtered by user_id
- File uploads in user-specific directories
- Session-based access control

---

## 🔄 Maintenance & Updates

### **Q: How to backup my data?**
**A: Regular Backups**

```bash
# Backup database
cp instance/medications.db backups/medications_$(date +%Y%m%d).db

# Backup uploaded images
tar -czf backups/uploads_$(date +%Y%m%d).tar.gz uploads/

# Automated backup script (Linux/macOS)
#!/bin/bash
DATE=$(date +%Y%m%d)
cp instance/medications.db backups/medications_$DATE.db
tar -czf backups/uploads_$DATE.tar.gz uploads/
```

### **Q: How to update MEDIMORPH?**
**A: Update Process**

```bash
# 1. Backup current data
cp instance/medications.db instance/medications_backup.db

# 2. Pull latest changes
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt --upgrade

# 4. Run system check
python final_system_check.py

# 5. Restart application
python app.py
```

---

## 📞 Getting Additional Help

### **Before Asking for Help:**
1. ✅ Run `python final_system_check.py`
2. ✅ Check this troubleshooting guide
3. ✅ Review error messages carefully
4. ✅ Try basic solutions (restart, reinstall)

### **When Reporting Issues:**
**Include this information:**
- Operating system and version
- Python version (`python --version`)
- Complete error message
- Steps to reproduce the issue
- Output of system check
- Screenshots (if UI issue)

### **Support Channels:**
- 📖 **Documentation**: All .md files in project
- 🐛 **GitHub Issues**: Report bugs and feature requests
- 💬 **Discussions**: Community help and questions
- 📧 **Email**: For sensitive issues

---

**🎯 Most issues can be resolved by following this guide. MEDIMORPH is designed to be robust and user-friendly!**
