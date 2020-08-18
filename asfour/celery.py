import os

from django.conf import settings

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asfour.settings')

# app = Celery('asfour', broker='redis://h:p19584989c8086e8237012d0c3abe04936c9ea82f28d985eb1699f1e8551de546@ec2-52-200-217-67.compute-1.amazonaws.com:18389')
app = Celery('asfour', broker='redis://localhost:6379/0')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


