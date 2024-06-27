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
def message_log(MessageLog, message, contact, user_profile, 
    sid, error):
    log = MessageLog.objects.create(
        message=message,
        organization=message.organization,
        contact=contact,
        sid=sid,
        error=error
    )
    if user_profile:
        log.sender = user_profile
    if error:
        log.status = MessageLog.FAILED
        log.error = error
    return log


@app.task
def send_messages(msg_id, voice_uri=None, user_profile=None):
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
            kwargs['to'] = get_recipient(message, contact)
            msg = client_action.create(**kwargs)
            sid = getattr(msg, 'sid', None)
            error = ""
            print('sent!')
        except Exception as e:
            sid = ""
            error = e
            print(error)
        log = message_log(MessageLog, message, contact, 
            user_profile, sid, error)
        log.save()

def get_recipient(message, contact):
    if message.method == message.WHATSAPP:
        return 'whatsapp:{}'.format(contact.phone)
    else:
        return contact.phone
