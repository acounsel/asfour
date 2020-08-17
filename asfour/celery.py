import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asfour.settings')

app = Celery('asfour')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


