import django_heroku
import os

from django.core.exceptions import ImproperlyConfigured
#from .local_settings import BROKER_URL

def get_env_variable(var_name):
    """Get the environment variable or return exception.""" 
    try:
        return os.environ[var_name] 
    except KeyError:
        error_msg = 'Set the {} environment 􏰁\
            variable'.format(var_name)
    raise ImproperlyConfigured(error_msg)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'django_extensions',
    'crispy_forms',
    'messenger',
    'django_celery_beat',
    'django_celery_results',
    'debug_toolbar',
]

DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '.3asfour.com']

INTERNAL_IPS = ['127.0.0.1', 'localhost']

ADMINS = (
    ('Samer', 'samer@accountabilitycounsel.org'),
    ('Marisa', 'marisa@accountabilitycounsel.org')
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#CELERY_BROKER_URL = BROKER_URL
#CELERY_TIMEZONE = 'UTC'
#CELERY_ENABLE_UTC = True
# CELERY_RESULT_BACKEND = 'django-db'
#CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
#CELERY_IMPORTS = ('messenger.tasks')
# CELERY_RESULT_BACKEND = 'django-db'

TEMPLATEDIRS = ['templates', '/templates']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'asfour.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATEDIRS,
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

WSGI_APPLICATION = 'asfour.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases




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

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": os.environ.get('REDIS_URL'),
    }
}


CRISPY_TEMPLATE_PACK = 'bootstrap4'


try:
    from .local_settings import *
except Exception as e:
    print('getting environ vars')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('S3_BUCKET')
    AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)
    AWS_PUBLIC_MEDIA_LOCATION = 'media/public'
    DEFAULT_FILE_STORAGE = 'zwazo.storage_backends.PublicMediaStorage'
    AWS_PRIVATE_MEDIA_LOCATION = 'media/private'
    PRIVATE_FILE_STORAGE = 'zwazo.storage_backends.PrivateMediaStorage'
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'apikey'
    EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
    EMAIL_USE_TLS = True
    RECAPTCHA_API_KEY = get_env_variable('RECAPTCHA_API_KEY')
    RECAPTCHA_SECRET_KEY = get_env_variable('RECAPTCHA_SECRET_KEY')
    SERVER_EMAIL = 'noreply@3asfour.com'
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True

# Activate Django-Heroku.
django_heroku.settings(locals())
