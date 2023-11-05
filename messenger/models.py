import datetime
import re

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from asfour.storage_backends import PrivateMediaStorage
from asfour.storage_backends import PublicMediaStorage

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Dial

from .functions import send_email
from .tasks import task_send_email, send_messages

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

    def get_reply_msg(self, response):
        for reply in self.autoreply_set.all():
            if response.body.lower() == reply.text.lower():
                reply.add_tags(response.contact)
                return reply.reply
        if response.contact:
            if not response.contact.has_email:
                return "Thank you for subscribing. Please reply with your email address or STOP to unsubscribe"
        return self.response_msg
    
    def transfer(self):
        btb = Organization.objects.get(id=4)
        wrong_list = Tag.objects.get(id=279)
        btb_transfers = Tag.objects.get(id=280)
        contacts = self.contact_set.filter(tags=wrong_list)
        counter = 0
        for contact in contacts:
            contact.tags.remove(wrong_list)
            contact.tags.add(btb_transfers)
            contact.organization = btb
            contact.save()
            counter += 1
        return '{} contacts transfered'.format(counter)
            

class UserProfile(models.Model):

    user = models.OneToOneField(User, 
        on_delete=models.CASCADE)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, blank=True)
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
    is_international = models.BooleanField(default=False)
    is_unsubscribed = models.BooleanField(default=False)
    has_name = models.BooleanField(default=False)
    has_email = models.BooleanField(default=False)

    class Meta:
        ordering = ('first_name',)

    def __str__(self):
        return '{0} {1}'.format(
            self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        if '+' not in self.phone:
            if not self.is_international:
                self.phone = '1' + self.phone
            self.phone = '+' + self.phone
        super(Contact, self).save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     tag = None
    #     if not self.id:
    #         tag, created = Tag.objects.get_or_create(
    #             name='All Contacts',
    #             organization=self.organization
    #         )
    #     if '+' not in self.phone:
    #         self.phone = '+1' + self.phone
    #     super(Contact, self).save(*args, **kwargs)
    #     if tag:
    #         self.tags.add(tag)
    #         super(Contact, self).save(*args, **kwargs)

    def send_sms(self, body):
        account_sid, auth_token, phone = self.organization \
        .get_credentials()
        client = Client(account_sid, auth_token)
        try:
            msg = client.messages.create(
                to=self.phone,
                from_=phone,
                body=body,
                status_callback='{}{}'.format(
                    'https://www.3asfour.com',
                    reverse('status-callback', kwargs={
                        'pk':self.organization.id
                    }),
                )
            )
            sid = getattr(msg, 'sid', None)
            error = ''
        except Exception as e:
            sid = ''
            error = e
        log = MessageLog.objects.create(
            organization=self.organization,
            text=body,
            contact=self,
            sid=sid,
            error=error,
        )
        return True

    def get_absolute_url(self):
        return reverse('contact-detail', 
            kwargs={'pk':self.id})

    def get_delete_url(self):
        return reverse('contact-delete',
            kwargs={'pk':self.id})

    def get_full_name(self):
        return '{0} {1}'.format(
            self.first_name, self.last_name)

    def extract_email(self, input_string):
        print('EXTRACING {}'.format(input_string))
        input_string = input_string.strip()
        email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        potential_emails = re.findall(email_regex, input_string)
        if potential_emails:
            return potential_emails[0]
        else:
            return None

    def add_email(self, email_input):
        print('EXTRACTING EMAIL')
        email = self.extract_email(email_input)
        print('EMAIL CLEANED: {}'.format(email))
        if email:
            self.email = email
            self.has_email = True
            self.save()

    # def get_absolute_url(self):
    #     return reverse('contact-list') + '
    # ?project={0}'.format(getattr(self.project, 'id', ''))

class Message(models.Model):
    SMS = 'sms'
    VOICE = 'voice'
    EMAIL = 'email'
    WHATSAPP = 'whatsapp'
    MIXED = 'mixed'
    CONFERENCE = 'conference'
    MEDIUM_CHOICES = (
        (SMS, 'SMS'),
        (VOICE, 'Voice'),
        (EMAIL, 'Email'),
        (WHATSAPP, 'WhatsApp'),
        (CONFERENCE, 'Conference Call'),
        (MIXED, 'Mixed'),
    )
    name = models.CharField(max_length=255, blank=True)
    body = models.TextField()
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
    created_by = models.ForeignKey(UserProfile, 
        on_delete=models.SET_NULL, blank=True, null=True)
    date_created = models.DateField(auto_now_add=True)
    date_sent = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.body

    def get_absolute_url(self):
        return reverse('message-detail', 
            kwargs={'pk':self.id})

    def get_delete_url(self):
        return reverse('message-delete',
            kwargs={'pk':self.id})

    def next(self):
        messages = Message.objects.filter(
            organization=self.organization,
            id__gt=self.id, 
            date_sent__isnull=False).order_by('date_sent')
        if messages:
            return messages[0]
        return None

    def send(self, request=None):
        kwargs = {'msg_id': self.id,}
        print('sending msg')
        # if request:
        #     if hasattr(request.user, 'userprofile'):
        #         kwargs['user_profile'] = \
        #         request.user.userprofile
        if self.method == 'voice':
            print('sending voice msg')
            kwargs['voice_uri'] = self.get_voice_uri(request)
        send_messages.delay(**kwargs)
        # self.log_message(contact, request, error)
        self.date_sent = datetime.datetime.now()
        self.save()
        return True

    def get_kwargs(self, phone, voice_uri):
        kwargs = {
            'status_callback': '{}{}'.format(
                'https://www.3asfour.com',
                reverse('status-callback', kwargs={
                    'pk':self.organization.id
                }),
            )
        }
        if self.method == self.WHATSAPP:
           kwargs['from_'] = 'whatsapp:{}'.format(phone)
        else:
            kwargs['from_'] = phone
        if voice_uri:
            kwargs['url'] = voice_uri
        else:
            kwargs['body'] = self.body
            if self.attachment:
                kwargs['media_url'] = [self.attachment.url]
        return kwargs

    def get_voice_uri(self, request):
        return request.build_absolute_uri(
            reverse('voice-call', kwargs={
                'pk': self.organization.id,
                'msg_id': self.id
            })
        )

    def get_client_verb(self):
        if self.method in (self.SMS, self.WHATSAPP):
            verb = 'messages'
        else:
            verb = 'calls'
        return verb

    def log_message(self, contact, request=None, error=None):
        log = MessageLog.objects.create(
            message=self,
            organization=self.organization,
            contact=contact,
        )
        if request:
            log.sender = request.user.userprofile
        if error:
            log.status = MessageLog.FAILED
            log.error = error
        log.save()
        return log

    def get_segments(self):
        chars = len(self.body)
        return -(-chars // 160)

    def get_delivery_window(self):
        segs = self.get_segments()
        contacts = self.contacts.count()
        return round(segs * contacts / 180)

    def get_moderator(self):
        if self.created_by:
            return self.created_by.phone
        elif self.organization.forward_phone:
            return self.organization.forward_phone
        else:
            return '+14154938715'

    def conference_call(self):
        response = VoiceResponse()
        account_sid, auth_token, phone = \
            self.organization.get_credentials()
        client = Client(account_sid, auth_token)
        call = client.calls.create(from_="client:"+phone, 
            to="client:"+self.get_moderator(),
            url='https://www.3asfour.com/{}'.format(
                reverse('conference-call', 
                    kwargs={'session_id':str(self.name)})
            ),
            status_callback_event=['completed'],
        )
        # with Dial() as dial:
        #     if request.POST.get('From') == self.get_moderator():
        #         dial.conference(self.name,
        #             start_conference_on_enter=True,
        #             end_conference_on_exit=False,
        #             record='record-from-start',
        #         )
        #     else:
        #         dial.conference(self.name, 
        #             start_conference_on_enter=False)
        # response.append(dial)
        
        for contact in self.contacts.all():
            client.conferences(self.name).participants.create(
                from_=phone, to=contact.phone)
        return True


class MessageLog(models.Model):
    SUCCESS = 'success'
    FAILED = 'failed'
    STATUS_CHOICES = (
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
    )
    sid = models.CharField(max_length=255, blank=True)
    message = models.ForeignKey(Message, 
        on_delete=models.CASCADE, blank=True, null=True)
    text = models.TextField(blank=True)
    status = models.CharField(max_length=40, 
        choices=STATUS_CHOICES, default=SUCCESS)
    twilio_status = models.CharField(max_length=200, 
        blank=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, 
        on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(UserProfile,
        on_delete=models.SET_NULL, blank=True, null=True)
    error = models.TextField(blank=True)
    async_task_id = models.CharField(max_length=255, 
        default = '')
    is_finished = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return '{0} sent to {1} on {2}'.format(
            self.text,
            self.contact.get_full_name(),
            self.date
        )

    def save(self, *args, **kwargs):
        if self.message and not self.text:
            self.text = self.message.body
        super(MessageLog, self).save(*args, **kwargs)

    def get_status(self):
        if self.twilio_status:
            return self.twilio_status.title()
        else:
            return self.get_status_display()

class Autoreply(models.Model):

    organization = models.ForeignKey(Organization, 
        on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    reply = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, blank=True)
    prev_msg = models.ManyToManyField(Message, blank=True)

    class Meta:
        verbose_name_plural = 'autoreplies'

    def __str__(self):
        return self.reply

    def get_absolute_url(self):
        return reverse('autoreply-update', 
            kwargs={'pk':self.id})

    def add_tags(self, contact):
        if contact:
            for tag in self.tags.all():
                contact.tags.add(tag)
            contact.save()

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

    class Meta:
        ordering = ('-date_received',)

    def __str__(self):
        return self.body

    def add_contact(self):
        if 'whatsapp' in self.phone:
            self.phone = self.phone.split(':')[1]
        contact, created = Contact.objects.get_or_create(
            phone=self.phone, organization=self.organization)
        if not created:
            if not contact.has_email:
                contact.add_email(self.body)
        self.contact = contact
        self.save()

    def get_most_recent_message(self):
        messages = Message.objects.filter(
            organization=self.organization,
            date_sent__lte=self.date_received).order_by(
            '-date_sent')
        if messages:
            return messages[0]
        return None

    def forward_sms(self):
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

    def forward_voice(self):
        if self.organization.forward_phone:
            account_sid, auth_token, phone = \
            self.organization.get_credentials()
            client = Client(account_sid, auth_token)
            kwargs = {
                'body':'voice msg from {}: {}'.format(
                    self.phone, self.recording),
                'from_':self.organization.phone,
                'to': self.organization.forward_phone,
            }
            try:
                message = client.messages.create(**kwargs)
                result = True
            except Exception as error:
                print(error)
        if self.organization.forward_email:
            task_send_email.delay(
                to=self.organization.forward_email,
                subject='Incoming Voice Msg',
                content='<p>{}</p>'.format(self.recording)
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



