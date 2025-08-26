#!/usr/bin/env python3
"""
MongoDB Simulator for MEDIMORPH
This module provides a file-based simulation of MongoDB for testing purposes
when MongoDB is not available locally.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

class MockObjectId:
    """Mock ObjectId for simulation"""
    def __init__(self, oid=None):
        self.oid = oid or str(uuid.uuid4()).replace('-', '')[:24]
    
    def __str__(self):
        return self.oid
    
    def __repr__(self):
        return f"ObjectId('{self.oid}')"

class MockDocument:
    """Mock document class"""
    def __init__(self, **kwargs):
        self.id = MockObjectId()
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.created_at = datetime.utcnow()
    
    def save(self):
        """Simulate saving to database"""
        collection_name = self.__class__.__name__.lower() + 's'
        MockMongoClient.get_instance().save_document(collection_name, self)
        return self
    
    def to_dict(self):
        """Convert to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, MockObjectId):
                result[key] = str(value)
            else:
                result[key] = value
        return result

class MockQuerySet:
    """Mock QuerySet for filtering"""
    def __init__(self, collection_name: str, documents: List[Dict]):
        self.collection_name = collection_name
        self.documents = documents
        self.filters = {}
    
    def filter(self, **kwargs):
        """Apply filters"""
        filtered_docs = []
        for doc in self.documents:
            match = True
            for key, value in kwargs.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                filtered_docs.append(doc)
        
        new_queryset = MockQuerySet(self.collection_name, filtered_docs)
        new_queryset.filters = {**self.filters, **kwargs}
        return new_queryset
    
    def first(self):
        """Get first document"""
        if self.documents:
            return self._dict_to_object(self.documents[0])
        return None
    
    def all(self):
        """Get all documents"""
        return [self._dict_to_object(doc) for doc in self.documents]
    
    def count(self):
        """Count documents"""
        return len(self.documents)
    
    def order_by(self, field):
        """Order documents"""
        reverse = field.startswith('-')
        if reverse:
            field = field[1:]
        
        sorted_docs = sorted(self.documents, 
                           key=lambda x: x.get(field, ''), 
                           reverse=reverse)
        return MockQuerySet(self.collection_name, sorted_docs)
    
    def _dict_to_object(self, doc_dict):
        """Convert dictionary to mock object"""
        obj = MockDocument()
        for key, value in doc_dict.items():
            if key == 'id' or key == '_id':
                obj.id = MockObjectId(value)
            else:
                setattr(obj, key, value)
        return obj

class MockCollection:
    """Mock MongoDB collection"""
    def __init__(self, name: str, db_path: str):
        self.name = name
        self.db_path = db_path
        self.file_path = os.path.join(db_path, f"{name}.json")
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure collection file exists"""
        os.makedirs(self.db_path, exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def _load_documents(self) -> List[Dict]:
        """Load documents from file"""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_documents(self, documents: List[Dict]):
        """Save documents to file"""
        with open(self.file_path, 'w') as f:
            json.dump(documents, f, indent=2, default=str)
    
    def insert_one(self, document: Dict):
        """Insert one document"""
        documents = self._load_documents()
        document['_id'] = str(MockObjectId())
        document['created_at'] = datetime.utcnow().isoformat()
        documents.append(document)
        self._save_documents(documents)
        return type('InsertResult', (), {'inserted_id': document['_id']})()
    
    def find(self, filter_dict: Dict = None):
        """Find documents"""
        documents = self._load_documents()
        if filter_dict:
            filtered_docs = []
            for doc in documents:
                match = True
                for key, value in filter_dict.items():
                    if key not in doc or doc[key] != value:
                        match = False
                        break
                if match:
                    filtered_docs.append(doc)
            return filtered_docs
        return documents
    
    def find_one(self, filter_dict: Dict):
        """Find one document"""
        results = self.find(filter_dict)
        return results[0] if results else None
    
    def count_documents(self, filter_dict: Dict = None):
        """Count documents"""
        return len(self.find(filter_dict or {}))
    
    def update_one(self, filter_dict: Dict, update_dict: Dict):
        """Update one document"""
        documents = self._load_documents()
        for doc in documents:
            match = True
            for key, value in filter_dict.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                if '$set' in update_dict:
                    doc.update(update_dict['$set'])
                doc['updated_at'] = datetime.utcnow().isoformat()
                break
        self._save_documents(documents)
    
    def delete_one(self, filter_dict: Dict):
        """Delete one document"""
        documents = self._load_documents()
        for i, doc in enumerate(documents):
            match = True
            for key, value in filter_dict.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                documents.pop(i)
                break
        self._save_documents(documents)

class MockDatabase:
    """Mock MongoDB database"""
    def __init__(self, name: str, db_path: str):
        self.name = name
        self.db_path = os.path.join(db_path, name)
        self.collections = {}
    
    def __getitem__(self, collection_name: str):
        """Get collection"""
        if collection_name not in self.collections:
            self.collections[collection_name] = MockCollection(collection_name, self.db_path)
        return self.collections[collection_name]
    
    def list_collection_names(self):
        """List collection names"""
        try:
            return [f.replace('.json', '') for f in os.listdir(self.db_path) if f.endswith('.json')]
        except FileNotFoundError:
            return []

class MockMongoClient:
    """Mock MongoDB client"""
    _instance = None
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or "mock://localhost:27017/"
        self.db_path = "mock_mongodb_data"
        self.databases = {}
        MockMongoClient._instance = self
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = MockMongoClient()
        return cls._instance
    
    def __getitem__(self, db_name: str):
        """Get database"""
        if db_name not in self.databases:
            self.databases[db_name] = MockDatabase(db_name, self.db_path)
        return self.databases[db_name]
    
    def list_database_names(self):
        """List database names"""
        try:
            return [d for d in os.listdir(self.db_path) if os.path.isdir(os.path.join(self.db_path, d))]
        except FileNotFoundError:
            return []
    
    def save_document(self, collection_name: str, document: MockDocument):
        """Save document to collection"""
        db = self['medimorph_db']
        collection = db[collection_name]
        doc_dict = document.to_dict()
        collection.insert_one(doc_dict)
    
    def close(self):
        """Close connection (no-op for mock)"""
        pass
    
    def admin(self):
        """Admin interface"""
        return type('Admin', (), {
            'command': lambda self, cmd: {'ok': 1} if cmd == 'ping' else {}
        })()

# Mock MongoEngine classes
class MockUser(MockDocument):
    """Mock User model"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_active = kwargs.get('is_active', True)
    
    def set_password(self, password):
        """Set password hash"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Get user ID for Flask-Login"""
        return str(self.id)
    
    @classmethod
    def objects(cls, **kwargs):
        """Query objects"""
        client = MockMongoClient.get_instance()
        db = client['medimorph_db']
        collection = db['users']
        documents = collection.find(kwargs)
        return MockQuerySet('users', documents)

