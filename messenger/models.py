from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from asfour.storage_backends import PrivateMediaStorage
from asfour.storage_backends import PublicMediaStorage
from twilio.rest import Client

from .functions import send_email

class Organization(models.Model):

    name = models.CharField(max_length=255)
    twilio_api_key = models.CharField(
        max_length=255, blank=True)
    twilio_secret = models.CharField(
        max_length=255, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    response_msg = models.CharField(max_length=255, 
        default='Thank you, your message has been received')
    forward_phone = models.CharField(
        max_length=40, blank=True)
    forward_email = models.CharField(
        max_length=255, blank=True)
    url = models.URLField(max_length=255, blank=True)

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
    is_admin = models.BooleanField(default=False)

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

    def get_delete_url(self):
        return reverse('tag-delete',
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

    def get_delete_url(self):
        return reverse('contact-delete',
            kwargs={'pk':self.id})

    def get_full_name(self):
        return '{0} {1}'.format(
            self.first_name, self.last_name)

    # def get_absolute_url(self):
    #     return reverse('contact-list') + '
    # ?project={0}'.format(getattr(self.project, 'id', ''))

class Message(models.Model):
    SMS = 'sms'
    VOICE = 'voice'
    EMAIL = 'email'
    WHATSAPP = 'whatsapp'
    MIXED = 'mixed'
    MEDIUM_CHOICES = (
        (SMS, 'SMS'),
        (VOICE, 'Voice'),
        (EMAIL, 'Email'),
        (WHATSAPP, 'WhatsApp'),
        (MIXED, 'Mixed'),
    )
    body = models.CharField(max_length=255)
    method = models.CharField(max_length=50, 
        choices=MEDIUM_CHOICES, default=SMS)
    attachment = models.FileField(
        storage=PrivateMediaStorage(), 
        upload_to='files/', blank=True, null=True)
    recording = models.FileField(
        storage=PublicMediaStorage(), 
        upload_to='files/', blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    contacts = models.ManyToManyField(Contact, blank=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE)
    request_for_response = models.BooleanField(default=False)

    def __str__(self):
        return self.body

    def get_absolute_url(self):
        return reverse('message-detail', 
            kwargs={'pk':self.id})

    def get_delete_url(self):
        return reverse('message-delete',
            kwargs={'pk':self.id})

    def send(self, request=None):
        account_sid, auth_token, phone = self.organization \
        .get_credentials()
        client = Client(account_sid, auth_token)
        kwargs = self.get_kwargs(phone, request)
        sender_client = self.get_client_verb(client)
        for contact in self.contacts.all():
            kwargs['to'] = contact.phone
            message = sender_client.create(**kwargs)
            self.log_message(contact, request)
        return True

    def get_kwargs(self, phone, request):
        kwargs = {'from_':phone,}
        if self.method == self.SMS:
            kwargs['body'] = self.body
            if self.attachment:
                kwargs['media_url'] = [self.attachment.url]
        else:
            kwargs['url'] = request.build_absolute_uri(
                reverse('voice-call', kwargs={
                    'pk': self.organization.id,
                    'msg_id': self.id
                })
            )
        return kwargs

    def get_client_verb(self, client):
        if self.method == self.SMS:
            verb = 'messages'
        else:
            verb = 'calls'
        return getattr(client, verb)

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

    method = models.CharField(max_length=50, 
        choices=MEDIUM_CHOICES, default=SMS)
    contact = models.ForeignKey(Contact, 
        on_delete=models.SET_NULL, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True)
    body = models.TextField(blank=True)
    recording = models.CharField(max_length=255, blank=True)
    sid = models.CharField(max_length=255, blank=True)
    date_received = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.body

    def add_contact(self):
        contact, created = Contact.objects.get_or_create(
            phone=self.phone, organization=self.organization)
        self.contact = contact
        self.save()

    def forward(self):
        result = False
        if self.organization.forward_phone:
            account_sid, auth_token, phone = \
            self.organization.get_credentials()
            client = Client(account_sid, auth_token)
            kwargs = {
                'body':'msg from {}: {}'.format(
                    self.phone, self.body),
                'from_':self.organization.phone,
                'to': self.organization.forward_phone,
            }
            try:
                message = client.messages.create(**kwargs)
                result = True
            except Exception as error:
                print(error)
        if self.organization.forward_email:
            send_email(
                to=self.organization.forward_email,
                subject='Incoming SMS',
                content='<p>{}</p>'.format(self.body)
            )
            result = True
        return result

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



