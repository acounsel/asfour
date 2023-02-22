import csv
import datetime
import io
import re

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator

from celery.result import AsyncResult
from .decorators import validate_twilio_request
from .forms import OrganizationForm, MessageForm
from .functions import send_email
from .models import (Autoreply, Contact, Message, MessageLog, 
    Note, Organization, Response, Tag, UserProfile)
from .tasks import send_messages

from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse


decorators = [
    csrf_exempt, require_POST, validate_twilio_request
]

class Echo:
    """An object that implements just the write method
    of the file-like interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of
        storing in a buffer.
        """
        return value

class LoginRequiredMixin(LoginRequiredMixin):

    def get_profile(self):
        return self.request.user.userprofile

    def get_org(self):
        return self.get_profile().organization

    def get_queryset(self):
        queryset = super().get_queryset()
        organization = self.get_org()
        return queryset.filter(organization=organization)

    def form_valid(self, form):
        form.instance.organization = self.get_org()
        messages.success(
            self.request,
            '{} Created'.format(
                form.instance._meta.verbose_name.title()
            )
        )
        return super().form_valid(form)

class AdminMixin(UserPassesTestMixin):
    login_url = '/login/'

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user.userprofile.is_admin
        else:
            return False

class NoteMixin:

    def post(self, request, **kwargs):
        userprofile = request.user.userprofile
        note = Note.objects.create(
            body = request.POST.get('note'),
            organization = userprofile.organization,
            author = userprofile,
        )
        field = self.model._meta.verbose_name
        value = self.get_object()
        setattr(note, field, value)
        note.save()
        messages.success(request, 'Note Added!')
        return redirect(value.get_absolute_url())

