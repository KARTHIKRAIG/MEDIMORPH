# 🤝 Contributing to MEDIMORPH

## 🎯 Welcome Contributors!

Thank you for your interest in contributing to MEDIMORPH! This guide will help you get started with contributing to our AI-powered prescription digitization and medication reminder system.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Submission Process](#submission-process)
- [Areas for Contribution](#areas-for-contribution)

---

## 📜 Code of Conduct

### **Our Pledge**
We are committed to making participation in MEDIMORPH a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity, level of experience, nationality, personal appearance, race, religion, or sexual identity.

### **Expected Behavior**
- ✅ Use welcoming and inclusive language
- ✅ Be respectful of differing viewpoints
- ✅ Accept constructive criticism gracefully
- ✅ Focus on what's best for the community
- ✅ Show empathy towards other contributors

### **Unacceptable Behavior**
- ❌ Harassment, trolling, or discriminatory comments
- ❌ Publishing private information without permission
- ❌ Spam or irrelevant promotional content
- ❌ Any conduct that would be inappropriate in a professional setting

---

## 🚀 Getting Started

### **Prerequisites**
- **Python 3.11+** installed
- **Git** for version control
- **Basic knowledge** of Flask, SQLAlchemy, and web development
- **Understanding** of OCR and AI/ML concepts (for AI contributions)
- **Familiarity** with healthcare/medical terminology (helpful)

### **First Steps**
1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Set up** development environment
4. **Read** all documentation files
5. **Run** the application and tests
6. **Explore** the codebase structure

---

## 🛠️ Development Setup

### **1. Clone and Setup**
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/MEDIMORPH.git
cd MEDIMORPH

# Add upstream remote
git remote add upstream https://github.com/KARTHIKRAIG/MEDIMORPH.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists
```

### **2. Development Dependencies**
```bash
# Install additional development tools
pip install pytest pytest-cov black flake8 mypy

# Install pre-commit hooks (if configured)
pip install pre-commit
pre-commit install
```

### **3. Environment Configuration**
```bash
# Create .env file for development
cp .env.example .env  # If exists

# Edit .env with your settings
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-not-for-production
```

### **4. Database Setup**
```bash
# Initialize development database
python app.py  # Run once to create tables
# Stop with Ctrl+C

# Verify setup
python final_system_check.py
```

---

## 📝 Contributing Guidelines

### **Types of Contributions**

#### **🐛 Bug Reports**
- Use GitHub Issues with "bug" label
- Include detailed reproduction steps
- Provide system information
- Attach screenshots if UI-related

#### **✨ Feature Requests**
- Use GitHub Issues with "enhancement" label
- Describe the problem you're solving
- Explain your proposed solution
- Consider backward compatibility

#### **📖 Documentation**
- Fix typos and improve clarity
- Add missing documentation
- Update outdated information
- Translate to other languages

#### **💻 Code Contributions**
- Bug fixes
- New features
- Performance improvements
- Code refactoring
- Test coverage improvements

### **Contribution Workflow**

1. **Check existing issues** - Avoid duplicate work
2. **Create/comment on issue** - Discuss your approach
3. **Fork and branch** - Create feature branch
4. **Develop and test** - Follow coding standards
5. **Submit pull request** - Include detailed description
6. **Address feedback** - Collaborate on improvements
7. **Merge** - Celebrate your contribution! 🎉

---

## 🎨 Code Standards

### **Python Code Style**

#### **Formatting**
```python
# Use Black formatter
black --line-length 88 .

# Follow PEP 8 guidelines
flake8 --max-line-length=88 --extend-ignore=E203,W503 .

# Type hints (preferred)
def process_prescription(image_path: str) -> Dict[str, Any]:
    """Process prescription image and extract medications."""
    pass
```

#### **Naming Conventions**
```python
# Variables and functions: snake_case
medication_name = "Aspirin"
def extract_medication_info():
    pass

# Classes: PascalCase
class MedicationExtractor:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 16 * 1024 * 1024
DEFAULT_REMINDER_TIME = "08:00"
```

#### **Documentation**
```python
def extract_medications(text: str) -> List[Dict[str, str]]:
    """
    Extract medication information from OCR text.
    
    Args:
        text (str): Raw text from OCR processing
        
    Returns:
        List[Dict[str, str]]: List of medication dictionaries with
            keys: name, dosage, frequency, instructions
            
    Raises:
        ValueError: If text is empty or invalid
        
    Example:
        >>> text = "Aspirin 100mg once daily"
        >>> extract_medications(text)
        [{'name': 'Aspirin', 'dosage': '100mg', 'frequency': 'once daily'}]
    """
    pass
```

### **Frontend Code Style**

#### **HTML**
```html
<!-- Use semantic HTML5 elements -->
<main class="dashboard-container">
    <section class="medication-list">
        <h2>Your Medications</h2>
        <!-- Content -->
    </section>
</main>

<!-- Proper indentation and attributes -->
<button 
    type="submit" 
    class="btn btn-primary" 
    id="upload-btn"
    aria-label="Upload prescription image">
    Upload Prescription
</button>
```

#### **CSS**
```css
/* Use BEM methodology for class names */
.medication-card {
    /* Block */
}

.medication-card__title {
    /* Element */
}

.medication-card--urgent {
    /* Modifier */
}

/* Mobile-first responsive design */
.dashboard-grid {
    display: grid;
    grid-template-columns: 1fr;
}

@media (min-width: 768px) {
    .dashboard-grid {
        grid-template-columns: 1fr 1fr;
    }
}
```

#### **JavaScript**
```javascript
// Use modern ES6+ syntax
const uploadPrescription = async (file) => {
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/upload-prescription', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Upload failed:', error);
        throw error;
    }
};

