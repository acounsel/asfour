from __future__ import absolute_import, unicode_literals
import celery 
from celery import shared_task, current_task
from celery.utils.log import get_task_logger
import time
from builtins import range
from messenger import functions
from messenger import models
from django.contrib import messages

app = celery.Celery('messenger')
logger = get_task_logger(__name__)

@app.task
def task_send_message(to, subject, content):
    logger.info("task kicked off")
    #allows for the front end to load before displaying stuff
    time.sleep(1.5)
    functions.send_email(to, subject, content, current_task)
    return 'done'
