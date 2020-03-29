import os

from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def get_settings_value(name):
    try:
        value = getattr(settings, name)
    except:
        value = os.environ.get(name)
    return value

def send_email(to, subject, content):
    message = Mail(
        from_email='admin@asfour.com',
        to_emails=to,
        subject=subject,
        html_content=content)
    try:
        api_key = get_settings_value('SENDGRID_API_KEY')
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print('ERROR')
        print(e.message)