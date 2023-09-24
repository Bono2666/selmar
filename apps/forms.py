from django import forms
from django.forms import ModelForm
from apps.models import *
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm, UserCreationForm


class FormUser(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(FormUser, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['user_id'].widget = forms.TextInput(
            {'class': 'form-control text-uppercase', 'placeholder': 'XXXXX'})
        self.fields['username'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['email'].widget = forms.EmailInput(
            {'class': 'form-control'})
        self.fields['password1'].widget = forms.PasswordInput(
            {'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(
            {'class': 'form-control'})

    class Meta:
        model = User
        exclude = ['date_joined', 'password', 'is_active', 'is_staff', 'is_superuser']


class FormUserUpdate(ModelForm):
    class Meta:
        model = User
        exclude = ['user_id', 'password', 'date_joined',
                   'is_active', 'is_staff', 'is_superuser']


class FormChangePassword(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(FormChangePassword, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['old_password'].widget = forms.PasswordInput(
            {'class': 'form-control'})
        self.fields['new_password1'].widget = forms.PasswordInput(
            {'class': 'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(
            {'class': 'form-control'})


class FormSetPassword(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(FormSetPassword, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['new_password1'].widget = forms.PasswordInput(
            {'class': 'form-control'})
        self.fields['new_password2'].widget = forms.PasswordInput(
            {'class': 'form-control'})
