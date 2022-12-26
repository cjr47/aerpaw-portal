"""
Django settings for drf project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# Session expiration settings - 4 hours or browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 14400

# SECURITY WARNING: don't run with debug turned on in production!
if os.getenv('DJANGO_DEBUG').casefold() == 'true':
    DEBUG = True
else:
    DEBUG = False

# AERPAW OPS WARNING: don't run with mock turned on in production!
if os.getenv('AERPAW_OPS_MOCK').casefold() == 'true':
    MOCK_OPS = True
else:
    MOCK_OPS = False

# ALLOWED_HOSTS = ['.localhost', '127.0.0.1', '[::1]']
ALLOWED_HOSTS = [os.getenv('DJANGO_ALLOWED_HOSTS')]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'mozilla_django_oidc',  # Load after auth
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_bootstrap5',  # django bootstrap
    'fontawesomefree',  # fontawesome free version
    'portal.apps.mixins',  # mixins
    'portal.apps.users',  # custom user model
    'portal.apps.profiles',  # custom user profile
    'portal.apps.resources',  # resources
    'portal.apps.projects',  # projects
    'portal.apps.experiment_files',  # experiment files
    'portal.apps.experiments',  # experiments
    'portal.apps.operations',  # operations
    'portal.apps.credentials',  # credentials
    'portal.apps.user_messages',  # user messages
    'portal.apps.user_requests',  # user requests
]

# Add 'mozilla_django_oidc' authentication backend
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # used for admin created by
    # 'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
    'portal.apps.users.oidc_users.MyOIDCAB',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'mozilla_django_oidc.contrib.drf.OIDCAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    # metadata settings
    'DEFAULT_METADATA_CLASS': 'portal.server.drf_settings.MinimalMetadata',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=float(os.getenv('ACCESS_TOKEN_LIFETIME_HOURS'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=float(os.getenv('REFRESH_TOKEN_LIFETIME_DAYS'))),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

ROOT_URLCONF = 'portal.server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates/credentials'),
            os.path.join(BASE_DIR, 'templates/experiment_files'),
            os.path.join(BASE_DIR, 'templates/experiments'),
            os.path.join(BASE_DIR, 'templates/portal'),
            os.path.join(BASE_DIR, 'templates/profiles'),
            os.path.join(BASE_DIR, 'templates/projects'),
            os.path.join(BASE_DIR, 'templates/resources'),
            os.path.join(BASE_DIR, 'templates/rest_framework'),
            os.path.join(BASE_DIR, 'templates/user_messages'),
            os.path.join(BASE_DIR, 'templates/user_requests'),
        ],
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

WSGI_APPLICATION = 'portal.server.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT')
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.getenv('DJANGO_TIME_ZONE')

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'server/static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login/Logout redirects
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# mozilla-django-oidc
# https://mozilla-django-oidc.readthedocs.io/en/stable/index.html

# client id and client secret
OIDC_RP_CLIENT_ID = os.getenv('OIDC_RP_CLIENT_ID', None)
OIDC_RP_CLIENT_SECRET = os.getenv('OIDC_RP_CLIENT_SECRET', None)
# signing algorithm
OIDC_RP_SIGN_ALGO = os.getenv('OIDC_RP_SIGN_ALGO')
OIDC_OP_JWKS_ENDPOINT = os.getenv('OIDC_OP_JWKS_ENDPOINT')
# OpenID Connect provider (CILogon)
OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv('OIDC_OP_AUTHORIZATION_ENDPOINT')
OIDC_OP_TOKEN_ENDPOINT = os.getenv('OIDC_OP_TOKEN_ENDPOINT')
OIDC_OP_USER_ENDPOINT = os.getenv('OIDC_OP_USER_ENDPOINT')
# CILogon scopes (default: openid email profile org.cilogon.userinfo)
OIDC_RP_SCOPES = os.getenv('OIDC_RP_SCOPES')
# username algorithm
OIDC_USERNAME_ALGO = 'portal.apps.users.oidc_users.generate_username'
# SameSite prevents the browser from sending this cookie along with cross-site requests
# Safari seems to need this set to None
SESSION_COOKIE_SAMESITE = None
# SessionRefresh expiry
OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = int(os.getenv('OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS'))

OIDC_DRF_AUTH_BACKEND = 'mozilla_django_oidc.auth.OIDCAuthenticationBackend'

# AERPAW Email for development (use only 1 email backend at a time)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# AERPAW Email for production (use only 1 email backend at a time)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST')
# EMAIL_PORT = os.getenv('EMAIL_PORT')
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
# EMAIL_ADMIN_USER = os.getenv('EMAIL_ADMIN_USER')
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False

# Default Django logging is WARNINGS+ to console
# so visible via docker-compose logs django
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'mozilla_django_oidc': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
    },
}

# Auth user model (custom user account)
AUTH_USER_MODEL = 'users.AerpawUser'

# Django running behind Nginx reverse proxy
USE_X_FORWARDED_HOST = True
