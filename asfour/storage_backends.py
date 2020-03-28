import os

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    try:
        location = settings.AWS_LOCATION
    except:
        location = os.environ['AWS_LOCATION']

class PublicMediaStorage(S3Boto3Storage):
    try:
        location = settings.AWS_PUBLIC_MEDIA_LOCATION
    except:
        location = os.environ['AWS_PUBLIC_MEDIA_LOCATION']
    file_overwrite = False

class PrivateMediaStorage(S3Boto3Storage):
    try:
        location = settings.AWS_PRIVATE_MEDIA_LOCATION
    except:
        location = os.environ['AWS_PRIVATE_MEDIA_LOCATION']
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False