class Home(View):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = {
            'captcha_key': settings.RECAPTCHA_API_KEY,
        }
        if hasattr(self.request.user, 'userprofile'):
            org = self.request.user.userprofile.organization
            kwargs = {'organization': org,}
            context.update({
                'contact_list': Contact.objects.filter(
                    **kwargs),
                'message_list': Message.objects.filter(
                    **kwargs),
                'response_list': Response.objects.filter(
                    **kwargs),
            })
        return context

    def get(self, request, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        context = self.get_context_data()
        email = send_email(
            to='sarrabi@gmail.com',
            subject='Account Requested',
            content='{0} ({1}): {2}'.format(
                request.POST.get('name'),
                request.POST.get('email'),
                request.POST.get('body')
            )
        )
        messages.success(request, 
            'Request Received, Thank You!')
        return render(request, self.template_name, context)

class OrgListView(LoginRequiredMixin, ListView):
    pass
    

class OrgDetailView(LoginRequiredMixin, 
    NoteMixin, DetailView):
    pass

class OrgDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'messenger/confirm_delete.html'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Succesfully Deleted')
        return super().delete(request, *args, **kwargs)

class OrgCreateView(LoginRequiredMixin, CreateView):
    pass

class OrgUpdateView(LoginRequiredMixin, UpdateView):
    pass

class TagView(View):
    model = Tag
    fields = ('name',)
    success_url = reverse_lazy('tag-list')

class TagList(TagView, OrgListView):
    pass

class TagDetail(TagView, OrgDetailView):
    pass

class TagCreate(TagView, OrgCreateView):
    pass

class TagUpdate(TagView, OrgUpdateView):
    pass

class TagDelete(TagView, OrgDeleteView):
    pass

class ContactView(View):
    model = Contact
    fields = ('first_name', 'last_name', 'phone', 'email',
        'preferred_method', 'tags', 'has_whatsapp')
    success_url = reverse_lazy('contact-list')
    paginate_by = 500

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        org = self.request.user.userprofile.organization
        form.fields['tags'].queryset = Tag.objects.filter(
            organization=org)
        return form

class ContactList(ContactView, OrgListView):
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('tags', 
            'response_set', 'messagelog_set')

class ContactDetail(ContactView, OrgDetailView):
    
    def post(self, request, **kwargs):
        contact = self.get_object()
        if request.POST.get('body'):
            contact.send_sms(request.POST.get('body'))
            messages.success(request, 
                'Message Sent.')
        return redirect(reverse(
            'contact-detail', kwargs={'pk':contact.id}
        ))

class ContactCreate(ContactView, OrgCreateView):
    pass

class ContactUpdate(ContactView, OrgUpdateView):
    pass

class ContactDelete(ContactView, OrgDeleteView):
    pass

class ContactImport(ContactList):
    template_name = 'messenger/contact_import.html'

    def post(self, request, **kwargs):
        organization = request.user.userprofile.organization
        try:
            import_file = request.FILES['csv_file']
        except KeyError:
            messages.error(request, 'Please upload a file.')
        else:
            errors = self.import_csv_data(import_file, 
                organization=organization)
            print(errors)
            messages.success(request, 
                'Contacts successfully uploaded.')
        return redirect(reverse('home'))

    def import_csv_data(self, import_file, organization):
        errors = []
        try:
            # with open(import_file, 'rt', encoding="utf-8",
            # errors='ignore') as csvfile:
            reader = csv.DictReader(
                io.StringIO(
                    import_file.read().decode('utf-8')
                )
            )
        except Exception as error:
            errors.append(error)
            messages.error(self.request, \
                'Failed to read file. Please make sure \
                the file is in CSV format.')
        else:
            errors = self.enumerate_rows(reader, organization)
        return errors

    # Loop through CSV, skipping header row.
    def enumerate_rows(self, reader, org, start=1):
        row_errors = []
        # Index is for row numbers in error message-s.
        for index, contact in enumerate(reader, start=1):
            row_errors = []
            try:
                self.import_contact_row(contact, org)
            except Exception as error:
                print(error)
                row_errors.append('Row {0}: {1}'.format(
                    index, error))
        return row_errors

    def import_contact_row(self, contact_dict, org):
        print(contact_dict)
        phone = re.sub("[^0-9]", "", contact_dict['phone'])
        if '+' not in phone:
            phone = '+1' + phone
        print('adding {}'.format(phone))  
        contact, created = Contact.objects.get_or_create(
            phone=phone,
            organization=org)
        print(contact, created)
        contact.first_name = contact_dict['first_name']
        contact.last_name = contact_dict['last_name']
        contact.email = contact_dict['email']
        for tagname in ('tag1', 'tag2', 'tag3'):
            if contact_dict.get(tagname):
                tag, created = Tag.objects.get_or_create(
                    name=contact_dict[tagname],
                    organization=org)
                contact.tags.add(tag)
        contact.save()
        return contact

class MessageView(View):
    model = Message
    form_class = MessageForm

    # def get_form(self, *args, **kwargs):
    #     form = super().get_form(*args, **kwargs)
    #     org = self.request.user.userprofile.organization
    #     form.fields['tags'].queryset = Tag.objects.filter(
    #         organization=org)
    #     form.fields['contacts'].queryset = Contact.objects \
    #     .filter(organization=org)
    #     return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_all_bool'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(MessageView, self).get_form_kwargs()
        kwargs['user_profile'] = self.request.user.userprofile
        return kwargs   

    def form_valid(self, form):
        print(self.request.POST)
        response = super().form_valid(form)
        contacts = Contact.objects.filter(
            tags__in=self.object.tags.all()).distinct()
        for contact in contacts:
            self.object.contacts.add(contact)
        if self.request.POST.get('add_all'):
            org = self.request.user.userprofile.organization
            contacts = org.contact_set.all()
            self.object.contacts.set(contacts)
        # for contact in contacts:
        #     if contact not in self.object.contacts.all():
        #         self.object.contacts.add(contact)
        self.object.save()
        return response

class MessageList(MessageView, OrgListView):
   
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('contacts')

class MessageDetail(MessageView, OrgDetailView):
    
    def get_context_data(self, **kwargs):
        message = self.get_object()
        context = super().get_context_data(**kwargs)
        context['form'] = MessageForm(
            instance=message, 
            user_profile=self.request.user.userprofile)
        context['form_action'] = reverse('message-update',
            kwargs={'pk':message.id})
        context['contacts'] = self.get_contacts(
            message=message)
        context['responses'] = self.get_responses(
            message=message)
        return context

    def get_contacts(self, message):
        contacts = message.contacts.prefetch_related(
            'messagelog_set', 'tags')
        contact_list = []
        messagelogs = MessageLog.objects.filter(
            message=message).values_list('contact', flat=True)
        for contact in contacts:
            if contact.id in messagelogs:
                status = 'Sent'
            else:
                status = 'Unsent'
            contact_list.append({
                'url': contact.get_absolute_url(),
                'first_name': contact.first_name,
                'last_name': contact.last_name,
                'phone': contact.phone,
                'tags': ', '.join(
                    tag.name for tag in contact.tags.all()),
                'status': status,
            })
        return contact_list

    def get_responses(self, message):
        if message.date_sent:
            rdict = {
                'contact__in': message.contacts.all(),
                'date_received__gt': message.date_sent,
            }
            next_msg = message.next()
            if next_msg:
                rdict['date_received__lte'] = next_msg.date_sent
            responses = Response.objects.filter(
                **rdict).select_related('contact').distinct()
            return responses
        return None

class MessageCreate(MessageView, OrgCreateView):
    pass

class MessageUpdate(MessageView, OrgUpdateView):
    pass

class MessageDelete(MessageView, OrgDeleteView):
    success_url = reverse_lazy('message-list')

class MessageSend(MessageDetail):

    def get(self, request, **kwargs):
        response = super().get(request, **kwargs)
        context = self.get_context_data(**kwargs)
        message = self.get_object()
        message.send(request)
        messages.success(request, 'Message Sent!')
        return redirect(message.get_absolute_url())

class MessageLogList(OrgListView):
    model = MessageLog
    paginate_by = 500

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'message', 'contact', 'sender')

