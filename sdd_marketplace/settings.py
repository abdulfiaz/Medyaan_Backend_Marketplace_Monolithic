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

        try:
            JWT_VERIFY = data["JWT_VERIFY"]
        except:
            JWT_VERIFY = os.environ["JWT_VERIFY"]
        try:
            JWT_VERIFY_EXPIRATION = data["JWT_VERIFY_EXPIRATION"]
        except:
            JWT_VERIFY_EXPIRATION = os.environ["JWT_VERIFY_EXPIRATION"]
        try:
            JWT_EXPIRATION_TIME = data["JWT_EXPIRATION_TIME"]
        except:
            JWT_EXPIRATION_TIME = os.environ["JWT_EXPIRATION_TIME"]
        try:
            JWT_AUTH_HEADER_PREFIX = data["JWT_AUTH_HEADER_PREFIX"]
        except:
            JWT_AUTH_HEADER_PREFIX = os.environ["JWT_AUTH_HEADER_PREFIX"]
        try:
            JWT_ALGORITHM = data["JWT_ALGORITHM"]
        except:
            JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
        try:
            JWT_PAYLOAD_HANDLER = data["JWT_PAYLOAD_HANDLER"]
        except:
            JWT_PAYLOAD_HANDLER = os.environ["JWT_PAYLOAD_HANDLER"]
    
        try:
            APPLICATION_HOST = data["APPLICATION_HOST"]
        except:
            APPLICATION_HOST = os.environ["APPLICATION_HOST"]
        try:
            BACKENDHOST = data["BACKENDHOST"]
        except:
            BACKENDHOST = os.environ["BACKENDHOST"]

        try:
            REDISHOST = data["REDISHOST"]
        except:
            REDISHOST = os.environ["REDISHOST"]
        try:
            REDISPORT = data["REDISPORT"]
        except:
            REDISPORT = os.environ["REDISPORT"]

        try:
            TIME_ZONE = data['TIME_ZONE']
        except:
            TIME_ZONE = os.environ['TIME_ZONE']

        try:
            EMAIL_HOST = data['EMAIL_HOST']
        except:
            EMAIL_HOST = os.environ['EMAIL_HOST']

        try:
            EMAIL_HOST_PASSWORD = data['EMAIL_HOST_PASSWORD']
        except:
            EMAIL_HOST_PASSWORD = data['EMAIL_HOST_PASSWORD']

        try:
            EMAIL_PORT = data['EMAIL_PORT']
        except:
            EMAIL_PORT = os.environ['EMAIL_PORT']

        try:
            EMAIL_HOST_USER = data['EMAIL_HOST_USER']
        except:
            EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']

        try:
            EMAIL_USE_TLS = data['EMAIL_USE_TLS']
        except:
            EMAIL_USE_TLS = os.environ['EMAIL_USE_TLS']

        try:
            RAK_AWS_OWNER = data['RAK_AWS_OWNER']
        except:
            RAK_AWS_OWNER = os.environ['RAK_AWS_OWNER']

        try:
            SMTP_SERVER = data["SMTP_SERVER"]
        except:
            SMTP_SERVER = os.environ["SMTP_SERVER"]
        
        try:
            SMTP_PORT = data["SMTP_PORT"]
        except:
            SMTP_PORT = os.environ["SMTP_PORT"]

        try:
            SMTP_USERNAME = data["SMTP_USERNAME"]
        except:
            SMTP_USERNAME = os.environ["SMTP_USERNAME"]

        try:
            SMTP_PASSWORD = data["SMTP_PASSWORD"]
        except:
            SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]

else:
    db_name = os.environ['DB_NAME']
    db_user = os.environ['DB_USERNAME']
    db_password = os.environ['DB_PASSWORD']
    db_host = os.environ['DB_HOSTNAME']
    db_port = os.environ['DB_PORT']

    logsdb_name = os.environ["logsdb_name"]
    logsdb_password = os.environ["logsdb_password"]
    logsdb_user = os.environ['logsdb_user']
    logsdb_host = os.environ['logsdb_host']
    logsdb_port = os.environ['logsdb_port']


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

    'JWT_VERIFY': JWT_VERIFY,
    'JWT_VERIFY_EXPIRATION': JWT_VERIFY_EXPIRATION,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=int(JWT_EXPIRATION_TIME)),
    'JWT_AUTH_HEADER_PREFIX': JWT_AUTH_HEADER_PREFIX,
    'JWT_ALGORITHM': JWT_ALGORITHM,
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_ALLOW_REFRESH': True,

    'JWT_ENCODE_HANDLER': 'users.utils.jwt_encode_handler',
    'JWT_DECODE_HANDLER': 'users.utils.jwt_decode_handler',
    'JWT_PAYLOAD_HANDLER': 'users.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USERNAME_HANDLER': 'users.utils.jwt_get_userid_from_payload_handler',

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