// Use descriptive variable names
const medicationReminderTime = '08:00';
const isReminderActive = true;
```

---

## 🧪 Testing Requirements

### **Test Structure**
```
tests/
├── unit/
│   ├── test_ai_processor.py
│   ├── test_prescription_ocr.py
│   └── test_medication_reminder.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_user_workflows.py
└── fixtures/
    ├── sample_prescriptions/
    └── test_data.json
```

### **Writing Tests**

#### **Unit Tests**
```python
import pytest
from app import app, db
from ai_processor import AIProcessor

class TestAIProcessor:
    def setup_method(self):
        """Setup test environment."""
        self.ai_processor = AIProcessor()
        
    def test_extract_medication_name(self):
        """Test medication name extraction."""
        text = "Take Aspirin 100mg daily"
        result = self.ai_processor.extract_medications(text)
        
        assert len(result) == 1
        assert result[0]['name'] == 'Aspirin'
        assert result[0]['dosage'] == '100mg'
        assert result[0]['frequency'] == 'daily'
        
    def test_extract_multiple_medications(self):
        """Test extraction of multiple medications."""
        text = "Aspirin 100mg daily, Metformin 500mg twice daily"
        result = self.ai_processor.extract_medications(text)
        
        assert len(result) == 2
        assert result[0]['name'] == 'Aspirin'
        assert result[1]['name'] == 'Metformin'
```

#### **Integration Tests**
```python
import pytest
from flask import url_for
from app import app, db, User

class TestUserWorkflow:
    def setup_method(self):
        """Setup test client and database."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            
    def test_user_registration_and_login(self):
        """Test complete user registration and login flow."""
        # Register user
        response = self.client.post('/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        assert response.status_code == 200
        
        # Login user
        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert response.status_code == 200
        assert response.json['success'] is True
```

### **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_ai_processor.py

# Run tests with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_medication"
```

### **Test Coverage Requirements**
- **Minimum 80% code coverage** for new contributions
- **All new functions** must have corresponding tests
- **Critical paths** (authentication, OCR, reminders) require 95%+ coverage
- **Integration tests** for all API endpoints

---

## 📤 Submission Process

### **Pull Request Guidelines**

#### **Before Submitting**
- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No merge conflicts with main branch

#### **PR Title Format**
```
[Type] Brief description

Examples:
[Feature] Add medication interaction checker
[Bug] Fix OCR processing for rotated images
[Docs] Update installation guide for macOS
[Refactor] Improve database query performance
```

#### **PR Description Template**
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] New tests added

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

### **Review Process**
1. **Automated checks** run (tests, linting, security)
2. **Code review** by maintainers
3. **Feedback** and requested changes
4. **Approval** and merge
5. **Release** in next version

---

## 🎯 Areas for Contribution

### **🔥 High Priority**
- **Mobile responsiveness** improvements
- **Performance optimization** for large images
- **Multi-language OCR** support
- **Advanced AI models** for better extraction
- **Accessibility** improvements (WCAG compliance)

### **🚀 New Features**
- **Medication interaction** checker
- **Pharmacy integration** API
- **Voice reminders** and commands
- **Wearable device** integration
- **Analytics dashboard** for healthcare providers
- **Backup and sync** functionality

### **🐛 Bug Fixes**
- **OCR accuracy** improvements
- **Edge case handling** in medication extraction
- **Browser compatibility** issues
- **Performance bottlenecks**
- **Security vulnerabilities**

### **📖 Documentation**
- **API documentation** improvements
- **Tutorial videos** and guides
- **Translation** to other languages
- **Code comments** and docstrings
- **Architecture diagrams**

### **🧪 Testing**
- **Increase test coverage**
- **Add performance tests**
- **Browser automation tests**
- **Load testing** scenarios
- **Security testing**

---

## 🏆 Recognition

### **Contributors Wall**
All contributors will be recognized in:
- **README.md** contributors section
- **CHANGELOG.md** for each release
- **GitHub contributors** page
- **Special mentions** for significant contributions

### **Contribution Levels**
- 🥉 **Bronze**: 1-5 merged PRs
- 🥈 **Silver**: 6-15 merged PRs
- 🥇 **Gold**: 16+ merged PRs or major feature
- 💎 **Diamond**: Core maintainer status

---

## 📞 Getting Help

### **Communication Channels**
- **GitHub Issues**: Technical questions and bugs
- **GitHub Discussions**: General questions and ideas
- **Code Review**: Direct feedback on pull requests
- **Email**: Sensitive issues or private questions

### **Mentorship**
New contributors can request mentorship for:
- Understanding the codebase
- Learning best practices
- Guidance on first contributions
- Career advice in healthcare tech

---

**🎉 Thank you for contributing to MEDIMORPH! Together, we're building technology that improves healthcare and saves lives.**
