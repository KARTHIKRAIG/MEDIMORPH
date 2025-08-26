
# MEDIMORPH - Prescription Digitization & Medication Reminder System

A comprehensive AI-powered application that digitizes prescriptions using OCR and provides intelligent medication reminders with user authentication and real-time features.

## 🚀 Features

### 🔐 User Authentication & Security
- **User Registration & Login**: Secure user accounts with password hashing
- **Session Management**: Flask-Login integration for secure sessions
- **User Profiles**: Personal information management
- **Multi-user Support**: Each user has their own medication data

### 📸 Prescription Digitization
- **OCR Processing**: Extract text from prescription images using Tesseract OCR
- **AI-Powered Extraction**: Use machine learning to identify medications, dosages, and frequencies
- **Multiple Recognition Methods**: Combines rule-based, pattern-based, and NER-based extraction
- **Image Preprocessing**: Advanced image processing for better OCR accuracy

### 💊 Medication Management
- **Smart Parsing**: Automatically extract medication names, dosages, frequencies, and durations
- **Database Storage**: Secure storage of medication information per user
- **Edit & Delete**: Manage your medication list with ease
- **Medication History**: Track when medications were taken

### ⏰ Intelligent Reminders
- **Automatic Scheduling**: Set up reminders based on prescription frequency
- **Multiple Frequencies**: Support for daily, twice daily, three times daily, etc.
- **Real-time Notifications**: Get reminded when it's time to take medication
- **Dose Tracking**: Mark medications as taken and track compliance

### 🔄 Real-time Features
- **WebSocket Integration**: Live updates using Flask-SocketIO
- **Instant Notifications**: Real-time medication reminders
- **Live Updates**: Medication changes appear instantly across all connected clients
- **Background Processing**: Continuous reminder checking in background threads

### 🎨 Modern Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Intuitive UI**: Clean, modern interface with easy navigation
- **Real-time Updates**: Live updates without page refresh
- **User Dashboard**: Personalized medication management interface

## 🛠️ Technology Stack

- **Backend**: Python Flask with Flask-Login and Flask-SocketIO
- **Database**: SQLite (with SQLAlchemy ORM)
- **Authentication**: Flask-Login with password hashing
- **Real-time**: WebSocket communication via Socket.IO
- **OCR**: Tesseract with OpenCV preprocessing
- **AI/ML**: Transformers library for NER, scikit-learn for pattern recognition
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Image Processing**: OpenCV, Pillow

## 📋 Prerequisites

### System Requirements
- Python 3.8 or higher
- Windows 10/11 (for Tesseract installation)
- At least 4GB RAM
- 2GB free disk space

