from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from asfour.storage_backends import PrivateMediaStorage
from twilio.rest import Client

class Organization(models.Model):

    name = models.CharField(max_length=255)
    twilio_api_key = models.CharField(
        max_length=255, blank=True)
    twilio_secret = models.CharField(
        max_length=255, blank=True)
    phone = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.name

    def get_credentials(self):
        return self.twilio_api_key, \
            self.twilio_secret, self.phone

class UserProfile(models.Model):

    user = models.OneToOneField(User, 
        on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name()

class Contact(models.Model):
    SMS = 'sms'
    VOICE = 'voice'
    EMAIL = 'email'
    WHATSAPP = 'whatsapp'
    MEDIUM_CHOICES = (
        (SMS, 'SMS'),
        (VOICE, 'Voice'),
        (EMAIL, 'Email'),
        (WHATSAPP, 'WhatsApp'),
    )
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=255, blank=True)
    preferred_method = models.CharField(max_length=30, 
        choices=MEDIUM_CHOICES, default=SMS)
    has_consented = models.BooleanField(default=False)
    has_whatsapp = models.BooleanField(default=False)

    def __str__(self):
        return '{0} {1}'.format(
            self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('contact-detail', 
            kwargs={'pk':self.id})
    # def get_absolute_url(self):
    #     return reverse('contact-list') + '
    # ?project={0}'.format(getattr(self.project, 'id', ''))

class Message(models.Model):

    body = models.CharField(max_length=255)
    attachment = models.FileField(
        storage=PrivateMediaStorage(), 
        upload_to='files/', blank=True, null=True)
    contacts = models.ManyToManyField(Contact, blank=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.body

    def get_absolute_url(self):
        return reverse('message-detail', 
            kwargs={'pk':self.id})

    def send(self):
        account_sid, auth_token, phone = self.organization \
        .get_credentials()
        client = Client(account_sid, auth_token)
        kwargs = {'body':self.body,'from_':phone,}
        if self.attachment:
            kwargs['media_url'] = [self.attachment.url]
        for contact in self.contacts.all():
            kwargs['to'] = contact.phone
            message = client.messages.create(**kwargs)
        return True

class Response(models.Model):

    contact = models.ForeignKey(Contact, 
        on_delete=models.SET_NULL, blank=True, null=True)
    body = models.TextField(blank=True)
    call_sid = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.body



