import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

import cloudinary
import cloudinary.uploader
import cloudinary.api

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env for local development. `.env` is gitignored and never deployed, so
# letting it win avoids ambient shell variables (e.g. a stray DEBUG=release from
# other tooling) silently overriding project config on a developer machine.
# In production there is no .env file, so real platform env vars are used as-is.
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env', override=True)
except ImportError:
    pass


def _as_bool(value, default=False):
    if value is None or value == '':
        return default
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}


DEBUG = _as_bool(os.environ.get('DEBUG'), default=True)

# Collected below and reported once, so a missing third-party key degrades that
# one feature instead of taking the whole site down.
_MISSING_ENV = []


def env(name, default=None, required_in_production=False, critical=False):
    """Read a setting from the environment.

    Secrets must never have a hardcoded fallback: a committed default silently
    becomes the production value and leaks through version control.

    `critical=True` means the app is unsafe to run without it, so we abort.
    `required_in_production=True` only warns: losing email or media uploads
    should not break every page, and Django swallows import-time exceptions
    into a confusing "Unknown command" during manage.py, which hides the cause.
    """
    value = os.environ.get(name, '')
    if value:
        return value
    if not DEBUG and (critical or required_in_production):
        _MISSING_ENV.append(name)
        if critical:
            message = (
                f"\n{'=' * 70}\n"
                f"FATAL: required environment variable {name} is not set.\n"
                f"Set it in your hosting provider's environment (see .env.example).\n"
                f"{'=' * 70}\n"
            )
            # Print before raising: Django hides settings-import exceptions
            # behind "Unknown command", so the reason would otherwise be lost.
            sys.stderr.write(message)
            sys.stderr.flush()
            raise ImproperlyConfigured(f"Missing required environment variable: {name}")
    return default


SECRET_KEY = env('SECRET_KEY', critical=True)
if not SECRET_KEY:
    # DEBUG-only ephemeral key; rotates each restart, never committed.
    from django.core.management.utils import get_random_secret_key
    SECRET_KEY = get_random_secret_key()

ALLOWED_HOSTS = [h.strip() for h in env('ALLOWED_HOSTS', '*').split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'auth_kirtan',
    'patient_roshan',
    'doctor_siddhartha',
    'admin_nishan',
    'anymail',
    'cloudinary',
    'cloudinary_storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hospital.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'hospital.notifications.notification_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'hospital.wsgi.application'

DATABASE_URL = os.environ.get('DATABASE_URL')

print(f"[DB CHECK] DATABASE_URL env var set: {'Yes' if DATABASE_URL else 'No'}")
if DATABASE_URL:
    db_prefix = DATABASE_URL.split('://')[0] if '://' in DATABASE_URL else 'unknown'
    print(f"[DB CHECK] DATABASE_URL starts with: {db_prefix}")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True),
    }
    print(f"[DB CHECK] Using database engine: {DATABASES['default']['ENGINE']}")
    print(f"[DB CHECK] Using database name: {DATABASES['default'].get('NAME', 'unknown')}")
    print(f"[DB CHECK] Using database host: {DATABASES['default'].get('HOST', 'unknown')}")
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print(f"[DB CHECK] DATABASE_URL not set. Using SQLite for local development.")

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/patient/'
LOGOUT_REDIRECT_URL = '/login/'

# ============ EMAIL CONFIG (Mailgun via django-anymail) ============
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', '')
ANYMAIL = {
    'MAILGUN_API_KEY': env('MAILGUN_API_KEY', '', required_in_production=True),
    'MAILGUN_SENDER_DOMAIN': env('MAILGUN_SENDER_DOMAIN', ''),
}

# ============ CLOUDINARY CONFIGURATION ============
CLOUDINARY_CLOUD_NAME = env('CLOUDINARY_CLOUD_NAME', '', required_in_production=True)
CLOUDINARY_API_KEY = env('CLOUDINARY_API_KEY', '', required_in_production=True)
CLOUDINARY_API_SECRET = env('CLOUDINARY_API_SECRET', '', required_in_production=True)

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
    'API_KEY': CLOUDINARY_API_KEY,
    'API_SECRET': CLOUDINARY_API_SECRET,
}

# ============ STORAGE BACKEND ============
# Use Cloudinary for media files
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Keep these for backward compatibility
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# eSewa ePay v2. EPAYTEST and the sandbox URLs are eSewa's public test values,
# so they are safe as non-secret defaults; the secret key is not.
ESEWA_PRODUCT_CODE = env('ESEWA_PRODUCT_CODE', 'EPAYTEST')
ESEWA_SECRET_KEY = env('ESEWA_SECRET_KEY', '', required_in_production=True)
ESEWA_FORM_URL = env('ESEWA_FORM_URL', 'https://rc-epay.esewa.com.np/api/epay/main/v2/form')
ESEWA_STATUS_URL = env('ESEWA_STATUS_URL', 'https://rc-epay.esewa.com.np/api/epay/transaction/status/')

# Payment gateways redirect back to this host, so it must be the public URL in production.
SITE_BASE_URL = env('SITE_BASE_URL', 'http://127.0.0.1:8000')

# Khalti - get a test key from dev.khalti.com
KHALTI_SECRET_KEY = env('KHALTI_SECRET_KEY', '', required_in_production=True)
KHALTI_INITIATE_URL = env('KHALTI_INITIATE_URL', 'https://dev.khalti.com/api/v2/epayment/initiate/')
KHALTI_LOOKUP_URL = env('KHALTI_LOOKUP_URL', 'https://dev.khalti.com/api/v2/epayment/lookup/')


# ============ CONFIG WARNINGS ============
# Report every non-fatal gap once, so the build log names what is unset instead
# of the feature failing mysteriously later at runtime.
if _MISSING_ENV:
    _impact = {
        'CLOUDINARY_CLOUD_NAME': 'image/media uploads',
        'CLOUDINARY_API_KEY': 'image/media uploads',
        'CLOUDINARY_API_SECRET': 'image/media uploads',
        'MAILGUN_API_KEY': 'outgoing email (password reset)',
        'ESEWA_SECRET_KEY': 'eSewa payments',
        'KHALTI_SECRET_KEY': 'Khalti payments',
    }
    sys.stderr.write(
        "\n[CONFIG WARNING] Running with DEBUG=False but these environment "
        "variables are not set:\n"
    )
    for _name in _MISSING_ENV:
        sys.stderr.write(f"  - {_name}  -> disables: {_impact.get(_name, 'related feature')}\n")
    sys.stderr.write("  See .env.example. The site will run, but those features will fail.\n\n")
    sys.stderr.flush()