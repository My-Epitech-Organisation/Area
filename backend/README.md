# AREA Backend - Django REST API

This Django backend implements the REST API for the AREA (Action-Reaction) application, an automation platform similar to IFTTT/Zapier.

## 🚀 Implemented Features

### ✅ Authentication and User Management
- ✅ User registration with validation
- ✅ JWT Authentication (Access + Refresh tokens)
- ✅ **Email verification with token system** (ENFORCED - required before app usage)
- ✅ User profile management
- ✅ Brute force protection (throttling)
- ✅ Complete input data validation

### 🔧 Technical Architecture
- **Framework**: Django 5.2.6 + Django REST Framework
- **Authentication**: JWT with djangorestframework-simplejwt
- **Database**: PostgreSQL
- **Tests**: 32 unit tests with 100% success rate
- **Email**: SMTP Gmail configured

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## ⚙️ Installation and Configuration

### 1. Clone the project
```bash
git clone <repository-url>
cd Area/backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment configuration

Create a `.env` file at the root of the backend folder:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True

# JWT Configuration
JWT_SIGNING_KEY=your-jwt-signing-key-here

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Database Configuration
DB_NAME=area_db
DB_USER=area_user
DB_PASSWORD=your-db-password
POSTGRES_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Database configuration

Create the PostgreSQL database:
```sql
CREATE DATABASE area_db;
CREATE USER area_user WITH PASSWORD 'your-db-password';
GRANT ALL PRIVILEGES ON DATABASE area_db TO area_user;
```

### 6. Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a superuser (optional)
```bash
python manage.py createsuperuser
```

### 8. Start the development server
```bash
python manage.py runserver 0.0.0.0:8080
```

The API will be accessible at `http://localhost:8080`

## 📚 API Documentation

### Base URL
```
http://localhost:8080
```

### 🔐 Authentication Endpoints

#### 1. User Registration
```http
POST /auth/register/
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123",
    "password2": "SecurePassword123"
}
```

**Response (201 Created):**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "email_verified": false
}
```

#### 2. Login
```http
POST /auth/login/
Content-Type: application/json

{
    "username": "john_doe",
    "password": "SecurePassword123"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 3. Token Refresh
```http
POST /auth/login/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 4. User Profile
```http
GET /auth/me/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response (200 OK):**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "email_verified": false
}
```

### 📧 Email Verification Endpoints

#### 5. Request Email Verification
```http
POST /auth/send-verification-email/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response (200 OK):**
```json
{
    "message": "Verification email sent successfully"
}
```

#### 6. Verify Email
```http
GET /auth/verify-email/{token}/
```

**Response (200 OK):**
```json
{
    "message": "Email verified successfully"
}
```

### 🚫 Error Handling

#### Authentication Errors (401)
```json
{
    "detail": "Invalid credentials"
}
```

#### Validation Errors (400)
```json
{
    "username": ["This field is required."],
    "password": ["Password fields didn't match."]
}
```

#### Rate Limit Exceeded (429)
```json
{
    "detail": "Request was throttled. Expected available in 86400 seconds."
}
```

### 🔧 JWT Configuration

- **Access Token**: 15 minutes lifetime
- **Refresh Token**: 7 days lifetime
- **Token Rotation**: Enabled (new refresh tokens on each refresh)
- **Blacklist**: Enabled (old tokens invalidated)

## 🧪 Testing

### Run all tests
```bash
python manage.py test users.tests
```

### Run tests with detailed coverage
```bash
python manage.py test users.tests -v 2
```

### Available tests
- **32 unit tests** covering:
  - Complete authentication flow
  - Input data validation
  - Error handling and failure cases
  - Security and protection
  - Email verification
  - Edge cases and special scenarios

## 🔒 Security

### Implemented security measures
- ✅ **Secure password hashing** (PBKDF2 with salt)
- ✅ **Password validation** (length, complexity)
- ✅ **JWT with short expiration** (15 min for access token)
- ✅ **Rate limiting** (request throttling)
- ✅ **Strict input validation**
- ✅ **CSRF protection** enabled
- ✅ **Security headers** configured

### Sensitive environment variables
- `SECRET_KEY`: Django secret key
- `JWT_SIGNING_KEY`: JWT signing key
- `EMAIL_HOST_PASSWORD`: Email password
- `DB_PASSWORD`: Database password

⚠️ **Never commit the .env file to version control!**

## 🚀 Deployment

### Production environment variables
```env
DEBUG=False
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

### Deployment commands
```bash
# Collect static files
python manage.py collectstatic

# Deployment check
python manage.py check --deploy
```

## 📁 Project Structure

```
backend/
├── area_project/          # Django configuration
│   ├── settings.py        # Main settings
│   ├── urls.py           # Main URLs
│   └── wsgi.py           # WSGI configuration
├── users/                # Users application
│   ├── models.py         # User and ServiceToken models
│   ├── views.py          # REST API views
│   ├── serializers.py    # DRF serializers
│   ├── urls.py           # App URLs
│   └── tests.py          # Unit tests
├── automations/          # AREA application (to be developed)
├── requirements.txt      # Python dependencies
├── manage.py            # Django utility
└── README.md            # This documentation
```

## 🛠️ Development

### Adding a new feature
1. Create/modify models in `models.py`
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Create serializers in `serializers.py`
5. Create views in `views.py`
6. Add URLs in `urls.py`
7. Write tests in `tests.py`
8. Test: `python manage.py test`

### Code standards
- Follow PEP 8 conventions
- Document complex functions
- Write tests for each new feature
- Use explicit variable names

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📞 Support

For any questions or issues:
1. Check the documentation above
2. Consult the tests for usage examples
3. Create an issue on the GitHub repository

## 📈 Roadmap (Upcoming versions)

- [ ] OAuth2 integration (Google, Facebook, GitHub)
- [ ] Services management (Gmail, GitHub, etc.)
- [ ] Actions and REActions system
- [ ] Webhook system for automation triggers
- [ ] Admin dashboard
- [ ] API rate limiting per user
- [ ] Metrics and monitoring

---

**Version**: 1.0.0
**Last updated**: September 2025
**Status**: ✅ Ready for Production (Authentication Module)
