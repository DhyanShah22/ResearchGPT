import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Ensure this path exists
]

# Optionally, collect static files in production
STATIC_ROOT = BASE_DIR / "staticfiles"


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = os.path.dirname(BASE_DIR)  # Move up one level to the main project directory

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
ROOT_URLCONF = 'backend.urls'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',  # Added CORS support
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Ensure it's before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy',
    }
}


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
            ],
        },
    },
]

# Static and Media Files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_DIR, "data")  # Ensuring data folder is outside `backend/`

# Ensure media directory exists
os.makedirs(MEDIA_ROOT, exist_ok=True)

# File upload settings
FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]

# CORS settings (for development, restrict in production)
CORS_ALLOW_ALL_ORIGINS = True

# Default primary key type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
