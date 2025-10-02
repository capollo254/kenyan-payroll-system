# apps/core/serializers.py

from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

# Get the custom User model from settings
User = settings.AUTH_USER_MODEL

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer to handle user authentication and login.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, data):
        """
        Validate the user's credentials using the request context.
        """
        email = data.get('email')
        password = data.get('password')
        request = self.context.get('request') # <-- Get the request object here

        if email and password:
            # Pass the request object to the authenticate function
            # Use username=email because our custom backend expects username parameter
            user = authenticate(request=request, username=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError(_("User account is disabled."))
                data['user'] = user
            else:
                raise serializers.ValidationError(_("Unable to log in with provided credentials."))
        else:
            raise serializers.ValidationError(_("Must include 'email' and 'password'."))
            
        return data