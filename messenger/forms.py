from django import forms

from .models import Contact, Message, Organization, Tag

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('method', 'body', 'attachment', 'recording', 
        'tags', 'contacts', 'request_for_response')

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile')
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.filter(
            organization=user_profile.organization)
        self.fields['contacts'].queryset = Contact.objects.filter(
            organization=user_profile.organization)

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

