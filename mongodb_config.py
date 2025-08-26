"""
MongoDB Configuration and Models for MEDIMORPH
This module provides MongoDB integration using MongoEngine ODM
"""

from mongoengine import Document, EmbeddedDocument, fields, connect, disconnect
from flask_login import UserMixin
from datetime import datetime, time
from werkzeug.security import generate_password_hash, check_password_hash
import os

# MongoDB Configuration
MONGODB_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "medimorph_db"

def init_mongodb(app=None):
    """Initialize MongoDB connection"""
    try:
        # Disconnect any existing connections
        disconnect()
        
        # Connect to MongoDB
        connect(
            db=DATABASE_NAME,
            host=MONGODB_URI,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,  # 10 second timeout
            socketTimeoutMS=20000,   # 20 second timeout
            maxPoolSize=50,
            retryWrites=True
        )
        
        print(f"✅ Connected to MongoDB: {MONGODB_URI}{DATABASE_NAME}")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    try:
        from pymongo import MongoClient
        
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        
        # List databases
        db_list = client.list_database_names()
        print(f"📊 Available databases: {db_list}")
        
        # Get database info
        db = client[DATABASE_NAME]
        collections = db.list_collection_names()
        print(f"📁 Collections in {DATABASE_NAME}: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection test failed: {e}")
        return False

# MongoDB Document Models using MongoEngine

class User(Document, UserMixin):
    """User model for MongoDB"""
    
    # Basic user information
    username = fields.StringField(required=True, unique=True, max_length=80)
    email = fields.EmailField(required=True, unique=True, max_length=120)
    password_hash = fields.StringField(required=True, max_length=200)
    
    # Personal information
    first_name = fields.StringField(max_length=50)
    last_name = fields.StringField(max_length=50)
    phone = fields.StringField(max_length=20)
    date_of_birth = fields.DateTimeField()
    
    # Account status
    is_active = fields.BooleanField(default=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    last_login = fields.DateTimeField()
    
    # MongoDB collection name
    meta = {
        'collection': 'users',
        'indexes': ['username', 'email']
    }
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return str(self.id)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Medication(Document):
    """Medication model for MongoDB"""
    
    # User reference
    user_id = fields.ObjectIdField(required=True)
    user_username = fields.StringField(required=True)  # Denormalized for easier queries
    
    # Medication information
    name = fields.StringField(required=True, max_length=100)
    dosage = fields.StringField(required=True, max_length=50)
    frequency = fields.StringField(required=True, max_length=50)
    instructions = fields.StringField(max_length=500)
    duration = fields.StringField(max_length=100)
    
    # Dates
    start_date = fields.DateTimeField(default=datetime.utcnow)
    end_date = fields.DateTimeField()
    
    # Status
    is_active = fields.BooleanField(default=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    # Additional metadata
    source = fields.StringField(default='manual')  # 'manual', 'ocr', 'prescription'
    confidence_score = fields.FloatField(default=1.0)
    
    # MongoDB collection name
    meta = {
        'collection': 'medications',
        'indexes': ['user_id', 'user_username', 'name', 'is_active']
    }
    
    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def to_dict(self):
        """Convert medication to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'name': self.name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'instructions': self.instructions,
            'duration': self.duration,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'source': self.source,
            'confidence_score': self.confidence_score
        }

class Reminder(Document):
    """Reminder model for MongoDB"""
    
    # References
    medication_id = fields.ObjectIdField(required=True)
    user_id = fields.ObjectIdField(required=True)
    
    # Reminder details
    time = fields.StringField(required=True)  # Store as "HH:MM" format
    days_of_week = fields.ListField(fields.StringField(), default=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
    
    # Status
    is_active = fields.BooleanField(default=True)
    last_sent = fields.DateTimeField()
    next_due = fields.DateTimeField()
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    # MongoDB collection name
    meta = {
        'collection': 'reminders',
        'indexes': ['user_id', 'medication_id', 'is_active', 'next_due']
    }
    
    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def to_dict(self):
        """Convert reminder to dictionary"""
        return {
            'id': str(self.id),
            'medication_id': str(self.medication_id),
            'user_id': str(self.user_id),
            'time': self.time,
            'days_of_week': self.days_of_week,
            'is_active': self.is_active,
            'last_sent': self.last_sent.isoformat() if self.last_sent else None,
            'next_due': self.next_due.isoformat() if self.next_due else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MedicationLog(Document):
    """Medication log model for MongoDB"""
    
    # References
    user_id = fields.ObjectIdField(required=True)
    medication_id = fields.ObjectIdField(required=True)
    
    # Log details
    taken_at = fields.DateTimeField(default=datetime.utcnow)
    dosage_taken = fields.StringField(max_length=50)
    notes = fields.StringField(max_length=500)
    
    # Status
    status = fields.StringField(choices=['taken', 'missed', 'delayed'], default='taken')
    reminder_id = fields.ObjectIdField()  # Reference to reminder that triggered this
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    # MongoDB collection name
    meta = {
        'collection': 'medication_logs',
        'indexes': ['user_id', 'medication_id', 'taken_at', 'status']
    }
    
    def to_dict(self):
        """Convert log to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'medication_id': str(self.medication_id),
            'taken_at': self.taken_at.isoformat() if self.taken_at else None,
            'dosage_taken': self.dosage_taken,
            'notes': self.notes,
            'status': self.status,
            'reminder_id': str(self.reminder_id) if self.reminder_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PrescriptionUpload(Document):
    """Prescription upload model for MongoDB"""
    
    # User reference
    user_id = fields.ObjectIdField(required=True)
    
    # File information
    filename = fields.StringField(required=True)
    original_filename = fields.StringField(required=True)
    file_path = fields.StringField(required=True)
    file_size = fields.IntField()
    mime_type = fields.StringField()
    
    # OCR results
    extracted_text = fields.StringField()
    ocr_confidence = fields.FloatField()
    processing_time = fields.FloatField()
    
    # Extracted medications
    medications_found = fields.IntField(default=0)
    medications_added = fields.IntField(default=0)
    
    # Status
    processing_status = fields.StringField(choices=['pending', 'processing', 'completed', 'failed'], default='pending')
    error_message = fields.StringField()
    
    # Timestamps
    uploaded_at = fields.DateTimeField(default=datetime.utcnow)
    processed_at = fields.DateTimeField()
    
    # MongoDB collection name
    meta = {
        'collection': 'prescription_uploads',
        'indexes': ['user_id', 'uploaded_at', 'processing_status']
    }
    
    def to_dict(self):
        """Convert upload to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'extracted_text': self.extracted_text,
            'ocr_confidence': self.ocr_confidence,
            'processing_time': self.processing_time,
            'medications_found': self.medications_found,
            'medications_added': self.medications_added,
            'processing_status': self.processing_status,
            'error_message': self.error_message,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

# Utility functions for MongoDB operations

def create_default_users():
    """Create default users in MongoDB"""
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
            existing_user = User.objects(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_active=True
                )
                user.set_password(user_data['password'])
                user.save()
                created_count += 1
                print(f"✅ Created MongoDB user: {user_data['username']}")
        
        if created_count == 0:
            print("ℹ️ All default users already exist in MongoDB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating default users: {e}")
        return False

def get_database_stats():
    """Get MongoDB database statistics"""
    try:
        stats = {
            'users': User.objects.count(),
            'medications': Medication.objects.count(),
            'reminders': Reminder.objects.count(),
            'medication_logs': MedicationLog.objects.count(),
            'prescription_uploads': PrescriptionUpload.objects.count()
        }
        return stats
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
        return None
