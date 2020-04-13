import csv
import io

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator

from .decorators import validate_twilio_request
from .functions import send_email
from .models import Organization, UserProfile, Contact, Tag
from .models import Message, MessageLog, Response, Note

from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse


decorators = [
    csrf_exempt, require_POST, validate_twilio_request
]

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
        if hasattr(self.request.user, 'userprofile'):
            org = self.request.user.userprofile.organization
            kwargs = {'organization': org,}
            context = {
                'contact_list': Contact.objects.filter(
                    **kwargs),
                'message_list': Message.objects.filter(
                    **kwargs),
                'respone_list': Response.objects.filter(
                    **kwargs),
            }
        else:
            context = {}
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

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        org = self.request.user.userprofile.organization
        form.fields['tags'].queryset = Tag.objects.filter(
            organization=org)
        return form

class ContactList(ContactView, OrgListView):
    pass

class ContactDetail(ContactView, OrgDetailView):
    pass

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
            contact.update({'organization': org})
            row_errors = []
            try:
                self.import_contact_row(contact)
            except Exception as error:
                row_errors.append('Row {0}: {1}'.format(
                    index, error))
        return row_errors

    def import_contact_row(self, contact_dict):
        contact = Contact.objects.get_or_create(
            **contact_dict)
        return contact

class MessageView(View):
    model = Message
    fields = ('method', 'body', 'attachment', 'recording', 
        'tags', 'contacts')
    success_url = reverse_lazy('message-list')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        org = self.request.user.userprofile.organization
        form.fields['tags'].queryset = Tag.objects.filter(
            organization=org)
        form.fields['contacts'].queryset = Contact.objects \
        .filter(organization=org)
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        contacts = Contact.objects.filter(
            tags__in=self.object.tags.all()).distinct()
        for contact in contacts:
            if contact not in self.object.contacts.all():
                self.object.contacts.add(contact)
        self.object.save()
        return response

class MessageList(MessageView, OrgListView):
    pass

class MessageDetail(MessageView, OrgDetailView):
    pass

class MessageCreate(MessageView, OrgCreateView):
    pass

class MessageUpdate(MessageView, OrgUpdateView):
    pass

class MessageDelete(MessageView, OrgDeleteView):
    pass

class MessageSend(MessageDetail):

    def get(self, request, **kwargs):
        response = super().get(request, **kwargs)
        context = self.get_context_data(**kwargs)
        message = self.get_object()
        message.send(request)
        messages.success(request, 'Message Sent!')
        return redirect(reverse('home'))

class MessageLogList(OrgListView):
    model = MessageLog

class ResponseView(View):
    model = Response

class ResponseList(ResponseView, OrgListView):
    pass

@method_decorator(decorators, name='dispatch')
class VoiceCall(View):
    model = Message

    def get_twiml(self):
        message = Message.objects.get(
            id=self.kwargs.get('msg_id'))
        twiml_response = VoiceResponse()
        twiml_response.play(message.recording.url)
        return twiml_response

    def get(self, request, **kwargs):
        print('its a get!')
        return HttpResponse(
            self.get_twiml(),
            content_type='application/xml'
        )

    def post(self, request, **kwargs):
        print('its a post!')
        return HttpResponse(
            self.get_twiml(),
            content_type='application/xml'
        )

@method_decorator(decorators, name='dispatch')
class HarvestResponse(View):

    def post(self, request, **kwargs):
        print(request.POST)
        body = request.POST.get('Body', None)
        sid = self.get_sid(request)
        organization = Organization.objects.get(
            id=self.kwargs.get('pk'))
        response = Response.objects.create(
            body=body,
            phone=request.POST.get('From'),
            sid=sid,
            organization=organization,
            recording=request.POST.get('RecordingUrl'),
        )
        response.find_contact()
        response.forward()
        resp = MessagingResponse()
        resp.message(organization.response_msg)
        return HttpResponse(str(resp))

    def get_sid(self, request):
        for sid in ('MessageSid', 'CallSid'):
            if request.POST.get(sid):
                return request.POST.get(sid)
        return None

class OrganizationUpdate(SuccessMessageMixin, UpdateView):
    model = Organization
    fields = ('name', 'twilio_api_key', 'twilio_secret',
        'phone', 'response_msg', 'forward_phone', 
        'forward_email')
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
