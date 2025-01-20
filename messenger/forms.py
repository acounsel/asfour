from django import forms

from .models import Contact, Message, Organization, Tag

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('name', 'method', 'body', 'attachment', 
            'recording', 'tags', 'contacts', 
            'request_for_response')

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile')
        super(MessageForm, self).__init__(*args, **kwargs)
        # self.fields['tags'].queryset = Tag.objects.filter(
        #     organization=user_profile.organization)
        self.fields['contacts'].queryset = Contact.objects.filter(
            organization=user_profile.organization)
        tags = Tag.objects.filter(is_active=True,
            organization=user_profile.organization)
        tag_choices = [
            (tag.id, f"{tag.name} ({tag.contact_set.count()} contacts)")
            for tag in tags
        ]

        self.fields['tags'] = forms.MultipleChoiceField(
            choices=tag_choices,
            widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            required=False,
        )

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

