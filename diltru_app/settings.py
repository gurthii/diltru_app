import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# load .env if it exists
env_path = os.path.join(BASE_DIR, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') == 'True'

# ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
# ALLOWED_HOSTS = ['appsbyjoe.pythonanywhere.com', 'localhost', '127.0.0.1'] # going-live

ALLOWED_HOSTS = ['onrender.com', 'localhost', '127.0.0.1', '.onrender.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party apps
    'rest_framework',
    'rest_framework.authtoken', # usable when dealing with js (front end UI for users)
    'corsheaders',
    'django_filters',
    'drf_spectacular', # added Swagger for API documentation 

    # my apps
    'products',
    'users', # customizing base User model
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'diltru_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/ 'templates'], # instructs on the location of my templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'diltru_app.wsgi.application'


# Database Config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Production (Render.com)
# If running on the server, always use the internal Render DB.
if os.getenv('RENDER'):
    DATABASES['default'] = dj_database_url.config(conn_max_age=600)

# 2. The Switch
# When I run the scheduler locally, it forces USE_CLOUD_DB to true
# meaning, Use Cloud DB (update prices to online db).
elif os.getenv('USE_CLOUD_DB') == 'True':
    DATABASES['default'] = dj_database_url.parse(os.getenv('CLOUD_DATABASE_URL'))
    print("‼️  WARNING: Connected to Production Database (Render)!")

# 3. Local (Laptop Website)
# Otherwise -> Stay on Local SQLite (Safe Mode).
else:
    print("💻 Connected to Local Database (SQLite)")

"""
To effect migrations locally and to cloud
Local:
py manage.py makemigrations
py manage.py migrate

Production: temporarily switch USE_CLOUD_DB to True using PowerShell or manually edit .env; Important since scheduler runs locally to avoid 'missing column errors'

$env:USE_CLOUD_DB="True"; py manage.py makemigrations
py manage.py migrate

"""
# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # tells Django where to put files when 'collectstatic' is run going-live

# applicable if there's global static folder for custom CSS/JS
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# Enable WhiteNoise compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# for local testing
CORS_ALLOW_ALL_ORIGINS = True

AUTH_USER_MODEL = 'users.CustomUser' # Django will use my custom model instead of the default

# Redirect behaviour upon loginng in via browser - go to api root
LOGIN_REDIRECT_URL = '/api/alerts/'
LOGOUT_REDIRECT_URL = '/api/alerts/'

# Session management and other settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication', # For your JS Frontend
        'rest_framework.authentication.SessionAuthentication', # Keep this for the Admin panel
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # 10 items per page

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema', # for Swagger
}

# Email Configuration

# Check if we are running on Render (Render automatically sets this variable)
if os.getenv('RENDER'):
    # In prod: Use Brevo API (Port 443) - Guaranteed Delivery 
    INSTALLED_APPS += ['anymail']
    EMAIL_BACKEND = "anymail.backends.sendinblue.EmailBackend"  # Note: Internal name is still 'sendinblue'
    
    ANYMAIL = {
        "SENDINBLUE_API_KEY": os.getenv('BREVO_API_KEY'),
    }
    
    # Must match your verified sender in Brevo
    DEFAULT_FROM_EMAIL = os.getenv('EMAIL_USER') 

else:
    # Use Gmail SMTP (Port 587) for easy local testing
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    EMAIL_HOST_USER = os.getenv('EMAIL_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
    DEFAULT_FROM_EMAIL = f'dilTru Alerts <{os.getenv("EMAIL_USER")}>'