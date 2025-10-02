# apps/core/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend to allow login with email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Use the 'username' field to represent the email
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None