class MockMedication(MockDocument):
    """Mock Medication model"""
    @classmethod
    def objects(cls, **kwargs):
        """Query objects"""
        client = MockMongoClient.get_instance()
        db = client['medimorph_db']
        collection = db['medications']
        documents = collection.find(kwargs)
        return MockQuerySet('medications', documents)

def init_mock_mongodb():
    """Initialize mock MongoDB"""
    print("🔄 Initializing Mock MongoDB (File-based simulation)...")
    
    try:
        client = MockMongoClient()
        
        # Test basic operations
        db = client['medimorph_db']
        test_collection = db['test']
        
        # Insert test document
        test_doc = {'test': 'data', 'timestamp': datetime.utcnow().isoformat()}
        test_collection.insert_one(test_doc)
        
        # Verify insertion
        found = test_collection.find_one({'test': 'data'})
        if found:
            print("✅ Mock MongoDB initialized successfully")
            print(f"📁 Data stored in: {client.db_path}")
            return True
        else:
            print("❌ Mock MongoDB test failed")
            return False
            
    except Exception as e:
        print(f"❌ Mock MongoDB initialization failed: {e}")
        return False

def create_mock_default_users():
    """Create default users in mock MongoDB"""
    try:
        default_users = [
            {
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User'
            },
            {
                'username': 'karthikrai390@gmail.com',
                'email': 'karthikrai390@gmail.com',
                'password': '123456',
                'first_name': 'Karthik',
                'last_name': 'Rai'
            }
        ]
        
        created_count = 0
        for user_data in default_users:
            # Check if user already exists
            existing_users = MockUser.objects(username=user_data['username'])
            if not existing_users.first():
                user = MockUser(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_active=True
                )
                user.set_password(user_data['password'])
                user.save()
                created_count += 1
                print(f"✅ Created mock user: {user_data['username']}")
        
        if created_count == 0:
            print("ℹ️ All default users already exist in mock MongoDB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating mock default users: {e}")
        return False

def get_mock_database_stats():
    """Get mock database statistics"""
    try:
        client = MockMongoClient.get_instance()
        db = client['medimorph_db']
        
        stats = {}
        collections = ['users', 'medications', 'reminders', 'medication_logs', 'prescription_uploads']
        
        for collection_name in collections:
            try:
                collection = db[collection_name]
                stats[collection_name] = collection.count_documents({})
            except:
                stats[collection_name] = 0
        
        return stats
    except Exception as e:
        print(f"❌ Error getting mock database stats: {e}")
        return None

if __name__ == '__main__':
    # Test mock MongoDB
    print("🧪 Testing Mock MongoDB Simulator")
    print("=" * 40)
    
    if init_mock_mongodb():
        create_mock_default_users()
        stats = get_mock_database_stats()
        if stats:
            print(f"📊 Mock Database Statistics:")
            for collection, count in stats.items():
                print(f"   - {collection}: {count}")
        print("✅ Mock MongoDB is ready for testing!")
    else:
        print("❌ Mock MongoDB test failed")
