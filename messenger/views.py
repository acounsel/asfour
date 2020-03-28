from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator

from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
from .decorators import validate_twilio_request
from .models import Organization, UserProfile, Contact
from .models import Message, Response

decorators = [
    csrf_exempt, require_POST, validate_twilio_request
]

class LoginRequiredMixin(LoginRequiredMixin):

    def get_profile(self):
        return self.request.user.userprofile

    def get_org(self):
        return self.get_profile().organization

class Home(View):
    template_name = 'home.html'

    def get(self, request, **kwargs):
        return render(request, self.template_name)

class OrgListView(LoginRequiredMixin, ListView):

    def get_queryset(self):
        queryset = super(OrgListView, self).get_queryset()
        organization = self.get_org()
        return queryset.filter(organization=organization)

class OrgDetailView(LoginRequiredMixin, DetailView):

    def get_queryset(self):
        queryset = super(OrgDetailView, self).get_queryset()
        organization = self.get_org()
        return queryset.filter(organization=organization)

class OrgCreateView(LoginRequiredMixin, CreateView):

    def form_valid(self, form):
        form.instance.organization = self.get_org()
        messages.success(
            self.request,
            '{} Created'.format(
                form.instance._meta.verbose_name.title()
            )
        )
        # response = super().form_valid(form)
        return super().form_valid(form)

class OrgUpdateView(LoginRequiredMixin, UpdateView):

    def form_valid(self, form):
        form.instance.organization = self.get_org()
        messages.success(
            self.request,
            '{} Created'.format(
                form.instance._meta.verbose_name.title()
            )
        )
        return super().form_valid(form)

class ContactView(View):
    model = Contact
    fields = ('first_name', 'last_name', 'phone', 'email',
        'preferred_method', 'has_whatsapp')
    success_url = reverse_lazy('contact-list')

class ContactList(ContactView, OrgListView):
    pass

class ContactDetail(ContactView, OrgDetailView):
    pass

class ContactCreate(ContactView, OrgCreateView):
    pass

class ContactUpdate(ContactView, OrgUpdateView):
    pass

class MessageView(View):
    model = Message
    fields = ('body', 'attachment', 'contacts')

class MessageList(MessageView, OrgListView):
    pass

class MessageDetail(MessageView, OrgDetailView):
    pass

class MessageCreate(MessageView, OrgCreateView):
    pass

class MessageUpdate(MessageView, OrgUpdateView):
    pass

class MessageSend(MessageDetail):

    def get(self, request, **kwargs):
        response = super().get(request, **kwargs)
        context = self.get_context_data(**kwargs)
        message = self.get_object()
        message.send()
        return redirect(reverse('home'))

class ResponseView(View):
    model = Response

class ResponseList(ResponseView, ListView):
    pass

@method_decorator(decorators, name='dispatch')
class HarvestResponse(View):

    def post(self, request, **kwargs):
        body = self.request.values.get('Body', None)
        print(body)
        print(self.request.values)
        organization = Organization.objects.get(
            id=self.kwargs.get('pk'))
        response = Response.objects.create(
            body=body,
            phone=self.request.values.get('from_'),
            sid=self.request.values.get('sid'),
            organization=organization,
        )
        resp = MessagingResponse()
        resp.message('Thank you for your message')
        return str(resp)