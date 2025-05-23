import django_heroku
import os

from django.core.exceptions import ImproperlyConfigured
from pathlib import Path
from urllib import parse

#from .local_settings import BROKER_URL

def get_env_variable(var_name):
    """Get the environment variable or return exception.""" 
    try:
        return os.environ[var_name] 
    except KeyError:
        error_msg = 'Set the {} environment 􏰁\
            variable'.format(var_name)
    raise ImproperlyConfigured(error_msg)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

AWS_ACCESS_KEY_ID = get_env_variable('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_env_variable('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = get_env_variable('S3_BUCKET')
AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(
    AWS_STORAGE_BUCKET_NAME)
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_PUBLIC_MEDIA_LOCATION = 'media/public'
AWS_PRIVATE_MEDIA_LOCATION = 'media/private'

MEDIA_ROOT = BASE_DIR / 'media'
STATIC_ROOT = BASE_DIR / 'static_root'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

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
    'crispy_bootstrap5',
    'messenger',
    'django_celery_beat',
    'django_celery_results',
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

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

REDIS_URL = os.environ.get('REDIS_URL')

if REDIS_URL:
    parsed_url = parse.urlparse(REDIS_URL)
    query = dict(parse.parse_qsl(parsed_url.query))
    query['ssl_cert_reqs'] = 'CERT_NONE'
    new_query = parse.urlencode(query)

    REDIS_URL = parse.urlunparse(parsed_url._replace(query=new_query))

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
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
DEFAULT_FROM_EMAIL = 'admin@3asfour.com'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

OPENAI_KEY = get_env_variable('OPENAI_KEY')

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
        "OPTIONS": {
            "SSL": {
                "ssl_cert_reqs": 'CERT_NONE',
            }
        }
    }
}


CRISPY_TEMPLATE_PACK = 'bootstrap4'



# Activate Django-Heroku.
django_heroku.settings(locals())
