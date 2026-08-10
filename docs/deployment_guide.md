# Deployment Guide

## 1. Local Development Setup

### 1.1 Prerequisites
- Python 3.10 or higher
- Git
- Virtual environment tool (venv or virtualenv)

### 1.2 Installation Steps

```bash
# Clone the repository
git clone https://github.com/your-username/hospital-management-system.git
cd hospital-management-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver
```

### 1.3 Environment Variables (Development)

Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Email (Mailgun)
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=your-mailgun-domain
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Cloudinary (Optional for local dev)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Site URL
SITE_URL=http://localhost:8000
```

## 2. Production Deployment on Render

### 2.1 Pre-Deployment Checklist
- [ ] Set `DEBUG=False` in production settings
- [ ] Configure PostgreSQL database (Neon)
- [ ] Set up Cloudinary for media storage
- [ ] Configure Mailgun for email
- [ ] Update `ALLOWED_HOSTS` with Render domain
- [ ] Set `SECURE_SSL_REDIRECT=True`

### 2.2 Render Configuration

#### 2.2.1 Create PostgreSQL Database on Neon
1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string (Format: `postgresql://user:pass@host/dbname`)

#### 2.2.2 Create Web Service on Render
1. Sign up at [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure the following settings:

| Setting | Value |
|---------|-------|
| Name | hospital-management-system |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate` |
| Start Command | `gunicorn hospital.wsgi:application` |
| Plan | Free |

#### 2.2.3 Environment Variables on Render

Add these environment variables in Render dashboard:

```env
# Core Settings
DEBUG=False
SECRET_KEY=<generate-a-secure-secret-key>
ALLOWED_HOSTS=your-app-name.onrender.com,.onrender.com

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@hostname:port/database

# Email (Mailgun)
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=your-mailgun-domain
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Site Configuration
SITE_URL=https://your-app-name.onrender.com

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2.3 Render Deployment Steps

1. **Push code to GitHub**
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

2. **Connect Repository on Render**
   - Go to Render Dashboard
   - Click "New" → "Web Service"
   - Select your repository
   - Render will auto-detect Django

3. **Add Environment Variables**
   - Go to "Environment" tab
   - Add all variables listed above

4. **Add PostgreSQL Database**
   - Click "New" → "PostgreSQL"
   - Copy the `DATABASE_URL`
   - Add it to your Web Service environment variables

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build to complete
   - Your app will be live at `https://your-app-name.onrender.com`

## 3. Neon PostgreSQL Setup

### 3.1 Creating Neon Database

```bash
# Using Neon CLI
npm install -g neonctl
neonctl projects create
neonctl branches create main
neonctl connection-string main
```

### 3.2 Database Migration

After deployment, run migrations:

```bash
# Via Render Shell
render shell

# In shell
python manage.py migrate
python manage.py createsuperuser
```

### 3.3 Database Configuration in settings.py

```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}
```

## 4. Cloudinary Configuration

### 4.1 Setup Steps

1. Sign up at [cloudinary.com](https://cloudinary.com)
2. Get your credentials from Dashboard
3. Install Cloudinary packages:
```bash
pip install cloudinary django-cloudinary-storage
```

### 4.2 Configuration in settings.py

```python
# settings.py
INSTALLED_APPS = [
    ...
    'cloudinary',
    'cloudinary_storage',
    ...
]

# Media Storage
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Cloudinary Configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}
```

### 4.3 Model Configuration

```python
# In models.py
from cloudinary.models import CloudinaryField

class PatientProfile(models.Model):
    profile_picture = CloudinaryField(
        'profile_picture',
        folder='hospital/profile_pictures/patients',
        blank=True,
        null=True
    )

class DoctorProfile(models.Model):
    profile_picture = CloudinaryField(
        'profile_picture',
        folder='hospital/profile_pictures/doctors',
        blank=True,
        null=True
    )
```

## 5. Mailgun Email Setup

### 5.1 Setup Steps

1. Sign up at [mailgun.com](https://www.mailgun.com)
2. Verify your domain
3. Get API credentials

### 5.2 Install django-anymail

```bash
pip install django-anymail
```

### 5.3 Configuration in settings.py

```python
# Email Backend
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'

# Mailgun Settings
ANYMAIL = {
    'MAILGUN_API_KEY': os.environ.get('MAILGUN_API_KEY'),
    'MAILGUN_SENDER_DOMAIN': os.environ.get('MAILGUN_DOMAIN'),
}

# Default sender
DEFAULT_FROM_EMAIL = f'HMS <noreply@{os.environ.get("MAILGUN_DOMAIN")}>`
SERVER_EMAIL = DEFAULT_FROM_EMAIL
```

### 5.4 Password Reset Email Template

```python
# auth_kirtan/views.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_password_reset_email(user, token):
    subject = 'Password Reset Request - Hospital Management System'
    html_message = render_to_string('emails/password_reset.html', {
        'user': user,
        'token': token,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
    )
```

## 6. Gunicorn Configuration

Create `gunicorn.conf.py` in project root:

```python
bind = "0.0.0.0:8000"
workers = 3
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
```

## 7. Build Script (build.sh)

```bash
#!/bin/bash
# Render build script

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Create superuser if not exists
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', '[REDACTED EMAIL]', '[REDACTED PASSWORD]')" | python manage.py shell
```

## 8. Troubleshooting

| Issue | Solution |
|-------|----------|
| Database connection error | Check DATABASE_URL format and credentials |
| Static files not loading | Run `collectstatic` and check STATIC_ROOT |
| Media files not uploading | Verify Cloudinary credentials |
| Email not sending | Check Mailgun API key and domain verification |
| 500 error on Render | Check logs in Render dashboard |
| Migration errors | Run `python manage.py makemigrations` locally first |

## 9. Post-Deployment Checklist

- [ ] Verify all pages load correctly
- [ ] Test user registration and login
- [ ] Test appointment booking flow
- [ ] Verify email notifications are sent
- [ ] Check profile picture uploads to Cloudinary
- [ ] Test admin dashboard access
- [ ] Verify database connections
- [ ] Check SSL certificate is active
- [ ] Test on mobile devices
