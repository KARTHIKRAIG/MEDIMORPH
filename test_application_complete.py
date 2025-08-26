#!/usr/bin/env python3
"""
MEDIMORPH - Complete Application Test
Comprehensive testing before GitHub deployment
"""

import requests
import json
import time
import os
import sys

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️ {message}")

def test_application_startup():
    print_header("APPLICATION STARTUP TEST")
    
    base_url = "http://localhost:5000"
    max_attempts = 10
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print_success(f"Application started successfully (attempt {attempt + 1})")
                return True
        except requests.exceptions.RequestException:
            print_info(f"Waiting for application to start... (attempt {attempt + 1})")
            time.sleep(2)
    
    print_error("Application failed to start within expected time")
    return False

def test_authentication_system():
    print_header("AUTHENTICATION SYSTEM TEST")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Test 1: Login page accessibility
    try:
        response = session.get(f"{base_url}/login")
        if response.status_code == 200:
            print_success("Login page accessible")
        else:
            print_error(f"Login page failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Login page error: {e}")
        return False
    
    # Test 2: Valid login
    try:
        login_data = {'username': 'testuser', 'password': 'testpass123'}
        response = session.post(f"{base_url}/login", 
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(login_data))
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success(f"Login successful for user: {result['user']['username']}")
            else:
                print_error(f"Login failed: {result.get('message')}")
                return False
        else:
            print_error(f"Login request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Login test error: {e}")
        return False
    
    # Test 3: Dashboard access after login
    try:
        response = session.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            print_success("Dashboard accessible after login")
        else:
            print_error(f"Dashboard access failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Dashboard test error: {e}")
        return False
    
    # Test 4: Invalid login
    try:
        invalid_session = requests.Session()
        login_data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = invalid_session.post(f"{base_url}/login", 
                                       headers={'Content-Type': 'application/json'},
                                       data=json.dumps(login_data))
        
        if response.status_code == 401:
            print_success("Invalid login properly rejected")
        else:
            print_error("Invalid login not properly handled")
            return False
    except Exception as e:
        print_error(f"Invalid login test error: {e}")
        return False
    
    return session

