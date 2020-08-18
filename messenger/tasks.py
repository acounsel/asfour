from __future__ import absolute_import, unicode_literals
import time
import os

from django.apps import apps
from django.contrib import messages

from twilio.rest import Client

from asfour.celery import app

from . import functions

@app.task
def task_send_email(to, subject, content):
    #allows for the front end to load before displaying stuff
    time.sleep(1)
    functions.send_email(to, subject, content)
    return 'done'

@app.task
def task_send_message(request, **kwargs):
     #allows for the front end to load before displaying stuff
    time.sleep(1)
    functions.send_message(self, request, **kwargs)
    return 'done'

@app.task
def send_test_message(message):
     #allows for the front end to load before displaying stuff
    time.sleep(1)
    message.send()
    return 'done'

# @app.task
# def send_message(sid, token, from_phone, to_phone, message):
#     client = Client(sid, token)
#     client.messages.create(**{
#         'from_': from_phone,
#         'to': to_phone,
#         'body': message,
#     })
#     return 'done'

# @app.task
# def send_messages(numbers, sid, token, verb, send_dict):
#     MessageLog = apps.get_model(app_label='messenger', 
#         model_name='MessageLog')
#     for numbers in numbers:
#         try:
#             send_dict['to'] = number
#             send_message(sid, token, verb, send_dict)
#             error = None
#         except Exception as e:
#             error = e

@app.task
def send_messages(msg_id, voice_uri=None):
    Message = apps.get_model(app_label='messenger', 
        model_name='Message')
    MessageLog = apps.get_model(app_label='messenger', 
        model_name='MessageLog')
    message = Message.objects.get(id=msg_id)
    account_sid, auth_token, phone = message.organization \
        .get_credentials()
    client = Client(account_sid, auth_token)
    verb = message.get_client_verb()
    client_action = getattr(client, verb)
    kwargs = message.get_kwargs(phone, voice_uri)
    for contact in message.contacts.all():
        try:
            kwargs['to'] = contact.phone
            client_action.create(**kwargs)
            error = None
        except Exception as e:
            error = e
        MessageLog.objects.create(
            message=message,
            organization=message.organization,
            contact=contact)

