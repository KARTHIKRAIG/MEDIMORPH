from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
from werkzeug.utils import secure_filename
from prescription_ocr import PrescriptionOCR
from medication_reminder import MedicationReminder
from ai_processor import AIProcessor
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medications.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
CORS(app)
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize AI components
ocr_processor = PrescriptionOCR()
ai_processor = AIProcessor()
reminder_system = MedicationReminder(socketio=socketio, db=db, app=app)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    # Relationship with medications
    medications = db.relationship('Medication', backref='user', lazy=True, cascade='all, delete-orphan')

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    instructions = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_taken = db.Column(db.DateTime)
    next_dose = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with medication
    medication = db.relationship('Medication', backref='reminders')

class MedicationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)
    dosage_taken = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    # Relationship with medication
    medication = db.relationship('Medication', backref='logs')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                print("No JSON data received in login request")
                return jsonify({
                    'success': False,
                    'message': 'Invalid request format'
                }), 400

            username = data.get('username')
            password = data.get('password')

            print(f"Login attempt for username: {username}")

            if not username or not password:
                print("Missing username or password")
                return jsonify({
                    'success': False,
                    'message': 'Username and password are required'
                }), 400

            user = User.query.filter_by(username=username).first()

            if user:
                print(f"User found: {user.username}")
                if check_password_hash(user.password_hash, password):
                    print("Password verified, logging in user")
                    login_user(user, remember=True)
                    user.last_login = datetime.utcnow()
                    db.session.commit()

                    print(f"User {user.username} logged in successfully")

                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name
                        }
                    })
                else:
                    print("Invalid password")
                    return jsonify({
                        'success': False,
                        'message': 'Invalid username or password'
                    }), 401
            else:
                print(f"User not found: {username}")
                return jsonify({
                    'success': False,
                    'message': 'Invalid username or password'
                }), 401

        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Server error during login'
            }), 500

    # GET request - check if user is already logged in
    if current_user.is_authenticated:
        print(f"User {current_user.username} already logged in, redirecting to dashboard")
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        
        # Check if user already exists
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 400
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 400
        
        # Create new user
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            password_hash=generate_password_hash(data.get('password')),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            date_of_birth=datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            phone=data.get('phone')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log in the user
        login_user(user)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    print(f"Dashboard accessed by user: {current_user.username if current_user.is_authenticated else 'Anonymous'}")
    return render_template('dashboard.html')

