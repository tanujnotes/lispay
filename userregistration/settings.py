"""
Django settings for userregistration project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

from .local_settings import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_DIR = os.path.join(BASE_DIR, 'static')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')

REGISTRATION_OPEN = REGISTRATION_OPEN_VALUE
ACCOUNT_ACTIVATION_DAYS = 1
INCLUDE_AUTH_URLS = True
INCLUDE_REGISTER_URL = True
REGISTRATION_AUTO_LOGIN = False
LOGIN_REDIRECT_URL = '/login-redirect/'
LOGIN_URL = '/accounts/login/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = EMAIL_HOST_USER_VALUE
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD_VALUE  # This is not your gmail password.
EMAIL_USE_TLS = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY_VALUE

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DEBUG_VALUE

ALLOWED_HOSTS = ALLOWED_HOSTS_VALUE

RAVEN_CONFIG = RAVEN_CONFIG_VALUE

# Application definition

INSTALLED_APPS = [
    'django.contrib.postgres',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'regapp',  # Should be above registration
    'registration',  # Should be above admin and immediately above auth
    'django.contrib.auth',
    'django.contrib.admin',
    'raven.contrib.django.raven_compat',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'userregistration.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.static',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'userregistration.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': DATABASE_VALUE
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'development_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': 'logs/django_dev.log',
            'formatter': 'verbose'
        },
        'production_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django_production.log',
            'maxBytes': 1024 * 1024 * 100,  # 100MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'dba_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_false', 'require_debug_true'],
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': 'logs/django_dba.log',
            'formatter': 'simple'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'loggers': {
        'regapp': {
            'handlers': ['development_logfile', 'production_logfile'],
        },
        'dash': {
            'handlers': ['development_logfile', 'production_logfile'],
        },
        'dba': {
            'handlers': ['dba_logfile'],
        },
        'django': {
            'handlers': ['development_logfile', 'production_logfile'],
        },
        'py.warnings': {
            'handlers': ['development_logfile'],
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

# STATIC_URL = '/static/'
# STATICFILES_DIRS = [STATIC_DIR, ]

MEDIA_ROOT = MEDIA_DIR
MEDIA_URL = '/media/'

SITE_ID = 1

AUTH_USER_MODEL = 'regapp.MyUser'

# AWS
AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID_VALUE
AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY_VALUE
AWS_S3_REGION_NAME = AWS_S3_REGION_NAME_VALUE
AWS_STORAGE_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME_VALUE
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

AWS_LOCATION = 'static'

STATICFILES_DIRS = [STATIC_DIR, ]
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)

DEFAULT_FILE_STORAGE = 'userregistration.storage_backends.MediaStorage'

# To make collectstatic only upload new files to S3
# AWS_PRELOAD_METADATA = True
