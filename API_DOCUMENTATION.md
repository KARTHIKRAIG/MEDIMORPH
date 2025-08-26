# 🌐 MEDIMORPH API Documentation

## 📋 Overview

MEDIMORPH provides a comprehensive RESTful API for prescription digitization, medication management, and real-time notifications. All endpoints require proper authentication except for public routes.

**Base URL**: `http://localhost:5000`  
**Authentication**: Session-based with Flask-Login  
**Content-Type**: `application/json` (unless specified)

---

## 🔐 Authentication Endpoints

### **POST /login**
Authenticate user and create session.

**Request Body:**
```json
{
    "username": "testuser",
    "password": "testpass123"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com"
    }
}
```

**Response (Error):**
```json
{
    "success": false,
    "message": "Invalid username or password"
}
```

### **POST /register**
Create new user account.

**Request Body:**
```json
{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepassword123"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Registration successful",
    "user_id": 2
}
```

### **POST /logout**
End user session.

**Response:**
```json
{
    "success": true,
    "message": "Logged out successfully"
}
```

---

## 💊 Medication Management Endpoints

### **GET /medications**
Retrieve all medications for authenticated user.

**Headers:**
```
Authorization: Session-based (automatic)
```

**Response:**
```json
[
    {
        "id": 1,
        "name": "Aspirin",
        "dosage": "100mg",
        "frequency": "Once daily",
        "instructions": "Take with food",
        "start_date": "2024-01-15",
        "end_date": "2024-02-15",
        "created_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": 2,
        "name": "Metformin",
        "dosage": "500mg",
        "frequency": "Twice daily",
        "instructions": "Take before meals",
        "start_date": "2024-01-10",
        "end_date": null,
        "created_at": "2024-01-10T09:15:00Z"
    }
]
```

### **POST /medications**
Add new medication manually.

**Request Body:**
```json
{
    "name": "Lisinopril",
    "dosage": "10mg",
    "frequency": "Once daily",
    "instructions": "Take in the morning",
    "start_date": "2024-01-20",
    "end_date": "2024-12-20"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Medication added successfully",
    "medication_id": 3
}
```

### **PUT /medications/{id}**
Update existing medication.

**Request Body:**
```json
{
    "dosage": "20mg",
    "frequency": "Twice daily",
    "instructions": "Take with breakfast and dinner"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Medication updated successfully"
}
```

### **DELETE /medications/{id}**
Remove medication from user's list.

**Response:**
```json
{
    "success": true,
    "message": "Medication deleted successfully"
}
```

---

## 📸 Prescription Processing Endpoints

### **POST /upload-prescription**
Upload and process prescription image.

**Content-Type**: `multipart/form-data`

**Request:**
```
file: <prescription_image.jpg>
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Prescription processed successfully",
    "extracted_text": "Patient: John Doe\nRx: Aspirin 100mg\nSig: Take 1 tablet daily\nQty: 30\nRefills: 2",
    "medications": [
        {
            "name": "Aspirin",
            "dosage": "100mg",
            "frequency": "Once daily",
            "quantity": "30",
            "refills": "2",
            "confidence": 0.95
        }
    ],
    "processing_time": 2.3
}
```

**Response (Error):**
```json
{
    "success": false,
    "message": "OCR processing failed",
    "error": "Image quality too low for reliable text extraction"
}
```

### **GET /prescription-history**
Get user's prescription upload history.

**Response:**
```json
[
    {
        "id": 1,
        "filename": "prescription_20240115.jpg",
        "upload_date": "2024-01-15T14:30:00Z",
        "processing_status": "completed",
        "medications_extracted": 3,
        "ocr_confidence": 0.92
    }
]
```

---

## ⏰ Reminder Management Endpoints

### **GET /api/reminders**
Get all active reminders for user.

**Response:**
```json
[
    {
        "id": 1,
        "medication_id": 1,
        "medication_name": "Aspirin",
        "reminder_time": "08:00",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": 2,
        "medication_id": 2,
        "medication_name": "Metformin",
        "reminder_time": "18:00",
        "is_active": true,
        "created_at": "2024-01-10T09:15:00Z"
    }
]
```

### **POST /api/reminders**
Create new medication reminder.

**Request Body:**
```json
{
    "medication_id": 1,
    "reminder_time": "09:00"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Reminder created successfully",
    "reminder_id": 3
}
```

### **PUT /api/reminders/{id}**
Update existing reminder.

**Request Body:**
```json
{
    "reminder_time": "10:00",
    "is_active": false
}
```

**Response:**
```json
{
    "success": true,
    "message": "Reminder updated successfully"
}
```

### **DELETE /api/reminders/{id}**
Delete reminder.

**Response:**
```json
{
    "success": true,
    "message": "Reminder deleted successfully"
}
```

---

## 📊 Analytics & Reporting Endpoints

### **GET /api/compliance-report**
Get medication compliance statistics.

