from django import forms
from django.forms import ModelForm
from apps.models import *
from django.contrib.auth.forms import UserCreationForm


class FormHero(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormHero, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['image'].label = 'Gambar'
        self.fields['title'].label = 'Judul'

    class Meta:
        model = Hero
        fields = '__all__'

        widgets = {
            'image': forms.FileInput({'class': 'form-control'}),
            'title': forms.TextInput({'class': 'form-control'}),
        }


class FormUser(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(FormUser, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['username'].widget = forms.TextInput({'class': 'form-control'})
        self.fields['password1'].widget = forms.PasswordInput({'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput({'class': 'form-control'})

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role']

        widgets = {
            'role': forms.Select({'class': 'form-control'}),
        }


class FormUserUpdate(ModelForm):
    class Meta:
        model = User
        exclude = ['username', 'password', 'date_joined']
