from django.http import HttpResponse, HttpResponseForbidden
from functools import wraps
from twilio import twiml
from twilio.request_validator import RequestValidator

from .models import Organization

import os

def validate_twilio_request(f):
    """Validates incoming requests originated from Twilio"""
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        # Create an instance of the RequestValidator class
        org = Organization.objects.get(id=kwargs.get('pk'))
        validator = RequestValidator(org.twilio_secret)

        # Validate the request using its URL, POST data,
        # and X-TWILIO-SIGNATURE header
        request_valid = validator.validate(
            request.build_absolute_uri(),
            request.POST,
            request.META.get('HTTP_X_TWILIO_SIGNATURE', ''))

        # Continue processing the request if it's valid, 
        # return a 403 error if it's not
        if request_valid:
            return f(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return decorated_function