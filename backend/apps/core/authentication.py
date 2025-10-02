# apps/core/authentication.py

from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import timedelta
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import exceptions
from django.conf import settings


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Token authentication with automatic expiration after inactivity.
    Tokens expire after 3 minutes (180 seconds) of inactivity.
    """
    
    # 3 minutes in seconds
    INACTIVITY_TIMEOUT = getattr(settings, 'TOKEN_INACTIVITY_TIMEOUT', 180)
    
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        # Check if token has expired due to inactivity
        if self.token_expired(token):
            token.delete()
            raise exceptions.AuthenticationFailed('Token has expired due to inactivity.')

        # Update the token's last activity time
        self.update_token_activity(token)

        return (token.user, token)

    def token_expired(self, token):
        """
        Check if the token has expired based on last activity.
        """
        try:
            from .models import TokenActivity
            activity = TokenActivity.objects.get(token=token)
            
            now = timezone.now()
            expiration_time = activity.last_activity + timedelta(seconds=self.INACTIVITY_TIMEOUT)
            return now > expiration_time
            
        except TokenActivity.DoesNotExist:
            # If no activity record exists, consider it active for this request
            # and create the record
            return False

    def update_token_activity(self, token):
        """
        Update the token's last activity timestamp.
        """
        try:
            # Try to update existing TokenActivity
            from .models import TokenActivity
            activity, created = TokenActivity.objects.update_or_create(
                token=token,
                defaults={'last_activity': timezone.now()}
            )
        except ImportError:
            # If TokenActivity model doesn't exist, we'll add it
            pass


class InactivityMiddleware:
    """
    Middleware to track user activity and automatically logout inactive users.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.INACTIVITY_TIMEOUT = getattr(settings, 'TOKEN_INACTIVITY_TIMEOUT', 180)

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Update activity timestamp for authenticated API requests
        if hasattr(request, 'auth') and request.auth:
            self.update_token_activity(request.auth)
        elif hasattr(request, 'user') and request.user.is_authenticated:
            # For session-based authentication
            request.session['last_activity'] = timezone.now().timestamp()
            request.session.set_expiry(self.INACTIVITY_TIMEOUT)
        
        return response

    def update_token_activity(self, token):
        """
        Update token activity timestamp.
        """
        try:
            from .models import TokenActivity
            TokenActivity.objects.update_or_create(
                token=token,
                defaults={'last_activity': timezone.now()}
            )
        except ImportError:
            pass