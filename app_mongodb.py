#!/usr/bin/env python3
"""
MEDIMORPH - AI-Powered Prescription Digitization & Medication Reminder System
MongoDB Version

This version uses MongoDB instead of SQLite for data storage.
Connection string: mongodb://localhost:27017/
Database: medimorph_db
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import threading
import time
import json
from bson import ObjectId

# Import MongoDB configuration and models
from mongodb_config import (
    init_mongodb, test_mongodb_connection, create_default_users, get_database_stats,
    User, Medication, Reminder, MedicationLog, PrescriptionUpload
)

# Import AI components
from prescription_ocr import PrescriptionOCR
from ai_processor import AIProcessor
from medication_reminder import MedicationReminder

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    try:
        return User.objects(id=ObjectId(user_id)).first()
    except:
        return None

# Initialize AI components
ocr_processor = PrescriptionOCR()
ai_processor = AIProcessor()

# MongoDB-compatible reminder system will be initialized after MongoDB connection

# Routes

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        print(f"Login attempt for username: {username}")
        
        # Find user in MongoDB
        user = User.objects(username=username).first()
        
        if user and user.check_password(password):
            print(f"Password verified for user: {username}")
            login_user(user, remember=True)
            
            # Update last login
            user.last_login = datetime.utcnow()
            user.save()
            
            print(f"User {username} logged in successfully")
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict()
            })
        else:
            print(f"Invalid credentials for username: {username}")
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'GET':
        return render_template('register.html')
    
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        # Check if user already exists
        if User.objects(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 409
        
        if User.objects(email=email).first():
            return jsonify({'success': False, 'message': 'Email already exists'}), 409
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            is_active=True
        )
        user.set_password(password)
        user.save()
        
        print(f"New user registered: {username}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user_id': str(user.id)
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'success': False, 'message': 'Registration failed'}), 500

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """User logout"""
    try:
        username = current_user.username
        logout_user()
        print(f"User {username} logged out")
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return jsonify({'success': False, 'message': 'Logout failed'}), 500

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/medications', methods=['GET', 'POST'])
@login_required
def medications():
    """Get or add medications"""
    if request.method == 'POST':
        # Add new medication
        try:
            data = request.json
            print(f"Adding new medication for user {current_user.username}: {data}")
            
            if not data.get('name'):
                return jsonify({'error': 'Medication name is required'}), 400
            
            # Check if medication already exists
            existing = Medication.objects(
                user_id=current_user.id,
                name=data['name'],
                is_active=True
            ).first()
            
            if existing:
                return jsonify({'error': 'Medication already exists'}), 409
            
            # Create new medication
            medication = Medication(
                user_id=current_user.id,
                user_username=current_user.username,
                name=data['name'],
                dosage=data.get('dosage', ''),
                frequency=data.get('frequency', ''),
                instructions=data.get('instructions', ''),
                duration=data.get('duration', ''),
                source='manual'
            )
            medication.save()
            
            print(f"✅ Successfully added medication: {medication.name}")
            
            return jsonify({
                'success': True,
                'message': 'Medication added successfully',
                'medication': medication.to_dict()
            }), 201
            
        except Exception as e:
            print(f"❌ Error adding medication: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    else:
        # Get all medications
        try:
            print(f"Getting medications for user {current_user.id} ({current_user.username})")
            
            medications = Medication.objects(
                user_id=current_user.id,
                is_active=True
            ).order_by('-created_at')
            
            print(f"Found {len(medications)} medications for user {current_user.id}")
            
            result = [med.to_dict() for med in medications]
            
            for med in result:
                print(f"  - {med['name']}: {med['dosage']}, {med['frequency']}")
            
            print(f"Returning {len(result)} medications")
            return jsonify(result)
            
        except Exception as e:
            print(f"Error getting medications: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/upload-prescription', methods=['POST'])
@login_required
def upload_prescription():
    """Upload and process prescription image"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if file:
            # Save uploaded file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            print(f"📁 File saved: {filepath}")
            
            # Create prescription upload record
            upload_record = PrescriptionUpload(
                user_id=current_user.id,
                filename=filename,
                original_filename=file.filename,
                file_path=filepath,
                file_size=os.path.getsize(filepath),
                mime_type=file.content_type,
                processing_status='processing'
            )
            upload_record.save()
            
            # Process with OCR
            start_time = time.time()
            extracted_text = ocr_processor.extract_text_from_image(filepath)
            processing_time = time.time() - start_time
            
            print(f"🔍 OCR extracted text: {extracted_text[:200]}...")
            
            # Process with AI
            medications = ai_processor.extract_medications(extracted_text)
            print(f"💊 AI found {len(medications)} medications")
            
            # Save medications to MongoDB
            medications_added = 0
            for med_data in medications:
                try:
                    # Check if medication already exists
                    existing = Medication.objects(
                        user_id=current_user.id,
                        name=med_data['name'],
                        is_active=True
                    ).first()
                    
                    if not existing:
                        medication = Medication(
                            user_id=current_user.id,
                            user_username=current_user.username,
                            name=med_data['name'],
                            dosage=med_data.get('dosage', ''),
                            frequency=med_data.get('frequency', ''),
                            instructions=med_data.get('instructions', ''),
                            source='ocr',
                            confidence_score=med_data.get('confidence', 0.8)
                        )
                        medication.save()
                        medications_added += 1
                        print(f"✅ Added medication from OCR: {medication.name}")
                    else:
                        print(f"⚠️ Medication already exists: {med_data['name']}")
                        
                except Exception as e:
                    print(f"❌ Error saving medication {med_data.get('name', 'Unknown')}: {e}")
            
            # Update upload record
            upload_record.extracted_text = extracted_text
            upload_record.processing_time = processing_time
            upload_record.medications_found = len(medications)
            upload_record.medications_added = medications_added
            upload_record.processing_status = 'completed'
            upload_record.processed_at = datetime.utcnow()
            upload_record.save()
            
            return jsonify({
                'success': True,
                'message': 'Prescription processed successfully',
                'extracted_text': extracted_text,
                'medications': medications,
                'medications_added': medications_added,
                'processing_time': round(processing_time, 2)
            })
            
    except Exception as e:
        print(f"❌ Upload processing error: {str(e)}")
        
        # Update upload record with error
        if 'upload_record' in locals():
            upload_record.processing_status = 'failed'
            upload_record.error_message = str(e)
            upload_record.save()
        
        return jsonify({
            'success': False,
            'message': 'Prescription processing failed',
            'error': str(e)
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'mongodb'
    })

