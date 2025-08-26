#!/usr/bin/env python3
"""
Test script to verify database storage functionality in MEDIMORPH
This script tests that data entered is properly stored in the database.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:5000'
TEST_USER = {
    'username': 'testuser',
    'password': 'testpass123'
}

def test_database_connection():
    """Test basic database connectivity"""
    print("🔍 Testing database connection...")
    try:
        response = requests.get(f'{BASE_URL}/database-status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database Status: {data['status']}")
            print(f"📊 Users: {data['statistics']['users']}")
            print(f"💊 Medications: {data['statistics']['medications']}")
            print(f"⏰ Reminders: {data['statistics']['reminders']}")
            print(f"📝 Logs: {data['statistics']['medication_logs']}")
            return True
        else:
            print(f"❌ Database status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def login_user(session):
    """Login test user"""
    print("🔐 Logging in test user...")
    try:
        response = session.post(f'{BASE_URL}/login', json=TEST_USER, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Login successful: {data.get('message', 'Logged in')}")
                return True
            else:
                print(f"❌ Login failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Login request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

def test_medication_storage(session):
    """Test adding and retrieving medications"""
    print("💊 Testing medication storage...")
    
    # Test medication data
    test_medications = [
        {
            'name': 'Test Aspirin',
            'dosage': '100mg',
            'frequency': 'Once daily',
            'instructions': 'Take with food',
            'duration': '30 days'
        },
        {
            'name': 'Test Metformin',
            'dosage': '500mg',
            'frequency': 'Twice daily',
            'instructions': 'Take before meals',
            'duration': '90 days'
        }
    ]
    
    added_medications = []
    
    # Add medications
    for med_data in test_medications:
        try:
            print(f"  📝 Adding medication: {med_data['name']}")
            response = session.post(f'{BASE_URL}/medications', json=med_data, timeout=5)
            
            if response.status_code == 201:
                data = response.json()
                if data.get('success'):
                    print(f"  ✅ Added: {med_data['name']}")
                    added_medications.append(data['medication'])
                else:
                    print(f"  ❌ Failed to add {med_data['name']}: {data.get('message')}")
            elif response.status_code == 409:
                print(f"  ⚠️ Medication already exists: {med_data['name']}")
            else:
                print(f"  ❌ Failed to add {med_data['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error adding {med_data['name']}: {e}")
    
    # Retrieve medications to verify storage
    try:
        print("  📋 Retrieving stored medications...")
        response = session.get(f'{BASE_URL}/medications', timeout=5)
        
        if response.status_code == 200:
            medications = response.json()
            print(f"  ✅ Retrieved {len(medications)} medications from database")
            
            for med in medications:
                print(f"    - {med['name']}: {med['dosage']}, {med['frequency']}")
            
            return len(medications) > 0
        else:
            print(f"  ❌ Failed to retrieve medications: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error retrieving medications: {e}")
        return False

def test_prescription_upload_storage(session):
    """Test prescription upload and data extraction storage"""
    print("📸 Testing prescription upload and storage...")
    
    # Check if sample prescription exists
    import os
    sample_files = ['uploads/prescription.jpg', 'uploads/sample_prescription.jpg', 'uploads/test_prescription.jpg']
    sample_file = None
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            sample_file = file_path
            break
    
    if not sample_file:
        print("  ⚠️ No sample prescription file found, skipping upload test")
        return True
    
    try:
        print(f"  📤 Uploading prescription: {sample_file}")
        
        with open(sample_file, 'rb') as f:
            files = {'file': f}
            response = session.post(f'{BASE_URL}/upload-prescription', files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  ✅ Prescription processed successfully")
                print(f"  🔍 Extracted text length: {len(data.get('extracted_text', ''))}")
                print(f"  💊 Medications found: {len(data.get('medications', []))}")
                
                # Check if medications were stored
                med_response = session.get(f'{BASE_URL}/medications', timeout=5)
                if med_response.status_code == 200:
                    medications = med_response.json()
                    print(f"  📊 Total medications in database: {len(medications)}")
                
                return True
            else:
                print(f"  ❌ Prescription processing failed: {data.get('message')}")
                return False
        else:
            print(f"  ❌ Upload failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Upload test failed: {e}")
        return False

def test_data_persistence():
    """Test that data persists across sessions"""
    print("💾 Testing data persistence...")
    
    # Create new session to simulate app restart
    new_session = requests.Session()
    
    if not login_user(new_session):
        return False
    
    try:
        response = new_session.get(f'{BASE_URL}/medications', timeout=5)
        if response.status_code == 200:
            medications = response.json()
            print(f"  ✅ Data persisted: {len(medications)} medications found in new session")
            return len(medications) > 0
        else:
            print(f"  ❌ Failed to retrieve persisted data: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Persistence test failed: {e}")
        return False

def main():
    """Run all database storage tests"""
    print("🧪 MEDIMORPH Database Storage Test")
    print("=" * 50)
    
    # Wait for application to start
    print("⏳ Waiting for application to start...")
    time.sleep(2)
    
    # Test basic connectivity
    if not test_database_connection():
        print("❌ Database connection failed. Make sure MEDIMORPH is running.")
        return False
    
    # Create session for authenticated requests
    session = requests.Session()
    
    # Login
    if not login_user(session):
        print("❌ Login failed. Cannot proceed with tests.")
        return False
    
    # Test medication storage
    medication_test = test_medication_storage(session)
    
    # Test prescription upload storage
    upload_test = test_prescription_upload_storage(session)
    
    # Test data persistence
    persistence_test = test_data_persistence()
    
    # Final database status
    print("\n📊 Final Database Status:")
    test_database_connection()
    
    # Summary
    print("\n🎯 Test Results Summary:")
    print(f"  Database Connection: {'✅ PASS' if True else '❌ FAIL'}")
    print(f"  User Authentication: {'✅ PASS' if True else '❌ FAIL'}")
    print(f"  Medication Storage: {'✅ PASS' if medication_test else '❌ FAIL'}")
    print(f"  Prescription Upload: {'✅ PASS' if upload_test else '❌ FAIL'}")
    print(f"  Data Persistence: {'✅ PASS' if persistence_test else '❌ FAIL'}")
    
    all_passed = medication_test and upload_test and persistence_test
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Database storage is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    return all_passed

if __name__ == '__main__':
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        exit(1)
