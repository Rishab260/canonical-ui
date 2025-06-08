from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from .models import App, Artifact, Screenshot, Team, User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [('developer', 'Developer'), ('user', 'User')]
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_approved = user.role == 'user'  # auto-approve users
        if commit:
            user.save()
        return user

class AppForm(forms.ModelForm):
    artifacts_links = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter hyperlinks (separate multiple links with commas)',
            'class': 'form-control',
            'rows': 3
        }),
        help_text="You can add multiple links separated by commas."
    )

    class Meta:
        model = App
        fields = ['name', 'description', 'category', 'teams_involved', 'artifacts_links']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter app name', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe your app', 'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'teams_involved': forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            'teams_involved': 'Select one or more teams involved in this app.',
        }

    def clean_artifacts_links(self):
        links = self.cleaned_data.get('artifacts_links')
        if links:
            for link in [l.strip() for l in links.split(',') if l.strip()]:
                if not link.startswith(('http://', 'https://')):
                    raise forms.ValidationError(f"Invalid URL: {link}")
        return links

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.role == 'developer' and not user.is_approved:
            raise ValidationError(
                'Your developer account is awaiting admin approval.',
                code='inactive',
            )