### Required Software
1. **Python**: Download from [python.org](https://python.org)
2. **Tesseract OCR**: Download from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
3. **Git**: For cloning the repository

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd medimorph
```

### 2. Install Tesseract OCR
1. Download Tesseract for Windows from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to default location: `C:\Program Files\Tesseract-OCR\`
3. Add Tesseract to your system PATH

### 3. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 5. Initialize Database
The database will be automatically created when you run the application for the first time.

## 🎯 Usage

### Starting the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Using the Application

#### 1. User Registration & Login
1. Visit the application and click "Create a new account"
2. Fill in your personal information and create a secure password
3. Log in with your credentials to access your personalized dashboard

#### 2. Upload Prescription
1. Click "Choose Image" to select a prescription photo
2. Click "Process Prescription" to digitize the prescription
3. The AI will extract medication information automatically

#### 3. Manage Medications
- View all your medications in your personalized dashboard
- Mark medications as taken with the "Take Now" button
- Edit or delete medications as needed
- View medication history and compliance

#### 4. Real-time Features
- Receive instant notifications when it's time to take medication
- See live updates when medications are added or modified
- Get real-time reminders based on your prescription schedule

## 📁 Project Structure

```
medimorph/
├── app.py                 # Main Flask application with auth & WebSocket
├── prescription_ocr.py    # OCR processing module
├── ai_processor.py        # AI/ML medication extraction
├── medication_reminder.py # Reminder system with user support
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   ├── login.html        # User login page
│   ├── register.html     # User registration page
│   └── dashboard.html    # Main dashboard with real-time features
├── uploads/              # Uploaded prescription images
└── medications.db        # SQLite database (created automatically)
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///medications.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### Tesseract Configuration
The application automatically detects Tesseract installation. If you installed it in a custom location, update the path in `prescription_ocr.py`:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Your\Custom\Path\To\Tesseract\tesseract.exe'
```

## 🤖 AI/ML Features

### OCR Processing
- **Image Preprocessing**: Noise reduction, thresholding, morphological operations
- **Text Extraction**: Tesseract OCR with custom configuration
- **Text Cleaning**: Remove artifacts and fix common OCR mistakes

### Medication Extraction
- **Rule-based**: Pattern matching for known medications
- **NER-based**: Named Entity Recognition for medication names
- **Pattern-based**: Regex patterns for dosage and frequency extraction
- **Confidence Scoring**: Multiple extraction methods with confidence scores

### Reminder Intelligence
- **Frequency Parsing**: Automatic parsing of prescription frequencies
- **Smart Scheduling**: Calculate optimal reminder times
- **Compliance Tracking**: Monitor medication adherence per user

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Flask-Login for secure user sessions
- **User Isolation**: Each user can only access their own data
- **File Upload Validation**: Secure file handling with size limits
- **Input Sanitization**: Clean and validate all user inputs
- **Database Security**: SQLAlchemy ORM prevents SQL injection
- **Error Handling**: Comprehensive error handling and logging

## 🔄 Real-time Architecture

### WebSocket Implementation
- **Flask-SocketIO**: Server-side WebSocket handling
- **Socket.IO Client**: Browser-side real-time communication
- **Room-based Messaging**: User-specific notification channels
- **Background Threading**: Continuous reminder checking

### Real-time Events
- **medication_added**: When new medications are processed
- **medication_updated**: When medications are modified
- **medication_deleted**: When medications are removed
- **medication_taken**: When doses are marked as taken
- **medication_reminder**: When it's time to take medication

## 🧪 Testing

### Manual Testing
1. Register a new user account
2. Upload a prescription image
3. Verify medication extraction accuracy
4. Test real-time reminder functionality
5. Check web interface responsiveness

### Sample Prescriptions
The application works best with clear, well-lit images of prescriptions. For testing, you can use:
- Clear photos of prescription labels
- Scanned prescription documents
- Screenshots of digital prescriptions

## 🐛 Troubleshooting

### Common Issues

#### Tesseract Not Found
```
Error: Could not read image
```
**Solution**: Ensure Tesseract is installed and in your system PATH

#### Import Errors
```
ModuleNotFoundError: No module named 'flask_login'
```
**Solution**: Install dependencies with `pip install -r requirements.txt`

#### WebSocket Connection Issues
```
WebSocket connection failed
```
**Solution**: Ensure the application is running and check firewall settings

#### Database Errors
```
OperationalError: no such table
```
**Solution**: The database will be created automatically on first run

### Performance Optimization
- Use high-quality images for better OCR accuracy
- Close other applications to free up memory
- Consider using SSD storage for faster database operations

## 📈 Future Enhancements

### Planned Features
- **Mobile App**: Native iOS and Android applications
- **Cloud Storage**: Secure cloud storage for prescriptions
- **Doctor Integration**: Direct integration with healthcare providers
- **Advanced Analytics**: Detailed medication compliance reports
- **Voice Reminders**: Voice-activated medication reminders
- **Drug Interaction Checking**: Check for potential drug interactions
- **Push Notifications**: Mobile push notifications for reminders
- **Email Notifications**: Email-based medication reminders

### AI Improvements
- **Custom ML Models**: Train models on medical prescription data
- **Handwriting Recognition**: Better recognition of handwritten prescriptions
- **Multi-language Support**: Support for prescriptions in different languages
- **Image Quality Assessment**: Automatic assessment of image quality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application is for educational and demonstration purposes. It should not be used as a replacement for professional medical advice. Always consult with healthcare professionals regarding medication management.

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review the documentation

---

**Made with ❤️ for better healthcare management**
