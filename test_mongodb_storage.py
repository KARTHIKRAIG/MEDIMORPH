#!/usr/bin/env python3
"""
MongoDB Storage Test for MEDIMORPH
This script tests MongoDB integration and data storage functionality
"""

import requests
import json
import time
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# Configuration
BASE_URL = 'http://localhost:5000'
MONGODB_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = 'medimorph_db'

TEST_USER = {
    'username': 'testuser',
    'password': 'testpass123'
}

def test_mongodb_connection():
    """Test direct MongoDB connection"""
    print("🔍 Testing direct MongoDB connection...")
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        # Get database info
        db = client[DATABASE_NAME]
        collections = db.list_collection_names()
        
        print(f"✅ MongoDB connection successful")
        print(f"📊 Database: {DATABASE_NAME}")
        print(f"📁 Collections: {collections}")
        
        # Get collection stats
        for collection_name in collections:
            count = db[collection_name].count_documents({})
            print(f"   - {collection_name}: {count} documents")
        
        client.close()
        return True
        
    except ServerSelectionTimeoutError:
        print("❌ MongoDB connection failed - server not available")
        return False
    except Exception as e:
        print(f"❌ MongoDB connection test failed: {e}")
        return False

def test_app_database_status():
    """Test application database status endpoint"""
    print("🔍 Testing application database status...")
    try:
        response = requests.get(f'{BASE_URL}/database-status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database Status: {data['status']}")
            print(f"🗄️ Database Type: {data['database_type']}")
            print(f"🔗 Connection: {data['connection_string']}")
            print(f"📊 Statistics:")
            for key, value in data['statistics'].items():
                print(f"   - {key}: {value}")
            return True
        else:
            print(f"❌ Database status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database status test failed: {e}")
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
                print(f"👤 User ID: {data['user']['id']}")
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

def test_mongodb_medication_storage(session):
    """Test medication storage in MongoDB"""
    print("💊 Testing MongoDB medication storage...")
    
    # Test medications with MongoDB-specific features
    test_medications = [
        {
            'name': 'MongoDB Test Aspirin',
            'dosage': '100mg',
            'frequency': 'Once daily',
            'instructions': 'Take with food - MongoDB test',
            'duration': '30 days'
        },
        {
            'name': 'MongoDB Test Metformin',
            'dosage': '500mg',
            'frequency': 'Twice daily',
            'instructions': 'Take before meals - MongoDB test',
            'duration': '90 days'
        },
        {
            'name': 'MongoDB Test Lisinopril',
            'dosage': '10mg',
            'frequency': 'Once daily',
            'instructions': 'Take in morning - MongoDB test',
            'duration': '60 days'
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
    
    # Retrieve medications to verify MongoDB storage
    try:
        print("  📋 Retrieving medications from MongoDB...")
        response = session.get(f'{BASE_URL}/medications', timeout=5)
        
        if response.status_code == 200:
            medications = response.json()
            print(f"  ✅ Retrieved {len(medications)} medications from MongoDB")
            
            # Show MongoDB-specific fields
            for med in medications:
                print(f"    - {med['name']}: {med['dosage']}, {med['frequency']}")
                print(f"      ID: {med['id']}, Source: {med.get('source', 'unknown')}")
                print(f"      Confidence: {med.get('confidence_score', 'N/A')}")
            
            return len(medications) > 0
        else:
            print(f"  ❌ Failed to retrieve medications: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error retrieving medications: {e}")
        return False

def test_direct_mongodb_queries():
    """Test direct MongoDB queries to verify data storage"""
    print("🔍 Testing direct MongoDB queries...")
    
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        
        # Query users collection
        users_collection = db['users']
        users = list(users_collection.find({}))
        print(f"  👥 Users in MongoDB: {len(users)}")
        
        for user in users:
            print(f"    - {user['username']} ({user['email']})")
        
        # Query medications collection
        medications_collection = db['medications']
        medications = list(medications_collection.find({}))
        print(f"  💊 Medications in MongoDB: {len(medications)}")
        
        # Show recent medications
        recent_meds = list(medications_collection.find({}).sort('created_at', -1).limit(5))
        for med in recent_meds:
            print(f"    - {med['name']}: {med['dosage']} ({med.get('source', 'unknown')})")
        
        # Query other collections
        for collection_name in ['reminders', 'medication_logs', 'prescription_uploads']:
            if collection_name in db.list_collection_names():
                count = db[collection_name].count_documents({})
                print(f"  📊 {collection_name}: {count} documents")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Direct MongoDB query failed: {e}")
        return False

def test_mongodb_data_persistence():
    """Test that data persists in MongoDB across sessions"""
    print("💾 Testing MongoDB data persistence...")
    
    # Create new session to simulate app restart
    new_session = requests.Session()
    
    if not login_user(new_session):
        return False
    
    try:
        response = new_session.get(f'{BASE_URL}/medications', timeout=5)
        if response.status_code == 200:
            medications = response.json()
            print(f"  ✅ Data persisted in MongoDB: {len(medications)} medications found")
            
            # Verify MongoDB-specific fields are preserved
            mongodb_test_meds = [med for med in medications if 'MongoDB Test' in med['name']]
            print(f"  🧪 MongoDB test medications: {len(mongodb_test_meds)}")
            
            return len(medications) > 0
        else:
            print(f"  ❌ Failed to retrieve persisted data: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Persistence test failed: {e}")
        return False

def test_mongodb_performance():
    """Test MongoDB performance with bulk operations"""
    print("⚡ Testing MongoDB performance...")
    
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        
        # Test bulk insert performance
        test_collection = db['performance_test']
        
        # Insert test documents
        start_time = time.time()
        test_docs = [{'test_id': i, 'data': f'test_data_{i}', 'timestamp': datetime.utcnow()} for i in range(1000)]
        result = test_collection.insert_many(test_docs)
        insert_time = time.time() - start_time
        
        print(f"  ✅ Inserted {len(result.inserted_ids)} documents in {insert_time:.2f} seconds")
        print(f"  📊 Insert rate: {len(result.inserted_ids)/insert_time:.0f} docs/second")
        
        # Test bulk query performance
        start_time = time.time()
        found_docs = list(test_collection.find({'test_id': {'$lt': 100}}))
        query_time = time.time() - start_time
        
        print(f"  ✅ Queried {len(found_docs)} documents in {query_time:.3f} seconds")
        
        # Clean up test data
        test_collection.drop()
        print(f"  🧹 Cleaned up performance test data")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Performance test failed: {e}")
        return False

def main():
    """Run all MongoDB storage tests"""
    print("🧪 MEDIMORPH MongoDB Storage Test")
    print("=" * 50)
    
    # Wait for application to start
    print("⏳ Waiting for application to start...")
    time.sleep(2)
    
    # Test direct MongoDB connection
    mongodb_connection = test_mongodb_connection()
    if not mongodb_connection:
        print("❌ MongoDB connection failed. Make sure MongoDB is running.")
        return False
    
    # Test application database status
    app_db_status = test_app_database_status()
    
    # Create session for authenticated requests
    session = requests.Session()
    
    # Login
    login_success = login_user(session)
    if not login_success:
        print("❌ Login failed. Cannot proceed with authenticated tests.")
        return False
    
    # Test MongoDB medication storage
    medication_test = test_mongodb_medication_storage(session)
    
    # Test direct MongoDB queries
    direct_query_test = test_direct_mongodb_queries()
    
    # Test data persistence
    persistence_test = test_mongodb_data_persistence()
    
    # Test MongoDB performance
    performance_test = test_mongodb_performance()
    
    # Final database status
    print("\n📊 Final MongoDB Status:")
    test_mongodb_connection()
    test_app_database_status()
    
    # Summary
    print("\n🎯 MongoDB Test Results Summary:")
    print(f"  MongoDB Connection: {'✅ PASS' if mongodb_connection else '❌ FAIL'}")
    print(f"  App Database Status: {'✅ PASS' if app_db_status else '❌ FAIL'}")
    print(f"  User Authentication: {'✅ PASS' if login_success else '❌ FAIL'}")
    print(f"  Medication Storage: {'✅ PASS' if medication_test else '❌ FAIL'}")
    print(f"  Direct MongoDB Queries: {'✅ PASS' if direct_query_test else '❌ FAIL'}")
    print(f"  Data Persistence: {'✅ PASS' if persistence_test else '❌ FAIL'}")
    print(f"  Performance Test: {'✅ PASS' if performance_test else '❌ FAIL'}")
    
    all_passed = all([
        mongodb_connection, app_db_status, login_success, 
        medication_test, direct_query_test, persistence_test, performance_test
    ])
    
    if all_passed:
        print("\n🎉 ALL MONGODB TESTS PASSED! MongoDB integration is working perfectly.")
        print("💾 All data is being stored in MongoDB successfully!")
    else:
        print("\n⚠️ Some MongoDB tests failed. Check the output above for details.")
    
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