@app.route('/database-status')
def database_status():
    """MongoDB database status"""
    try:
        stats = get_database_stats()
        if stats:
            return jsonify({
                'status': 'connected',
                'database_type': 'mongodb',
                'connection_string': 'mongodb://localhost:27017/',
                'database_name': 'medimorph_db',
                'statistics': stats,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to get database statistics'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        print(f"🔌 User {current_user.username} connected to WebSocket")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    if current_user.is_authenticated:
        leave_room(f'user_{current_user.id}')
        print(f"🔌 User {current_user.username} disconnected from WebSocket")

@socketio.on('join_user_room')
def handle_join_user_room(data):
    """Join user-specific room for notifications"""
    if current_user.is_authenticated:
        room = f'user_{current_user.id}'
        join_room(room)
        emit('status', {'message': f'Joined room {room}'})

# MongoDB-compatible reminder system
class MongoMedicationReminder:
    """MongoDB-compatible medication reminder system"""

    def __init__(self, socketio=None, app=None):
        self.reminder_thread = None
        self.is_running = False
        self.socketio = socketio
        self.app = app
        self.active_reminders = {}

    def start_reminder_service(self):
        """Start the reminder service"""
        if not self.is_running:
            self.is_running = True
            self.reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
            self.reminder_thread.start()
            print("🔔 MongoDB Medication reminder service started")

    def stop_reminder_service(self):
        """Stop the reminder service"""
        self.is_running = False
        if self.reminder_thread:
            self.reminder_thread.join(timeout=5)
        print("🔔 Medication reminder service stopped")

    def _reminder_loop(self):
        """Main reminder loop"""
        while self.is_running:
            try:
                with self.app.app_context():
                    self._check_and_send_reminders()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"❌ Error in reminder loop: {e}")
                time.sleep(60)

    def _check_and_send_reminders(self):
        """Check for due reminders and send alerts"""
        try:
            current_time = datetime.now()
            current_time_str = current_time.strftime('%H:%M')

            # Get all active reminders
            reminders = Reminder.objects(is_active=True)

            for reminder in reminders:
                if self._is_time_match(current_time_str, reminder.time):
                    if not self._reminder_sent_recently(reminder):
                        self._send_reminder_alert(reminder)

        except Exception as e:
            print(f"❌ Error checking reminders: {e}")

    def _is_time_match(self, current_time, reminder_time):
        """Check if current time matches reminder time (within 1 minute)"""
        try:
            current_hour, current_minute = map(int, current_time.split(':'))
            reminder_hour, reminder_minute = map(int, reminder_time.split(':'))

            current_total_minutes = current_hour * 60 + current_minute
            reminder_total_minutes = reminder_hour * 60 + reminder_minute

            return abs(current_total_minutes - reminder_total_minutes) <= 1
        except:
            return False

    def _reminder_sent_recently(self, reminder):
        """Check if reminder was sent recently (within last hour)"""
        if not reminder.last_sent:
            return False

        time_diff = datetime.now() - reminder.last_sent
        return time_diff.total_seconds() < 3600  # 1 hour

    def _send_reminder_alert(self, reminder):
        """Send reminder alert to user"""
        try:
            # Get medication details
            medication = Medication.objects(id=reminder.medication_id).first()
            if not medication:
                return

            # Update last sent time
            reminder.last_sent = datetime.now()
            reminder.save()

            # Prepare alert data
            alert_data = {
                'type': 'medication_reminder',
                'medication_id': str(reminder.medication_id),
                'medication_name': medication.name,
                'dosage': medication.dosage,
                'frequency': medication.frequency,
                'time': reminder.time,
                'instructions': medication.instructions or '',
                'timestamp': datetime.now().isoformat()
            }

            # Send WebSocket notification
            if self.socketio:
                room = f'user_{reminder.user_id}'
                self.socketio.emit('medication_reminder', alert_data, room=room)
                print(f"🔔 Sent MongoDB reminder for {medication.name} to user {reminder.user_id}")

            # Store in active reminders
            user_id_str = str(reminder.user_id)
            if user_id_str not in self.active_reminders:
                self.active_reminders[user_id_str] = []

            self.active_reminders[user_id_str].append(alert_data)

        except Exception as e:
            print(f"❌ Error sending reminder: {e}")

# Initialize MongoDB reminder system
reminder_system = None

def initialize_mongodb_app():
    """Initialize MongoDB connection and setup"""
    global reminder_system

    try:
        print("🔄 Initializing MongoDB application...")

        # Test MongoDB connection
        if not test_mongodb_connection():
            print("❌ MongoDB connection test failed")
            return False

        # Initialize MongoDB
        if not init_mongodb(app):
            print("❌ MongoDB initialization failed")
            return False

        # Create default users
        if not create_default_users():
            print("⚠️ Warning: Could not create default users")

        # Initialize reminder system
        reminder_system = MongoMedicationReminder(socketio=socketio, app=app)

        # Get initial statistics
        stats = get_database_stats()
        if stats:
            print(f"📊 MongoDB Database status:")
            print(f"   👥 Users: {stats['users']}")
            print(f"   💊 Medications: {stats['medications']}")
            print(f"   ⏰ Reminders: {stats['reminders']}")
            print(f"   📝 Logs: {stats['medication_logs']}")
            print(f"   📄 Uploads: {stats['prescription_uploads']}")

        print("✅ MongoDB application initialized successfully")
        return True

    except Exception as e:
        print(f"❌ MongoDB application initialization failed: {e}")
        return False

if __name__ == '__main__':
    # Initialize MongoDB application
    if not initialize_mongodb_app():
        print("❌ Failed to initialize MongoDB application. Exiting...")
        exit(1)

    # Start reminder service
    if reminder_system:
        print("🔔 Starting MongoDB medication reminder service...")
        reminder_system.start_reminder_service()

    print("🏥 Starting MEDIMORPH with MongoDB...")
    print("🌐 Access the application at: http://localhost:5000")
    print("🗄️ Database: MongoDB (mongodb://localhost:27017/)")
    print("💾 All data will be stored in MongoDB!")

    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
