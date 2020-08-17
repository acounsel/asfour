from __future__ import absolute_import, unicode_literals
import time
import os
from messenger import functions
from asfour.celery import app
from django.contrib import messages

@app.task
def task_send_email(to, subject, content):
    #allows for the front end to load before displaying stuff
    time.sleep(1)
    functions.send_email(to, subject, content)
    return 'done'

@app.task
def task_send_message(self, request, **kwargs):
     #allows for the front end to load before displaying stuff
    time.sleep(1)
    functions.send_message(self, request, **kwargs)
    return 'done'
