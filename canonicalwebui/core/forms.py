from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from .models import App, Team, User, Feedback, Rating

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
        user.is_approved = user.role == 'user'
        if commit:
            user.save()
        return user

class AppForm(forms.ModelForm):
    class Meta:
        model = App
        fields = ['name', 'description', 'category', 'teams_involved', 'icon', 'tech_stack', 'authors']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter app name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your app',
                'rows': 4
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'teams_involved': forms.CheckboxSelectMultiple(),
            'icon': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'authors': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter author names (comma separated)'
            }),
        }
        help_texts = {
            'teams_involved': 'Select one or more teams involved in this app.',
        }


class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.role == 'developer' and not user.is_approved:
            raise ValidationError(
                'Your developer account is awaiting admin approval.',
                code='inactive',
            )


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Leave your feedback...',
                'rows': 3
            }),
        }
        labels = {
            'comment': ''
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['gmail','rating', 'review']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'review': forms.Textarea(attrs={
                'placeholder': 'Write your review (optional)...',
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'rating': 'Your Rating (1 to 5 stars)',
            'review': ''
        }
