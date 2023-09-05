from django import forms
from django.forms import ModelForm
from apps.models import *
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm, UserCreationForm


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
        self.fields['username'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['password1'].widget = forms.PasswordInput(
            {'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(
            {'class': 'form-control'})

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role']

        widgets = {
            'role': forms.Select({'class': 'form-control'}),
        }


class FormUserUpdate(ModelForm):
    class Meta:
        model = User
        exclude = ['username', 'password', 'date_joined',
                   'is_active', 'is_staff', 'is_superuser']

        widgets = {
            'role': forms.Select({'class': 'form-control'}),
        }


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


class FormSetup(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSetup, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['website'].required = False
        self.fields['question_1'].required = False
        self.fields['question_2'].required = False
        self.fields['question_3'].required = False
        self.fields['logo'].required = False
        self.fields['kecamatan'].required = False
        self.fields['telp'].required = False
        self.fields['signature'].required = False

        self.fields['logo'].widget = forms.FileInput({'class': 'form-control'})
        self.fields['alamat'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['kota'].widget = forms.TextInput({'class': 'form-control'})
        self.fields['kecamatan'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['slogan'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['website'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['note'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['signature'].widget = forms.FileInput(
            {'class': 'form-control'})
        self.fields['signature_name'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['signature_title'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['question_1'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['question_2'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['question_3'].widget = forms.TextInput(
            {'class': 'form-control'})

    class Meta:
        model = Setup
        fields = '__all__'

        waktu = [
            ('', 'Pilih Waktu'),
            ('1 Jam Sebelumnya', '1 Jam Sebelumnya'),
            ('2 Jam Sebelumnya', '2 Jam Sebelumnya'),
            ('3 Jam Sebelumnya', '3 Jam Sebelumnya'),
        ]

        widgets = {
            'waktu_pengiriman': forms.Select(choices=waktu, attrs={'class': 'form-control'}),
            'waktu_masakan_siap': forms.Select(choices=waktu, attrs={'class': 'form-control'}),
            'telp': forms.TextInput({'class': 'form-control', 'type': 'tel', 'placeholder': '+628xxxxxxxxxx'}),
        }


class FormCabang(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormCabang, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['nama'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['alamat'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['kota'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['kecamatan'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['telp'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['manager'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['rekening_1'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['atas_nama_1'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['bank_1'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['rekening_2'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['atas_nama_2'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['bank_2'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['rekening_2'].required = False
        self.fields['atas_nama_2'].required = False
        self.fields['bank_2'].required = False

    class Meta:
        model = Cabang
        fields = '__all__'


class FormPaket(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormPaket, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['nama'].widget = forms.TextInput(
            {'class': 'form-control'})

    class Meta:
        model = Paket
        fields = '__all__'


class FormKategoriItem(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormKategoriItem, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['nama'].widget = forms.TextInput(
            {'class': 'form-control'})

    class Meta:
        model = KategoriItem
        fields = '__all__'
        