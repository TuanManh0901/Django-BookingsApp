"""
Django settings for vn_travel project.
"""

from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-new-secret-key-generated-abcdef1234567890')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS
import os
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Render.com support
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Add Render domain to CSRF trusted origins
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'

# Session Settings
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
    # django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # project apps
    "vn_travel",
    "tours",
    "bookings",
    "payments",
    "telegram_bot",
    "ai_chatbot",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Must be right after SecurityMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "vn_travel.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "vn_travel.wsgi.application"

# Database
import os
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Parse DATABASE_URL (format: postgresql://user:pass@host:port/dbname)
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
    if match:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "USER": match.group(1),
                "PASSWORD": match.group(2),
                "HOST": match.group(3),
                "PORT": match.group(4),
                "NAME": match.group(5),
            }
        }
    else:
        # Fallback to individual config
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": config('DATABASE_NAME', default='vn_travel_db'),
                "USER": config('DATABASE_USER', default='postgres'),
                "PASSWORD": config('DATABASE_PASSWORD', default='1'),
                "HOST": config('DATABASE_HOST', default='localhost'),
                "PORT": config('DATABASE_PORT', default='5432'),
            }
        }
else:
    # Use individual config vars (for Render)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config('DB_NAME', default='vn_travel_db'),
            "USER": config('DB_USER', default='postgres'),
            "PASSWORD": config('DB_PASSWORD', default=''),
            "HOST": config('DB_HOST', default='localhost'),
            "PORT": config('DB_PORT', default='5432'),
        }
    }

# Site URL for MoMo callbacks
# Site URL configuration - Auto-detect for production
# This is CRITICAL for MoMo payment redirectUrl/ipnUrl!
if RENDER_EXTERNAL_HOSTNAME:
    # Production on Render - use HTTPS with Render hostname
    SITE_URL = f'https://{RENDER_EXTERNAL_HOSTNAME}'
else:
    # Local development - use config or default to localhost
    SITE_URL = config('SITE_URL', default='http://127.0.0.1:8000')

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "vi"

LANGUAGES = [
    ('en', 'English'),
    ('vi', 'Tiếng Việt'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

USE_I18N = True
TIME_ZONE = "Asia/Ho_Chi_Minh"
USE_TZ = True

# Static files
STATIC_URL = "static/"
# Include both regular static files AND static/media (tour images)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"  # For production collectstatic

# WhiteNoise middleware (in MIDDLEWARE) will serve static files
# Don't use custom STATICFILES_STORAGE - causes issues with admin files

# Media files - in production served from static/ via collectstatic
# In development: /media/ folder, in production: /static/media/ folder
MEDIA_URL = "/static/media/" if not DEBUG else "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication settings
LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": config('GOOGLE_CLIENT_ID', default=''),
            "secret": config('GOOGLE_CLIENT_SECRET', default=''),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {
            "access_type": "online",
            "prompt": "select_account"
        },
    }
}

# Allauth settings
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
# CRITICAL: Set to False to allow Google OAuth auto-signup without form!
ACCOUNT_USERNAME_REQUIRED = False  # Changed from True
ACCOUNT_SESSION_REMEMBER = True

# Social Account Auto Signup - Skip signup form completely
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # Skip email verification
SOCIALACCOUNT_EMAIL_REQUIRED = False  # Don't require email from social provider
SOCIALACCOUNT_QUERY_EMAIL = True  # Try to get email from provider
SOCIALACCOUNT_STORE_TOKENS = False  # Don't store OAuth tokens

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1

# Disable allauth messages
SOCIALACCOUNT_FORMS = {}
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
ACCOUNT_ADAPTER = 'vn_travel.allauth_signals.NoMessagesAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'vn_travel.allauth_signals.NoMessagesSocialAccountAdapter'

# Momo Payment Settings
MOMO_ACCESS_KEY = config('MOMO_ACCESS_KEY', default='F8BBA842ECF85')
MOMO_SECRET_KEY = config('MOMO_SECRET_KEY', default='K951B6PE1waDMi640xX08PD3vg6EkVlz')
MOMO_PARTNER_CODE = config('MOMO_PARTNER_CODE', default='MOMO')
MOMO_ENDPOINT = config('MOMO_ENDPOINT', default='https://test-payment.momo.vn/v2/gateway/api/create')
MOMO_MOCK_ENABLED = config('MOMO_MOCK_ENABLED', default='false').lower() == 'true'

# Telegram Bot Settings
TELEGRAM_BOT_TOKEN = config('TELEGRAM_TOKEN', default='')

# Gemini AI Settings
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')

# OpenWeather API
OPENWEATHER_API_KEY = config('OPENWEATHER_KEY', default='')

# Google Maps API
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default='')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'payments': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=f'VN Travel <{config("EMAIL_HOST_USER", default="noreply@vntravel.com")}>')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_TIMEOUT = 10