def test_medication_system(session):
    print_header("MEDICATION SYSTEM TEST")
    
    base_url = "http://localhost:5000"
    
    # Test 1: Get medications
    try:
        response = session.get(f"{base_url}/medications")
        if response.status_code == 200:
            medications = response.json()
            print_success(f"Medications API working - Found {len(medications)} medications")
            
            # Check for user isolation (testuser should have specific medications)
            aspirin_count = sum(1 for med in medications if 'aspirin' in med['name'].lower())
            if aspirin_count == 0:
                print_success("User isolation working - testuser has no Aspirin")
            else:
                print_error(f"User isolation issue - testuser has {aspirin_count} Aspirin entries")
                return False
                
        else:
            print_error(f"Medications API failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Medications API error: {e}")
        return False
    
    # Test 2: Get reminders
    try:
        response = session.get(f"{base_url}/reminders")
        if response.status_code == 200:
            reminders = response.json()
            print_success(f"Reminders API working - Found {len(reminders)} reminders")
        else:
            print_error(f"Reminders API failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Reminders API error: {e}")
        return False
    
    # Test 3: User info API
    try:
        response = session.get(f"{base_url}/api/user-info")
        if response.status_code == 200:
            user_info = response.json()
            if user_info.get('success'):
                user = user_info['user']
                print_success(f"User info API working - User: {user['username']}")
            else:
                print_error("User info API returned failure")
                return False
        else:
            print_error(f"User info API failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"User info API error: {e}")
        return False
    
    return True

def test_file_upload_system(session):
    print_header("FILE UPLOAD SYSTEM TEST")
    
    base_url = "http://localhost:5000"
    
    # Check if test image exists
    test_images = ['uploads/prescription.jpg', 'uploads/priscription.jpg']
    test_image = None
    
    for img in test_images:
        if os.path.exists(img):
            test_image = img
            break
    
    if not test_image:
        print_error("No test prescription image found")
        return False
    
    try:
        with open(test_image, 'rb') as f:
            files = {'file': (os.path.basename(test_image), f, 'image/jpeg')}
            response = session.post(f"{base_url}/upload-prescription", files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_success(f"File upload successful - Extracted {len(result.get('medications', []))} medications")
            else:
                print_error(f"File upload failed: {result.get('message')}")
                return False
        else:
            print_error(f"File upload request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"File upload test error: {e}")
        return False
    
    return True

def test_api_endpoints(session):
    print_header("API ENDPOINTS TEST")
    
    base_url = "http://localhost:5000"
    
    endpoints = [
        ('/health', 'Health Check'),
        ('/medication-report', 'Medication Report'),
        ('/debug/session', 'Debug Session')
    ]
    
    all_passed = True
    
    for endpoint, name in endpoints:
        try:
            response = session.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                print_success(f"{name}: {response.status_code}")
            else:
                print_error(f"{name}: {response.status_code}")
                all_passed = False
        except Exception as e:
            print_error(f"{name}: Error - {e}")
            all_passed = False
    
    return all_passed

def test_database_integrity():
    print_header("DATABASE INTEGRITY TEST")
    
    db_path = os.path.join('instance', 'medications.db')
    if not os.path.exists(db_path):
        print_error("Database file not found")
        return False
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['user', 'medication', 'reminder', 'medication_log']
        for table in required_tables:
            if table in tables:
                print_success(f"Table exists: {table}")
            else:
                print_error(f"Missing table: {table}")
                return False
        
        # Check data integrity
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        print_success(f"Users in database: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM medication WHERE is_active = 1")
        med_count = cursor.fetchone()[0]
        print_success(f"Active medications: {med_count}")
        
        cursor.execute("SELECT COUNT(*) FROM reminder WHERE is_active = 1")
        reminder_count = cursor.fetchone()[0]
        print_success(f"Active reminders: {reminder_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Database integrity error: {e}")
        return False

def test_core_files():
    print_header("CORE FILES TEST")
    
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
    
    all_exist = True
    
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print_success(f"{file} ({size} bytes)")
        else:
            print_error(f"Missing: {file}")
            all_exist = False
    
    # Check templates
    template_files = ['login.html', 'register.html', 'dashboard.html', 'index.html']
    for template in template_files:
        template_path = os.path.join('templates', template)
        if os.path.exists(template_path):
            print_success(f"Template: {template}")
        else:
            print_error(f"Missing template: {template}")
            all_exist = False
    
    return all_exist

def main():
    print("🚀 MEDIMORPH - COMPLETE APPLICATION TEST")
    print("=" * 60)
    print("Testing all components before GitHub deployment...")
    
    # Wait for application to start
    time.sleep(3)
    
    tests = []
    
    # Core system tests
    tests.append(("Application Startup", test_application_startup()))
    tests.append(("Core Files", test_core_files()))
    tests.append(("Database Integrity", test_database_integrity()))
    
    # Application functionality tests
    session = test_authentication_system()
    if session:
        tests.append(("Authentication System", True))
        tests.append(("Medication System", test_medication_system(session)))
        tests.append(("File Upload System", test_file_upload_system(session)))
        tests.append(("API Endpoints", test_api_endpoints(session)))
    else:
        tests.append(("Authentication System", False))
        tests.append(("Medication System", False))
        tests.append(("File Upload System", False))
        tests.append(("API Endpoints", False))
    
    # Results summary
    print_header("TEST RESULTS SUMMARY")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        if result:
            print_success(f"{test_name}")
            passed += 1
        else:
            print_error(f"{test_name}")
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("🎉 ALL TESTS PASSED! MEDIMORPH is ready for GitHub deployment!")
        return True
    else:
        print_error(f"❌ {total - passed} tests failed. Please fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