class ResponseView(View):
    model = Response

class ResponseList(ResponseView, OrgListView):
    paginate_by = 500

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('contact')

class ResponseExport(ResponseList):

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get('msg_id'):
            message = Message.objects.get(
                id=self.request.GET.get('msg_id'))
            queryset = queryset.filter(
                date_received__gt=message.date_sent)
            if message.next():
                next_msg = message.next()
                queryset = queryset.filter(
                    date_received__lte=next_msg.date_sent)
        return queryset

    def get(self, request, **kwargs):
        resp = super().get(request, **kwargs)
        rows = self.get_response_list(self.get_queryset())
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in rows),
            content_type="text/csv")
        today = datetime.date.today()
        filename = 'asfour_responses_{}'.format(today)
        cont_disp = 'attachment;filename="{}.csv"'.format(
            filename)
        response['Content-Disposition'] = cont_disp
        return response

    def get_response_list(self, queryset):
        header = ['phone', 'first_name', 'last_name', 'tags',
        'response', 'method', 'recording', 'date_received',
        'last_message_received']
        rows = [header,]
        for response in queryset:
            print('getting row')
            rows.append(self.get_response_row(response))
        return rows

    def get_response_row(self, response):
        first_name, last_name, tags = None, None, None
        if response.contact:
            first_name = response.contact.first_name
            last_name = response.contact.last_name
            if response.contact.tags.count():
                tags = '; '.join([tag.name for tag in \
                response.contact.tags.all()]),
        row = [
            response.phone,
            first_name,
            last_name,
            tags,
            response.body,
            response.get_method_display(),
            getattr(response.recording, 'url', None),
            response.date_received,
            response.get_most_recent_message()
        ]
        return row

class AutoreplyView(View):
    model = Autoreply
    fields = ('text', 'reply', 'tags')
    success_url = reverse_lazy('autoreply-list')

class AutoreplyCreate(AutoreplyView, OrgCreateView):
    pass

class AutoreplyUpdate(AutoreplyView, OrgUpdateView):
    pass

class AutoreplyList(AutoreplyView, OrgListView):
    pass

@method_decorator(decorators, name='dispatch')
class VoiceCall(View):
    model = Message

    def get_twiml(self):
        message = Message.objects.get(
            id=self.kwargs.get('msg_id'))
        twiml_response = VoiceResponse()
        twiml_response.play(message.recording.url)
        if message.request_for_response:
            print('REQUEST FOR RESPONSE ACTIVATED')
            twiml_response.record(
                action=reverse('record-call', kwargs={
                    'pk': message.organization.id,
                    'msg_id': message.id
                    }),
                method='POST',
                max_length=10,
                timeout=4,
                # transcribe=True,
                # transcribe_callback=action
            )
            # twiml_response.say('Thank you, goodbye')
        
        return twiml_response

    def post(self, request, **kwargs):
        print('its a post!')
        return HttpResponse(
            self.get_twiml(),
            content_type='application/xml'
        )

