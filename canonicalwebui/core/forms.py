from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import App
from .models import Artifact
from .models import Screenshot
from .models import Team
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow 'Developer' option when users sign up
        self.fields['role'].choices = [('developer', 'Developer'), ('user', 'User')]

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.role == 'developer':
            user.is_approved = False  # require admin approval
        if user.role == 'admin':
            user.is_approved = False  # require admin approval 
        if user.role == 'user':
            user.is_approved = True # auto approve user
        if commit:
            user.save()
        return user


class AppForm(forms.ModelForm):
    artifacts_links = forms.CharField(
        required=False, widget=forms.Textarea(
            attrs={
                'placeholder': 'Enter hyperlinks (separate multiple links with commas)', 'class': 'form-control'},
        ),
    )

    class Meta:
        model = App
        fields = [
            'name', 'description', 'category',
            'teams_involved', 'artifacts_links',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter app name', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe your app', 'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'teams_involved': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }


class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.role == 'developer' and not user.is_approved:
            raise ValidationError(
                'Your account is awaiting admin approval.',
                code='inactive',
            )