**Query Parameters:**
- `start_date` (optional): YYYY-MM-DD format
- `end_date` (optional): YYYY-MM-DD format
- `medication_id` (optional): Specific medication ID

**Response:**
```json
{
    "period": {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    },
    "overall_compliance": 0.87,
    "medications": [
        {
            "medication_id": 1,
            "medication_name": "Aspirin",
            "prescribed_doses": 31,
            "taken_doses": 28,
            "compliance_rate": 0.90,
            "missed_doses": 3
        }
    ],
    "trends": {
        "weekly_compliance": [0.85, 0.92, 0.88, 0.84],
        "best_day": "Monday",
        "worst_day": "Sunday"
    }
}
```

### **POST /api/log-medication**
Log medication intake.

**Request Body:**
```json
{
    "medication_id": 1,
    "taken_at": "2024-01-15T08:15:00Z",
    "notes": "Taken with breakfast"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Medication intake logged successfully",
    "log_id": 15
}
```

---

## 🔔 Real-Time WebSocket Events

### **Connection**
```javascript
const socket = io('http://localhost:5000');
```

### **Events Emitted by Server**

#### **medication_reminder**
```json
{
    "type": "medication_reminder",
    "medication": {
        "id": 1,
        "name": "Aspirin",
        "dosage": "100mg",
        "time": "08:00"
    },
    "message": "Time to take your Aspirin (100mg)",
    "timestamp": "2024-01-15T08:00:00Z"
}
```

#### **prescription_processed**
```json
{
    "type": "prescription_processed",
    "prescription_id": 5,
    "medications_found": 2,
    "processing_time": 2.1,
    "message": "Prescription processed successfully"
}
```

#### **system_notification**
```json
{
    "type": "system_notification",
    "level": "info",
    "message": "System maintenance scheduled for tonight",
    "timestamp": "2024-01-15T15:30:00Z"
}
```

### **Events Received by Server**

#### **join_user_room**
```json
{
    "user_id": 1
}
```

#### **medication_taken**
```json
{
    "medication_id": 1,
    "reminder_id": 3,
    "taken_at": "2024-01-15T08:05:00Z"
}
```

---

## 🏥 Health & Status Endpoints

### **GET /health**
System health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0.0",
    "services": {
        "database": "connected",
        "ocr_engine": "available",
        "reminder_service": "running",
        "websocket": "active"
    },
    "uptime": "2 days, 14 hours, 23 minutes"
}
```

### **GET /api/system-stats**
System statistics (admin only).

**Response:**
```json
{
    "users": {
        "total": 150,
        "active_today": 45,
        "new_this_week": 12
    },
    "prescriptions": {
        "total_processed": 1250,
        "processed_today": 23,
        "average_processing_time": 2.1
    },
    "medications": {
        "total_tracked": 3500,
        "reminders_sent_today": 180,
        "compliance_rate": 0.86
    }
}
```

---

## 🚨 Error Handling

### **Standard Error Response Format**
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {
            "field": "email",
            "issue": "Invalid email format"
        }
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Common Error Codes**
- `AUTHENTICATION_REQUIRED` (401): User not logged in
- `FORBIDDEN` (403): Insufficient permissions
- `NOT_FOUND` (404): Resource not found
- `VALIDATION_ERROR` (400): Invalid input data
- `OCR_PROCESSING_ERROR` (422): Image processing failed
- `DATABASE_ERROR` (500): Database operation failed
- `RATE_LIMIT_EXCEEDED` (429): Too many requests

---

## 📝 Usage Examples

### **JavaScript/Fetch API**
```javascript
// Login
const loginResponse = await fetch('/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'testuser',
        password: 'testpass123'
    })
});

// Upload prescription
const formData = new FormData();
formData.append('file', prescriptionFile);

const uploadResponse = await fetch('/upload-prescription', {
    method: 'POST',
    body: formData
});

// Get medications
const medications = await fetch('/medications').then(r => r.json());
```

### **Python/Requests**
```python
import requests

# Login
session = requests.Session()
login_data = {'username': 'testuser', 'password': 'testpass123'}
response = session.post('http://localhost:5000/login', json=login_data)

# Get medications
medications = session.get('http://localhost:5000/medications').json()

# Upload prescription
with open('prescription.jpg', 'rb') as f:
    files = {'file': f}
    response = session.post('http://localhost:5000/upload-prescription', files=files)
```

### **cURL Examples**
```bash
# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' \
  -c cookies.txt

# Get medications
curl -X GET http://localhost:5000/medications \
  -b cookies.txt

# Upload prescription
curl -X POST http://localhost:5000/upload-prescription \
  -F "file=@prescription.jpg" \
  -b cookies.txt
```

---

## 🔧 Rate Limiting

**Default Limits:**
- Authentication endpoints: 5 requests per minute
- Upload endpoints: 10 requests per hour
- API endpoints: 100 requests per hour
- WebSocket connections: 5 concurrent per user

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

---

**🎯 This API documentation provides complete integration guidance for developers building applications with MEDIMORPH's backend services.**