@method_decorator(decorators, name='dispatch')
class RecordCall(View):

    def post(self, request, **kwargs):
        message = Message.objects.get(
            id=self.kwargs.get('msg_id'))
        session_id = request.POST['CallSid']
        request_body = request.POST.get('RecordingUrl')
        phone_number = request.POST.get('To')
        response = Response.objects.create(
            method=Response.VOICE,
            phone=phone_number,
            recording=request.POST.get('RecordingUrl'),
            sid=session_id,
            organization=message.organization,
        )
        response.add_contact()
        if 'TranscriptionText' in request.POST:
            response.body = request.POST.get(
                'TranscriptionText')
            response.save()
        twiml_response = VoiceResponse()
        # twiml_response.say('Thank you, goodbye')
        # twiml_response.hangup()
        # return HttpResponse(
        #     twiml_response,
        #     content_type='application/xml'
        # )
        twiml_response.redirect(
            reverse(
                'voice-call', kwargs={
                    'pk': message.organization.id,
                    'msg_id': message.id
                }
            ), method='POST')
        return HttpResponse(
            twiml_response,
            content_type='application/xml'
        )

@method_decorator(decorators, name='dispatch')
class StatusCallback(View):
    
    def post(self, request, **kwargs):
        print('STATUS CALLBACK TRIGGERED')
        resp = 200
        org = Organization.objects.get(
            id=self.kwargs.get('pk'))
        try:
            callback = self.get_callback_dict(request)
            log = MessageLog.objects.filter(
                sid=callback['MessageSid'],
                contact__phone=callback['To']
            )
            if log:
                log[0].twilio_status = callback['MessageStatus']
                log[0].save()
        except:
            print('STATUS UPDATE FAILED')
            resp = 400
        print(request.POST)
        print(self.kwargs)
        return HttpResponse(resp)

    def get_callback_dict(self, request):
        callback_dict = {}
        for key in ('From','MessageSid','MessageStatus','To'):
            callback_dict[key] = request.POST.get(key)
        return callback_dict

@method_decorator(decorators, name='dispatch')
class HarvestResponse(View):

    def post(self, request, **kwargs):
        resp = 200
        org = Organization.objects.get(
            id=self.kwargs.get('pk'))
        resp_kwargs, save = self.get_response_kwargs(
            request, org)
        if save:
            response = Response.objects.create(**resp_kwargs)
            response.add_contact()
            if self.kwargs.get('medium') == 'message':
                resp = self.sms_forward_and_respond(
                    org, response)
        if self.kwargs.get('medium') == 'voice':
            if request.POST.get('CallStatus') == 'completed':
                response.forward_voice()
            else:
                resp = self.voice_forward_and_log(org)
        return HttpResponse(resp)

    def get_response_kwargs(self, request, organization):
        save = False
        medium = self.kwargs.get('medium')
        kwargs = {
            'organization': organization,
            'phone': request.POST.get('From'),
        }
        if medium == 'message':
            kwargs['sid'] = request.POST.get('MessageSid')
            kwargs['body'] = request.POST.get('Body', '')
            save = True
        elif medium == 'voice':
            if request.POST.get('CallStatus') == 'completed':
                save = True
            # if 'ringing' in request.POST.get('CallStatus'):
            #     return False
            kwargs['sid'] = request.POST.get('CallSid')
            kwargs['recording'] = request.POST.get(
                'RecordingUrl', '')
        return kwargs, save

    def sms_forward_and_respond(self, org, response):
        response.forward_sms()
        resp = MessagingResponse()
        resp.message(org.get_reply_msg(response))
        return str(resp)

    def voice_forward_and_log(self, org):
        resp = VoiceResponse()
        resp.say('Please leave a message after the tone, \
            then press the pound key.', 
            voice='alice')  
        resp.record()  
        resp.say('Thank you for your message. Goodbye.', 
            voice='alice')  
        resp.hangup()
        return str(resp)

class OrganizationUpdate(AdminMixin, SuccessMessageMixin, 
    UpdateView):
    model = Organization
    form_class = OrganizationForm
    success_message = 'Organization Updated!'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user.userprofile.organization

class UserUpdate(SuccessMessageMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email')
    success_message = 'User Updated!'
    success_url = reverse_lazy('home')
    template_name = 'messenger/user_form.html'

    def get_object(self):
        return self.request.user
