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

class Tag(models.Model):

    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag-detail', 
            kwargs={'pk':self.id})

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
    address = models.CharField(max_length=255, blank=True)
    preferred_method = models.CharField(max_length=30, 
        choices=MEDIUM_CHOICES, default=SMS)
    tags = models.ManyToManyField(Tag, blank=True)
    has_consented = models.BooleanField(default=False)
    has_whatsapp = models.BooleanField(default=False)

    def __str__(self):
        return '{0} {1}'.format(
            self.first_name, self.last_name)

    def get_absolute_url(self):
        return reverse('contact-detail', 
            kwargs={'pk':self.id})

    def get_full_name(self):
        return '{0} {1}'.format(
            self.first_name, self.last_name)
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

    def send(self, request=None):
        account_sid, auth_token, phone = self.organization \
        .get_credentials()
        client = Client(account_sid, auth_token)
        kwargs = {'body':self.body,'from_':phone,}
        if self.attachment:
            kwargs['media_url'] = [self.attachment.url]
        for contact in self.contacts.all():
            kwargs['to'] = contact.phone
            message = client.messages.create(**kwargs)
            self.log_message(contact, request)
        return True

    def log_message(self, contact, request=None):
        log = MessageLog.objects.create(
            message=self,
            organization=self.organization,
            contact=contact,
        )
        if request:
            log.sender = request.user.userprofile
        log.save()

class MessageLog(models.Model):

    message = models.ForeignKey(Message, 
        on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, 
        on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(UserProfile,
        on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return '{0} sent to {1} on {2}'.format(
            self.message.body,
            self.contact.get_full_name(),
            self.date
        )

class Response(models.Model):

    contact = models.ForeignKey(Contact, 
        on_delete=models.SET_NULL, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True)
    body = models.TextField(blank=True)
    sid = models.CharField(max_length=255)
    date_received = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.body

    def find_contact(self):
        contact, created = Contact.objects.get_or_create(
            phone=self.phone, organization=self.organization)
        self.contact = contact
        self.save()

class Note(models.Model):

    body = models.TextField(blank=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, 
        on_delete=models.SET_NULL, blank=True, null=True)
    message = models.ForeignKey(Message, 
        on_delete=models.SET_NULL, blank=True, null=True)
    message_log = models.ForeignKey(MessageLog,
        on_delete=models.SET_NULL, blank=True, null=True)
    response = models.ForeignKey(Response,
        on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(UserProfile, 
        on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.body



