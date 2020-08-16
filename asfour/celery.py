import os

from celery import Celery


app = Celery('genome_app')

app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asfour.settings')

app = Celery('asfour')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


