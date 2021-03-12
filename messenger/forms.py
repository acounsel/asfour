from django import forms

from .models import Message, Organization

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('method', 'body', 'attachment', 'recording', 
        'tags', 'contacts', 'request_for_response')

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ('name', 'twilio_api_key', 'twilio_secret',
        'phone', 'response_msg', 'forward_phone', 
        'forward_email')
        widgets = {
            'twilio_secret': forms.PasswordInput(
                render_value=True)
        }

