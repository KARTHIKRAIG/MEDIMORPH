#!/usr/bin/env python3
"""
MEDIMORPH - Final System Check
Comprehensive verification before GitHub deployment
"""

import os
import sys
import requests
import json
import sqlite3
from datetime import datetime
import subprocess
import time

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️ {message}")

def check_python_environment():
    print_header("PYTHON ENVIRONMENT CHECK")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 11):
        print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print_error(f"Python {python_version.major}.{python_version.minor} - Requires 3.11+")
        return False
    
    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success("Virtual environment active")
    else:
        print_warning("Virtual environment not detected")
    
    # Check required packages
    required_packages = [
        'flask', 'flask-sqlalchemy', 'flask-login', 'flask-cors', 
        'flask-socketio', 'pillow', 'pytesseract', 'werkzeug', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"Package: {package}")
        except ImportError:
            missing_packages.append(package)
            print_error(f"Missing package: {package}")
    
    return len(missing_packages) == 0

def check_tesseract():
    print_header("TESSERACT OCR CHECK")
    
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print_success(f"Tesseract installed: {version_line}")
            return True
        else:
            print_error("Tesseract not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_error("Tesseract not found in PATH")
        return False

def check_file_structure():
    print_header("FILE STRUCTURE CHECK")
    
    required_files = [
        'app.py',
        'ai_processor.py', 
        'medication_reminder.py',
        'prescription_ocr.py',
        'requirements.txt',
        'README.md',
        'SYSTEM_DOCUMENTATION.md',
        'QUICK_START_GUIDE.md'
    ]
    
    required_dirs = [
        'templates',
        'uploads', 
        'venv',
        'instance'
    ]
    
    all_good = True
    
    for file in required_files:
        if os.path.exists(file):
            print_success(f"File: {file}")
        else:
            print_error(f"Missing file: {file}")
            all_good = False
    
    for dir in required_dirs:
        if os.path.exists(dir):
            print_success(f"Directory: {dir}")
        else:
            print_error(f"Missing directory: {dir}")
            all_good = False
    
    # Check templates
    template_files = ['login.html', 'register.html', 'dashboard.html', 'index.html']
    for template in template_files:
        template_path = os.path.join('templates', template)
        if os.path.exists(template_path):
            print_success(f"Template: {template}")
        else:
            print_error(f"Missing template: {template}")
            all_good = False
    
    return all_good

def check_database():
    print_header("DATABASE CHECK")
    
    db_path = os.path.join('instance', 'medications.db')
    if not os.path.exists(db_path):
        print_error("Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['user', 'medication', 'reminder', 'medication_log']
        for table in required_tables:
            if table in tables:
                print_success(f"Table: {table}")
            else:
                print_error(f"Missing table: {table}")
        
        # Check user count
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print_success(f"Users in database: {user_count}")
        
        # Check medication count
        cursor.execute("SELECT COUNT(*) FROM medication")
        med_count = cursor.fetchone()[0]
        print_success(f"Medications in database: {med_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Database error: {e}")
        return False

def start_application():
    print_header("STARTING APPLICATION")
    
    try:
        # Start Flask app in background
        process = subprocess.Popen([
            sys.executable, 'app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for app to start
        print("⏳ Starting Flask application...")
        time.sleep(5)
        
        return process
    except Exception as e:
        print_error(f"Failed to start application: {e}")
        return None

def test_application_endpoints():
    print_header("APPLICATION ENDPOINT TESTS")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Test health endpoint
    try:
        response = session.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print_success("Health endpoint working")
        else:
            print_error(f"Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health endpoint error: {e}")
        return False
    
    # Test login page
    try:
        response = session.get(f"{base_url}/login", timeout=10)
        if response.status_code == 200:
            print_success("Login page accessible")
        else:
            print_error(f"Login page failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Login page error: {e}")
        return False
    
    # Test login functionality
    try:
        login_data = {'username': 'testuser', 'password': 'testpass123'}
        response = session.post(f"{base_url}/login", 
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(login_data), timeout=10)
        
        if response.status_code == 200 and response.json().get('success'):
            print_success("Login functionality working")
        else:
            print_error("Login functionality failed")
            return False
    except Exception as e:
        print_error(f"Login test error: {e}")
        return False
    
    # Test dashboard access
    try:
        response = session.get(f"{base_url}/dashboard", timeout=10)
        if response.status_code == 200:
            print_success("Dashboard accessible after login")
        else:
            print_error(f"Dashboard access failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Dashboard test error: {e}")
        return False
    
    # Test medications API
    try:
        response = session.get(f"{base_url}/medications", timeout=10)
        if response.status_code == 200:
            medications = response.json()
            print_success(f"Medications API working - {len(medications)} medications")
        else:
            print_error(f"Medications API failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Medications API error: {e}")
        return False
    
    return True

def check_git_status():
    print_header("GIT REPOSITORY CHECK")
    
    try:
        # Check if git is initialized
        result = subprocess.run(['git', 'status'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print_success("Git repository initialized")
            
            # Check for uncommitted changes
            if "nothing to commit" in result.stdout:
                print_success("No uncommitted changes")
            else:
                print_warning("Uncommitted changes detected")
            
            return True
        else:
            print_error("Git repository not initialized")
            return False
    except Exception as e:
        print_error(f"Git check error: {e}")
        return False

def main():
    print("🚀 MEDIMORPH - FINAL SYSTEM CHECK")
    print("=" * 60)
    print("Verifying all components before GitHub deployment...")
    
    checks = []
    
    # Run all checks
    checks.append(("Python Environment", check_python_environment()))
    checks.append(("Tesseract OCR", check_tesseract()))
    checks.append(("File Structure", check_file_structure()))
    checks.append(("Database", check_database()))
    
    # Start application for testing
    app_process = start_application()
    if app_process:
        checks.append(("Application Endpoints", test_application_endpoints()))
        
        # Stop application
        app_process.terminate()
        app_process.wait()
    else:
        checks.append(("Application Endpoints", False))
    
    checks.append(("Git Repository", check_git_status()))
    
    # Summary
    print_header("FINAL SUMMARY")
    
    passed = 0
    total = len(checks)
    
    for check_name, result in checks:
        if result:
            print_success(f"{check_name}")
            passed += 1
        else:
            print_error(f"{check_name}")
    
    print(f"\n📊 RESULTS: {passed}/{total} checks passed")
    
    if passed == total:
        print_success("🎉 ALL SYSTEMS GO! Ready for GitHub deployment!")
        return True
    else:
        print_error(f"❌ {total - passed} issues need to be resolved before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
