from .base import *

DEBUG = False

ALLOWED_HOSTS = ['.3asfour.com', 
    'asfour.herokuapp.com']

STATIC_URL = 'https://{0}/{1}/'.format(
    AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': 'unix:/home/acounsel/memcached.sock',
#     }
# }

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch5_backend.Elasticsearch5SearchEngine',
#         'URL': 'http://127.0.0.1:27770/',
#         'INDEX_NAME': 'haystack',
#         'TIMEOUT': 120,
#     },
# }
