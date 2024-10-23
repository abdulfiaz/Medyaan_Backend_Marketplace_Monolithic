"""
Django settings for sdd_marketplace project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import json

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if os.path.isfile('env.json'):
    with open('env.json') as f:
        data = json.load(f)

        try:
            db_name = data["db_name"]
        except:
            db_name = os.environ['DB_NAME']
        try:
            db_password = data["db_password"]
        except:
            db_password = os.environ["db_password"]
        try:
            db_user = data['db_user']
        except:
            db_user = os.environ['DB_USERNAME']
        try:
            db_host = data['db_host']
        except:
            db_host = os.environ['DB_HOSTNAME']
        try:
            db_port = data['db_port']
        except:
            db_port = os.environ['DB_PORT']

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5oo7#u1mcgr*1r(t_co9c5f@7lnjsf#r87tf%fma_%u7gmwl^h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'users',  # For managing users,
    'seller', # For managing sellers,
    'order',  # For managing orders,  
    'adminapp', #User defined application to manage the admin functionalities

]
# jwt setup

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

# JWT Authentication settings
import datetime

JWT_AUTH = {
    'JWT_VERIFY': data['JWT_VERIFY'],
    'JWT_VERIFY_EXPIRATION': data['JWT_VERIFY_EXPIRATION'],
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=data['JWT_EXPIRATION_TIME']),  # Token expiration time
    'JWT_ALLOW_REFRESH': True,  # Allow refresh token
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),  # Refresh token expiration
    'JWT_AUTH_HEADER_PREFIX': data['JWT_AUTH_HEADER_PREFIX'],
    'JWT_ALGORITHM': data['JWT_ALGORITHM'],
    'JWT_PAYLOAD_HANDLER': data['JWT_PAYLOAD_HANDLER'],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sdd_marketplace.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'sdd_marketplace.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_name,
        'USER': db_user,
        'PASSWORD': db_password,
        'HOST': db_host,
        'PORT': db_port
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = 'users.CustomUser'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "POST", "PUT"]
CORS_ALLOW_HEADERS = [
    "accept",
    "accepts",
    "accept-encoding",
    "authorization",
    "content-type",
    "content-disposition",
    "content-length",
    "cache-control",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "timezone"
]

# CORS Policy
CORS_ORIGIN_ALLOW_ALL = CORS_ORIGIN_ALLOW_ALL

CORS_ALLOW_METHODS = CORS_ALLOW_METHODS

CORS_ALLOW_HEADERS = CORS_ALLOW_HEADERS
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
