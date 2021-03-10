from .base import *

DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1', '.ngrok.io', 'localhost']

INSTALLED_APPS += ['debug_toolbar']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'asfour',
        'USER': 'samer',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_URL = 'static/'