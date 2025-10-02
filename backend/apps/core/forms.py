from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password field.
    """
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'phone_number',)

    def clean(self):
        super().clean()
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password != password2:
            self.add_error("password2", "Passwords don't match.")
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with a admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'is_staff', 'is_active', 'is_superuser', 'phone_number', 'profile_picture',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get('is_superuser'):
            self.fields['is_staff'].disabled = True