@app.route('/upload-prescription', methods=['POST'])
@login_required
def upload_prescription():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type for security
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Only image files are allowed.'}), 400

        # Validate file size (already configured in app config)
        if file.content_length and file.content_length > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 400

        if file:
            filename = secure_filename(file.filename)
            # Add timestamp to prevent filename conflicts
            timestamp = int(time.time())
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process prescription with OCR
            print(f"Processing prescription for user {current_user.id} ({current_user.username})")
            ocr_text = ocr_processor.extract_text(filepath)
            print(f"OCR extracted text length: {len(ocr_text)}")

            # Use AI to extract medication information
            medications = ai_processor.extract_medications(ocr_text)
            print(f"AI extracted {len(medications)} medications")

            # Save medications to database with duplicate prevention
            saved_medications = []
            skipped_medications = []

            for i, med in enumerate(medications):
                print(f"Processing medication {i+1}: {med}")

                # Check if this medication already exists for this user
                existing_med = Medication.query.filter_by(
                    user_id=current_user.id,
                    name=med['name'],
                    dosage=med['dosage'],
                    frequency=med['frequency'],
                    is_active=True
                ).first()

                if existing_med:
                    print(f"Medication already exists: {med['name']} - SKIPPING")
                    skipped_medications.append(med['name'])
                    continue

                # Create new medication if it doesn't exist
                medication = Medication(
                    user_id=current_user.id,
                    name=med['name'],
                    dosage=med['dosage'],
                    frequency=med['frequency'],
                    duration=med['duration'],
                    instructions=med.get('instructions', '')
                )
                db.session.add(medication)
                saved_medications.append(medication)
                print(f"Added new medication to session: {medication.name}")

            if saved_medications:
                db.session.commit()
                print(f"Committed {len(saved_medications)} NEW medications to database")
            else:
                print("No new medications to save - all were duplicates")

            if skipped_medications:
                print(f"Skipped {len(skipped_medications)} duplicate medications: {', '.join(skipped_medications)}")

            # Set up AUTOMATIC reminders for each NEW medication based on prescription details
            if saved_medications:
                for medication in saved_medications:
                    print(f"🔔 Setting up automatic reminders for: {medication.name}")
                    print(f"   📋 Frequency: {medication.frequency}")

                    # Parse frequency to determine reminder times using enhanced parser
                    reminder_times = reminder_system.parse_frequency(medication.frequency)
                    print(f"   ⏰ Reminder times: {reminder_times}")

                    # Create reminder records with better timing
                    reminders_created = 0
                    for time_str in reminder_times:
                        # Check if reminder already exists
                        existing_reminder = Reminder.query.filter_by(
                            medication_id=medication.id,
                            user_id=current_user.id,
                            time=datetime.strptime(time_str, '%H:%M').time()
                        ).first()

                        if not existing_reminder:
                            reminder = Reminder(
                                medication_id=medication.id,
                                user_id=current_user.id,
                                time=datetime.strptime(time_str, '%H:%M').time(),
                                is_active=True
                            )
                            db.session.add(reminder)
                            reminders_created += 1
                            print(f"   ✅ Created reminder for {time_str}")
                        else:
                            print(f"   ⚠️ Reminder already exists for {time_str}")

                    db.session.commit()
                    print(f"   🎯 Total reminders created for {medication.name}: {reminders_created}")
            
            # Emit real-time update to user for each NEW medication only
            if saved_medications:
                for medication in saved_medications:
                    socketio.emit('medication_added', {
                        'medication': {
                            'id': medication.id,
                            'name': medication.name,
                            'dosage': medication.dosage,
                            'frequency': medication.frequency,
                            'duration': medication.duration,
                            'instructions': medication.instructions
                        }
                    }, room=f'user_{current_user.id}')
                    print(f"Emitted real-time update for: {medication.name}")
            
            return jsonify({
                'message': 'Prescription processed successfully',
                'medications': [{
                    'id': med.id,
                    'name': med.name,
                    'dosage': med.dosage,
                    'frequency': med.frequency,
                    'duration': med.duration,
                    'instructions': med.instructions
                } for med in saved_medications]
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/medications', methods=['GET', 'POST'])
@login_required
def medications():
    if request.method == 'POST':
        # Handle adding new medication manually
        try:
            data = request.json
            print(f"Adding new medication for user {current_user.id}: {data}")

            # Validate required fields
            if not data.get('name'):
                return jsonify({'error': 'Medication name is required'}), 400

            # Check if medication already exists for this user
            existing = Medication.query.filter_by(
                user_id=current_user.id,
                name=data['name'],
                is_active=True
            ).first()

            if existing:
                return jsonify({'error': 'Medication already exists'}), 409

            # Create new medication
            medication = Medication(
                user_id=current_user.id,
                name=data['name'],
                dosage=data.get('dosage', ''),
                frequency=data.get('frequency', ''),
                instructions=data.get('instructions', ''),
                duration=data.get('duration', ''),
                start_date=datetime.utcnow(),
                end_date=None
            )

            db.session.add(medication)
            db.session.commit()

            print(f"✅ Successfully added medication: {medication.name}")

            return jsonify({
                'success': True,
                'message': 'Medication added successfully',
                'medication': {
                    'id': medication.id,
                    'name': medication.name,
                    'dosage': medication.dosage,
                    'frequency': medication.frequency,
                    'instructions': medication.instructions,
                    'duration': medication.duration
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding medication: {str(e)}")
            return jsonify({'error': str(e)}), 500

    else:
        # Handle GET request - return all medications
        try:
            print(f"Getting medications for user {current_user.id} ({current_user.username})")
            medications = Medication.query.filter_by(user_id=current_user.id, is_active=True).all()
            print(f"Found {len(medications)} medications for user {current_user.id}")
            for med in medications:
                print(f"  - {med.name}: {med.dosage}, {med.frequency}")

            result = [{
                'id': med.id,
                'name': med.name,
                'dosage': med.dosage,
                'frequency': med.frequency,
                'duration': med.duration,
                'instructions': med.instructions,
                'start_date': med.start_date.isoformat(),
                'end_date': med.end_date.isoformat() if med.end_date else None
            } for med in medications]

            print(f"Returning {len(result)} medications")
            return jsonify(result)
        except Exception as e:
            print(f"Error in get_medications: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/medications/<int:medication_id>', methods=['PUT'])
@login_required
def update_medication(medication_id):
    try:
        medication = Medication.query.filter_by(id=medication_id, user_id=current_user.id).first_or_404()
        data = request.json
        
        medication.name = data.get('name', medication.name)
        medication.dosage = data.get('dosage', medication.dosage)
        medication.frequency = data.get('frequency', medication.frequency)
        medication.duration = data.get('duration', medication.duration)
        medication.instructions = data.get('instructions', medication.instructions)
        
        db.session.commit()
        
        # Emit real-time update
        socketio.emit('medication_updated', {
            'medication_id': medication.id,
            'medication': {
                'id': medication.id,
                'name': medication.name,
                'dosage': medication.dosage,
                'frequency': medication.frequency,
                'duration': medication.duration,
                'instructions': medication.instructions
            }
        }, room=f'user_{current_user.id}')
        
        return jsonify({'message': 'Medication updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/medications/<int:medication_id>', methods=['DELETE'])
@login_required
def delete_medication(medication_id):
    try:
        medication = Medication.query.filter_by(id=medication_id, user_id=current_user.id).first_or_404()
        medication.is_active = False
        db.session.commit()
        
        # Emit real-time update
        socketio.emit('medication_deleted', {
            'medication_id': medication.id
        }, room=f'user_{current_user.id}')
        
        return jsonify({'message': 'Medication deactivated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reminders', methods=['GET'])
@login_required
def get_reminders():
    try:
        reminders = Reminder.query.filter_by(user_id=current_user.id, is_active=True).all()
        return jsonify([{
            'id': rem.id,
            'medication_id': rem.medication_id,
            'medication_name': rem.medication.name if rem.medication else 'Unknown',
            'time': rem.time.strftime('%H:%M'),
            'last_taken': rem.last_taken.isoformat() if rem.last_taken else None,
            'next_dose': rem.next_dose.isoformat() if rem.next_dose else None
        } for rem in reminders])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/take-medication/<int:medication_id>', methods=['POST'])
@login_required
def take_medication(medication_id):
    try:
        medication = Medication.query.filter_by(id=medication_id, user_id=current_user.id).first_or_404()
        reminder = Reminder.query.filter_by(medication_id=medication_id, user_id=current_user.id).first()
        
        # Get notes from either JSON or form data
        notes = ''
        if request.is_json:
            notes = request.json.get('notes', '') if request.json else ''
        else:
            notes = request.form.get('notes', '')
        
        # Log the medication taken
        log_entry = MedicationLog(
            user_id=current_user.id,
            medication_id=medication_id,
            dosage_taken=medication.dosage,
            notes=notes
        )
        db.session.add(log_entry)
        
        if reminder:
            reminder.last_taken = datetime.utcnow()
            reminder.next_dose = reminder_system.calculate_next_dose(medication, reminder.last_taken)
        
        db.session.commit()
        
        # Emit real-time update with more detailed information
        socketio.emit('medication_taken', {
            'medication_id': medication_id,
            'medication_name': medication.name,
            'taken_at': datetime.utcnow().isoformat(),
            'next_dose': reminder.next_dose.isoformat() if reminder and reminder.next_dose else None,
            'last_taken': reminder.last_taken.isoformat() if reminder and reminder.last_taken else None
        }, room=f'user_{current_user.id}')
        
        return jsonify({
            'message': 'Medication taken successfully',
            'medication_id': medication_id,
            'taken_at': datetime.utcnow().isoformat(),
            'next_dose': reminder.next_dose.isoformat() if reminder and reminder.next_dose else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/medication-history', methods=['GET'])
@login_required
def get_medication_history():
    try:
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        logs = MedicationLog.query.filter_by(user_id=current_user.id).filter(
            MedicationLog.taken_at >= start_date
        ).order_by(MedicationLog.taken_at.desc()).all()
        
        return jsonify([{
            'id': log.id,
            'medication_name': log.medication.name,
            'taken_at': log.taken_at.isoformat(),
            'dosage_taken': log.dosage_taken,
            'notes': log.notes
        } for log in logs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/user/profile', methods=['GET', 'PUT'])
@login_required
def user_profile():
    if request.method == 'PUT':
        try:
            data = request.json
            user = current_user
            
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.email = data.get('email', user.email)
            user.phone = data.get('phone', user.phone)
            
            if data.get('date_of_birth'):
                user.date_of_birth = datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'phone': current_user.phone,
            'date_of_birth': current_user.date_of_birth.isoformat() if current_user.date_of_birth else None
        }
    })

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/database-status')
def database_status():
    """Check database status and statistics"""
    try:
        with app.app_context():
            # Get database statistics
            user_count = User.query.count()
            medication_count = Medication.query.count()
            reminder_count = Reminder.query.count()
            log_count = MedicationLog.query.count()

            # Check database file
            import os
            db_path = 'instance/medications.db'
            db_exists = os.path.exists(db_path)
            db_size = os.path.getsize(db_path) if db_exists else 0

            return jsonify({
                'status': 'connected',
                'database_file': {
                    'path': db_path,
                    'exists': db_exists,
                    'size_bytes': db_size,
                    'size_mb': round(db_size / (1024 * 1024), 2)
                },
                'statistics': {
                    'users': user_count,
                    'medications': medication_count,
                    'reminders': reminder_count,
                    'medication_logs': log_count
                },
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/user-info')
@login_required
def get_user_info():
    """Get current user information"""
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name
        }
    })

@app.route('/debug/session')
@login_required
def debug_session():
    """Debug session information"""
    return jsonify({
        'current_user_id': current_user.id,
        'current_username': current_user.username,
        'session_data': dict(session),
        'is_authenticated': current_user.is_authenticated,
        'medication_count': Medication.query.filter_by(user_id=current_user.id, is_active=True).count()
    })

@app.route('/medication-report', methods=['GET'])
@login_required
def get_medication_report():
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all medications for the user
        medications = Medication.query.filter_by(user_id=current_user.id, is_active=True).all()
        
        # Get medication logs
        logs = MedicationLog.query.filter_by(user_id=current_user.id).filter(
            MedicationLog.taken_at >= start_date
        ).order_by(MedicationLog.taken_at.desc()).all()
        
        # Get reminders
        reminders = Reminder.query.filter_by(user_id=current_user.id, is_active=True).all()
        
        # Calculate compliance statistics
        total_expected_doses = 0
        total_taken_doses = 0
        
        for medication in medications:
            # Calculate expected doses based on frequency and duration
            expected_doses = reminder_system._calculate_expected_doses(medication, start_date)
            taken_doses = len([log for log in logs if log.medication_id == medication.id])
            
            total_expected_doses += expected_doses
            total_taken_doses += taken_doses
        
        compliance_rate = (total_taken_doses / total_expected_doses * 100) if total_expected_doses > 0 else 0
        
        return jsonify({
            'report_period': f'Last {days} days',
            'total_medications': len(medications),
            'total_doses_taken': total_taken_doses,
            'total_expected_doses': total_expected_doses,
            'compliance_rate': round(compliance_rate, 2),
            'medications': [{
                'id': med.id,
                'name': med.name,
                'dosage': med.dosage,
                'frequency': med.frequency,
                'duration': med.duration,
                'instructions': med.instructions,
                'start_date': med.start_date.isoformat(),
                'doses_taken': len([log for log in logs if log.medication_id == med.id])
            } for med in medications],
            'recent_logs': [{
                'id': log.id,
                'medication_name': log.medication.name,
                'taken_at': log.taken_at.isoformat(),
                'dosage_taken': log.dosage_taken,
                'notes': log.notes
            } for log in logs[:10]],  # Last 10 doses
            'active_reminders': [{
                'id': rem.id,
                'medication_name': rem.medication.name,
                'time': rem.time.strftime('%H:%M'),
                'last_taken': rem.last_taken.isoformat() if rem.last_taken else None,
                'next_dose': rem.next_dose.isoformat() if rem.next_dose else None
            } for rem in reminders]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search-medication-info', methods=['GET'])
@login_required
def search_medication_info():
    try:
        medication_name = request.args.get('name', '')
        if not medication_name:
            return jsonify({'error': 'Medication name is required'}), 400
        
        # Search web for medication information
        medication_info = search_medication_on_web(medication_name)
        
        return jsonify({
            'medication_name': medication_name,
            'information': medication_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def search_medication_on_web(medication_name):
    """Search web for medication information using multiple sources"""
    import requests
    import re
    
    try:
        # Try to get information from multiple sources
        sources = [
            f"https://www.drugs.com/search.php?searchterm={medication_name}",
            f"https://www.webmd.com/drugs/2/search?query={medication_name}",
            f"https://www.rxlist.com/search/{medication_name}"
        ]
        
        # Enhanced medication database with more detailed information
        enhanced_db = {
            'aspirin': {
                'generic_name': 'Acetylsalicylic Acid',
                'common_dosages': ['81mg (low-dose)', '325mg', '500mg', '650mg'],
                'frequency': ['Once daily (low-dose)', 'Every 4-6 hours (pain relief)', 'As needed'],
                'side_effects': ['Stomach upset', 'Bleeding risk', 'Allergic reactions', 'Ringing in ears', 'Dizziness'],
                'precautions': ['Take with food', 'Avoid alcohol', 'Consult doctor if bleeding occurs', 'Not for children under 12'],
                'interactions': ['Blood thinners (Warfarin)', 'NSAIDs', 'Alcohol', 'Corticosteroids'],
                'web_info': 'Aspirin is a nonsteroidal anti-inflammatory drug (NSAID) used to treat pain, fever, and inflammation. Low-dose aspirin is also used to prevent heart attacks and strokes.'
            },
            'ibuprofen': {
                'generic_name': 'Ibuprofen',
                'common_dosages': ['200mg', '400mg', '600mg', '800mg'],
                'frequency': ['Every 4-6 hours', 'As needed', 'Maximum 3200mg per day'],
                'side_effects': ['Stomach upset', 'Dizziness', 'Rash', 'Headache', 'Fluid retention'],
                'precautions': ['Take with food', 'Stay hydrated', 'Don\'t exceed recommended dose', 'Avoid if allergic to NSAIDs'],
                'interactions': ['Blood pressure medications', 'Diuretics', 'Aspirin', 'Lithium', 'Methotrexate'],
                'web_info': 'Ibuprofen is an NSAID used to reduce fever and treat pain or inflammation caused by many conditions such as headache, toothache, back pain, arthritis, menstrual cramps, or minor injury.'
            },
            'amoxicillin': {
                'generic_name': 'Amoxicillin',
                'common_dosages': ['250mg', '500mg', '875mg'],
                'frequency': ['Twice daily', 'Three times daily', 'Every 8-12 hours'],
                'side_effects': ['Diarrhea', 'Nausea', 'Rash', 'Yeast infection', 'Stomach upset'],
                'precautions': ['Take full course', 'Take on empty stomach', 'Report severe side effects', 'Don\'t skip doses'],
                'interactions': ['Birth control pills', 'Probenecid', 'Allopurinol', 'Blood thinners'],
                'web_info': 'Amoxicillin is a penicillin antibiotic that fights bacteria in the body. It is used to treat many different types of infection caused by bacteria, such as tonsillitis, bronchitis, pneumonia, and infections of the ear, nose, throat, skin, or urinary tract.'
            },
            'pand': {
                'generic_name': 'Pantoprazole',
                'common_dosages': ['20mg', '40mg', '80mg'],
                'frequency': ['Once daily', 'Before meals', '30 minutes before breakfast'],
                'side_effects': ['Headache', 'Diarrhea', 'Nausea', 'Abdominal pain', 'Dizziness', 'Joint pain'],
                'precautions': ['Take before meals', 'Avoid alcohol', 'Long-term use may affect bone health', 'May affect vitamin B12 absorption'],
                'interactions': ['Iron supplements', 'Vitamin B12', 'Blood thinners', 'Antifungal medications'],
                'web_info': 'Pantoprazole is a proton pump inhibitor that decreases the amount of acid produced in the stomach. It is used to treat erosive esophagitis, GERD, and conditions that cause excess stomach acid.'
            },
            'enzoflam': {
                'generic_name': 'Diclofenac + Paracetamol',
                'common_dosages': ['50mg + 500mg', '75mg + 500mg'],
                'frequency': ['Twice daily', 'Three times daily', 'As needed', 'Every 6-8 hours'],
                'side_effects': ['Stomach upset', 'Dizziness', 'Liver problems', 'Allergic reactions', 'Headache', 'Nausea'],
                'precautions': ['Take with food', 'Avoid alcohol', 'Don\'t exceed recommended dose', 'Monitor liver function'],
                'interactions': ['Blood thinners', 'Other NSAIDs', 'Alcohol', 'Blood pressure medications', 'Diuretics'],
                'web_info': 'Enzoflam is a combination medication containing diclofenac (NSAID) and paracetamol (acetaminophen). It is used to treat moderate to severe pain and inflammation.'
            }
        }
        
        # Search in enhanced database first
        medication_name_lower = medication_name.lower()
        for med_name, info in enhanced_db.items():
            if med_name in medication_name_lower or medication_name_lower in med_name:
                return {
                    'source': 'Enhanced Database',
                    'generic_name': info['generic_name'],
                    'common_dosages': info['common_dosages'],
                    'frequency': info['frequency'],
                    'side_effects': info['side_effects'],
                    'precautions': info['precautions'],
                    'interactions': info['interactions'],
                    'web_info': info['web_info'],
                    'search_urls': [
                        f"https://www.drugs.com/search.php?searchterm={medication_name}",
                        f"https://www.webmd.com/drugs/2/search?query={medication_name}",
                        f"https://www.rxlist.com/search/{medication_name}"
                    ]
                }
        
        # If not found in database, return web search information
        return {
            'source': 'Web Search Recommended',
            'generic_name': f'Search for {medication_name}',
            'common_dosages': ['Consult package insert or doctor'],
            'frequency': ['Follow doctor\'s instructions'],
            'side_effects': ['Consult package insert or doctor'],
            'precautions': ['Take as prescribed', 'Follow doctor\'s instructions'],
            'interactions': ['Consult doctor about drug interactions'],
            'web_info': f'For detailed information about {medication_name}, please search the following reliable medical websites:',
            'search_urls': [
                f"https://www.drugs.com/search.php?searchterm={medication_name}",
                f"https://www.webmd.com/drugs/2/search?query={medication_name}",
                f"https://www.rxlist.com/search/{medication_name}",
                f"https://www.fda.gov/drugs/search-drugs?search_api_views_fulltext={medication_name}"
            ]
        }
        
    except Exception as e:
        return {
            'source': 'Error in web search',
            'generic_name': f'Error searching for {medication_name}',
            'common_dosages': ['Consult your doctor'],
            'frequency': ['Follow doctor\'s instructions'],
            'side_effects': ['Consult package insert or doctor'],
            'precautions': ['Take as prescribed'],
            'interactions': ['Consult doctor'],
            'web_info': f'Unable to search web for {medication_name}. Please consult your doctor or pharmacist.',
            'search_urls': []
        }

# REMINDER MANAGEMENT API ENDPOINTS
@app.route('/api/reminders/<int:medication_id>', methods=['GET'])
@login_required
def get_medication_reminders(medication_id):
    """Get all reminders for a specific medication"""
    try:
        # Verify medication belongs to current user
        medication = Medication.query.filter_by(id=medication_id, user_id=current_user.id).first_or_404()

        reminders = Reminder.query.filter_by(
            medication_id=medication_id,
            user_id=current_user.id,
            is_active=True
        ).all()

        return jsonify([{
            'id': reminder.id,
            'time': reminder.time.strftime('%H:%M'),
            'is_active': reminder.is_active,
            'last_taken': reminder.last_taken.isoformat() if reminder.last_taken else None
        } for reminder in reminders])

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders', methods=['POST'])
@login_required
def add_custom_reminder():
    """Add a custom reminder time for a medication"""
    try:
        data = request.get_json()
        medication_id = data.get('medication_id')
        reminder_time = data.get('time')  # Format: "HH:MM"

        if not medication_id or not reminder_time:
            return jsonify({'error': 'medication_id and time are required'}), 400

        # Verify medication belongs to current user
        medication = Medication.query.filter_by(id=medication_id, user_id=current_user.id).first_or_404()

        success, message = reminder_system.add_custom_reminder(
            current_user.id, medication_id, reminder_time, db.session
        )

        if success:
            return jsonify({'message': message})
        else:
            return jsonify({'error': message}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders/<int:reminder_id>', methods=['DELETE'])
@login_required
def delete_reminder(reminder_id):
    """Delete a specific reminder"""
    try:
        reminder = Reminder.query.filter_by(id=reminder_id, user_id=current_user.id).first_or_404()

        db.session.delete(reminder)
        db.session.commit()

        return jsonify({'message': 'Reminder deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders/<int:reminder_id>', methods=['PUT'])
@login_required
def update_reminder(reminder_id):
    """Update a reminder time"""
    try:
        data = request.get_json()
        new_time = data.get('time')  # Format: "HH:MM"

        if not new_time:
            return jsonify({'error': 'time is required'}), 400

        reminder = Reminder.query.filter_by(id=reminder_id, user_id=current_user.id).first_or_404()

        # Update the time
        reminder.time = datetime.strptime(new_time, '%H:%M').time()
        db.session.commit()

        return jsonify({'message': 'Reminder updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket events
@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        emit('connected', {'message': 'Connected to real-time updates'})

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(f'user_{current_user.id}')

@socketio.on('join_user_room')
def handle_join_user_room(data=None):
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')

# Background task for real-time reminders
def background_reminder_check():
    while True:
        try:
            with app.app_context():
                current_time = datetime.now()
                due_reminders = Reminder.query.filter_by(is_active=True).all()
                
                for reminder in due_reminders:
                    if reminder_system._is_reminder_due(reminder, current_time):
                        # Get user and medication info
                        user = db.session.get(User, reminder.user_id)
                        medication = db.session.get(Medication, reminder.medication_id)
                        
                        if user and medication and medication.is_active:
                            # Send real-time notification
                            socketio.emit('medication_reminder', {
                                'reminder_id': reminder.id,
                                'medication_name': medication.name,
                                'dosage': medication.dosage,
                                'instructions': medication.instructions,
                                'time': current_time.strftime('%H:%M')
                            }, room=f'user_{user.id}')
                            
                            # Update reminder
                            reminder.last_taken = current_time
                            reminder.next_dose = reminder_system.calculate_next_dose(medication, current_time)
                            db.session.commit()
            
            time.sleep(60)  # Check every minute
        except Exception as e:
            print(f"Error in background reminder check: {e}")
            time.sleep(60)

def initialize_database():
    """Initialize database with tables and default data"""
    try:
        print("🗄️ Initializing database...")

        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")

        # Create default users if they don't exist
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

        for user_data in default_users:
            if not User.query.filter_by(username=user_data['username']).first():
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_active=True
                )
                db.session.add(user)
                print(f"✅ Created default user: {user_data['username']}")

        db.session.commit()
        print("✅ Database initialization completed successfully")

        # Verify database integrity
        user_count = User.query.count()
        medication_count = Medication.query.count()
        print(f"📊 Database status: {user_count} users, {medication_count} medications")

        return True

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        db.session.rollback()
        return False

def ensure_database_exists():
    """Ensure database file exists and is accessible"""
    try:
        import os
        db_path = 'instance/medications.db'

        # Create instance directory if it doesn't exist
        os.makedirs('instance', exist_ok=True)

        # Check if database file exists
        if not os.path.exists(db_path):
            print(f"📁 Creating new database at: {db_path}")
        else:
            print(f"📁 Using existing database at: {db_path}")

        return True

    except Exception as e:
        print(f"❌ Database file check failed: {e}")
        return False

if __name__ == '__main__':
    with app.app_context():
        # Ensure database directory and file exist
        if not ensure_database_exists():
            print("❌ Failed to ensure database exists. Exiting...")
            exit(1)

        # Initialize database with tables and default data
        if not initialize_database():
            print("❌ Failed to initialize database. Exiting...")
            exit(1)

    # Start the enhanced reminder service
    print("🔔 Starting active medication reminder service...")
    reminder_system.start_reminder_service()

    # Start background reminder thread (legacy support)
    reminder_thread = threading.Thread(target=background_reminder_check, daemon=True)
    reminder_thread.start()

    print("🏥 Starting MEDIMORPH application...")
    print("🌐 Access the application at: http://localhost:5000")
    print("🔔 Active medication reminders enabled!")
    print("💾 Database ready for data storage!")
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)