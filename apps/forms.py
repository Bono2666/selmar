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
        exclude = ['date_joined', 'password', 'is_active', 'is_staff', 'is_superuser', 'entry_date', 'entry_by', 'update_date', 'update_by']


class FormUserView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormUserView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['username'].widget = forms.TextInput(
            {'class': 'form-control', 'readonly': 'readonly'})
        self.fields['email'].widget = forms.EmailInput(
            {'class': 'form-control', 'readonly': 'readonly'})
        
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email']


class FormUserUpdate(ModelForm):
    class Meta:
        model = User
        exclude = ['user_id', 'password', 'date_joined',
                   'is_active', 'is_staff', 'is_superuser', 'entry_date', 'entry_by', 'update_date', 'update_by']


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
        

class FormDistributor(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormDistributor, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['distributor_id'].widget = forms.TextInput(
            {'class': 'form-control text-uppercase', 'placeholder': 'XXXXX'})
        self.fields['distributor_name'].widget = forms.TextInput(
            {'class': 'form-control'})

    class Meta:
        model = Distributor
        exclude = ['entry_date', 'entry_by', 'update_date', 'update_by']


class FormDistributorView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormDistributorView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['distributor_name'].widget = forms.TextInput(
            {'class': 'form-control', 'readonly': 'readonly'})

    class Meta:
        model = Distributor
        fields = ['distributor_id', 'distributor_name']

        
class FormDistributorUpdate(ModelForm):
    class Meta:
        model = Distributor
        exclude = ['distributor_id', 'entry_date', 'entry_by', 'update_date', 'update_by']


class FormAreaSales(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAreaSales, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['area_id'].widget = forms.TextInput(
            {'class': 'form-control text-uppercase', 'placeholder': 'XXXXX'})
        self.fields['area_name'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['manager'].widget = forms.TextInput(
            {'class': 'form-control'})

    class Meta:
        model = AreaSales
        exclude = ['entry_date', 'entry_by', 'update_date', 'update_by']


class FormAreaSalesView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAreaSalesView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['area_name'].widget = forms.TextInput(
            {'class': 'form-control', 'readonly': 'readonly'})
        self.fields['manager'].widget = forms.TextInput(
            {'class': 'form-control', 'readonly': 'readonly'})

    class Meta:
        model = AreaSales
        fields = ['area_id', 'area_name', 'manager']

        
class FormAreaSalesUpdate(ModelForm):
    class Meta:
        model = AreaSales
        exclude = ['area_id', 'entry_date', 'entry_by', 'update_date', 'update_by']


class FormAreaSalesDetailView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAreaSalesDetailView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['distributor'].label = ''

    class Meta:
        model = AreaSalesDetail
        fields = ['distributor']

        widgets = {
            'distributor': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
        }


class FormAreaSalesDetail(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAreaSalesDetail, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['distributor'].label = ''
        
    class Meta:
        model = AreaSalesDetail
        exclude = ['area', 'entry_date', 'entry_by', 'update_date', 'update_by']

        widgets = {
            'distributor': forms.Select(attrs={'class': 'form-control'}),
        }


class FormPosition(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormPosition, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['position_id'].widget = forms.TextInput(
            {'class': 'form-control text-uppercase', 'placeholder': 'XXXXX'})
        self.fields['position_name'].widget = forms.TextInput(
            {'class': 'form-control'})

    class Meta:
        model = Position
        exclude = ['entry_date', 'entry_by', 'update_date', 'update_by']


class FormPositionUpdate(ModelForm):
    class Meta:
        model = Position
        exclude = ['position_id', 'entry_date', 'entry_by', 'update_date', 'update_by']


class FormPositionView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormPositionView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['position_name'].widget = forms.TextInput(
            {'class': 'form-control', 'readonly': 'readonly'})

    class Meta:
        model = Position
        fields = ['position_id', 'position_name']
        