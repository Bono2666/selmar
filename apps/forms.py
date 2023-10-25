from django import forms
from django.forms import ModelForm
from apps.models import *
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm, UserCreationForm
import datetime


class FormUser(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(FormUser, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['user_id'].widget = forms.TextInput(
            {'class': 'form-control'})
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
        exclude = ['date_joined', 'password', 'is_active', 'is_staff',
                   'is_superuser', 'entry_date', 'entry_by', 'update_date', 'update_by']

        widgets = {
            'position': forms.Select(attrs={'class': 'form-control', 'place_holder': 'Select Position'}),
        }


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
        fields = ['user_id', 'username', 'email', 'position']

        widgets = {
            'position': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
        }


class FormUserUpdate(ModelForm):
    class Meta:
        model = User
        exclude = ['user_id', 'password', 'date_joined',
                   'is_active', 'is_staff', 'is_superuser', 'entry_date', 'entry_by', 'update_date', 'update_by']

        widgets = {
            'position': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Position'}),
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


class FormDistributor(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormDistributor, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['distributor_id'].widget = forms.TextInput(
            {'class': 'form-control text-uppercase'})
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
        exclude = ['distributor_id', 'entry_date',
                   'entry_by', 'update_date', 'update_by']


class FormAreaSales(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAreaSales, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['area_id'].widget = forms.TextInput(
            {'class': 'form-control text-uppercase'})
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
        exclude = ['area_id', 'entry_date',
                   'entry_by', 'update_date', 'update_by']


class FormAreaSalesDetailView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAreaSalesDetailView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['distributor'].label = ''

    class Meta:
        model = AreaSalesDetail
        fields = ['distributor']

        widgets = {
            'distributor': forms.Select(attrs={'class': 'form-control select2 border-0 ps-1 shadow-none bg-transparent', 'disabled': 'disabled'}),
        }


class FormAreaSalesDetail(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAreaSalesDetail, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['distributor'].label = ''

    class Meta:
        model = AreaSalesDetail
        exclude = ['area', 'entry_date',
                   'entry_by', 'update_date', 'update_by']

        widgets = {
            'distributor': forms.Select(attrs={'class': 'form-control select2 border-0 ps-1 shadow-none bg-transparent cursor-pointer', 'placeholder': 'Select Distributor'}),
        }


class FormAreaChannel(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAreaChannel, self).__init__(*args, **kwargs)
        self.label_suffix = ''

    class Meta:
        model = AreaChannel
        exclude = ['entry_date',
                   'entry_by', 'update_date', 'update_by']

        widgets = {
            'area_id': forms.Select(attrs={'class': 'form-control'}),
        }


class FormPosition(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormPosition, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['position_id'].widget = forms.TextInput(
            {'class': 'form-control text-uppercase', 'placeholder': 'XXX'})
        self.fields['position_name'].widget = forms.TextInput(
            {'class': 'form-control'})

    class Meta:
        model = Position
        exclude = ['entry_date', 'entry_by', 'update_date', 'update_by']


class FormPositionUpdate(ModelForm):
    class Meta:
        model = Position
        exclude = ['position_id', 'entry_date',
                   'entry_by', 'update_date', 'update_by']


class FormPositionView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormPositionView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['position_name'].widget = forms.TextInput(
            {'class': 'form-control', 'readonly': 'readonly'})

    class Meta:
        model = Position
        fields = ['position_id', 'position_name']


class FormMenu(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormMenu, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['menu_id'].widget = forms.TextInput(
            {'class': 'form-control text-uppercase'})
        self.fields['menu_name'].widget = forms.TextInput(
            {'class': 'form-control'})
        self.fields['menu_remark'].widget = forms.Textarea(
            {'class': 'form-control', 'rows': 3})

    class Meta:
        model = Menu
        exclude = ['entry_date', 'entry_by', 'update_date', 'update_by']


class FormMenuUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormMenuUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['menu_remark'].widget = forms.Textarea(
            {'class': 'form-control', 'rows': 3})

    class Meta:
        model = Menu
        exclude = ['entry_date', 'entry_by', 'update_date', 'update_by']


class FormMenuView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormMenuView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['menu_name'].widget = forms.TextInput(
            {'class': 'form-control', 'readonly': 'readonly'})
        self.fields['menu_remark'].widget = forms.Textarea(
            {'class': 'form-control', 'rows': 3, 'readonly': 'readonly'})

    class Meta:
        model = Menu
        fields = ['menu_id', 'menu_name', 'menu_remark']


class FormAuthUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAuthUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['add'].widget = forms.CheckboxInput(
            {'class': 'border mt-1'})
        self.fields['edit'].widget = forms.CheckboxInput(
            {'class': 'border mt-1'})
        self.fields['delete'].widget = forms.CheckboxInput(
            {'class': 'border mt-1'})

    class Meta:
        model = Auth
        exclude = ['user', 'entry_date',
                   'entry_by', 'update_date', 'update_by']


class FormChannel(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormChannel, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['channel_id'].widget = forms.TextInput(
            {'class': 'form-control text-uppercase'})
        self.fields['channel_name'].widget = forms.TextInput(
            {'class': 'form-control'})

    class Meta:
        model = Channel
        exclude = ['entry_date', 'entry_by', 'update_date', 'update_by']


class FormChannelUpdate(ModelForm):
    class Meta:
        model = Channel
        exclude = ['channel_id', 'entry_date',
                   'entry_by', 'update_date', 'update_by']


class FormChannelView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormChannelView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['channel_name'].widget = forms.TextInput(
            {'class': 'form-control', 'readonly': 'readonly'})

    class Meta:
        model = Channel
        fields = ['channel_id', 'channel_name']


class FormBudget(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormBudget, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['budget_amount'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'readonly': 'readonly'})
        self.fields['budget_total'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'readonly': 'readonly'})

    class Meta:
        model = Budget
        exclude = ['budget_no', 'budget_status', 'entry_date',
                   'entry_by', 'update_date', 'update_by']

        YEAR_CHOICES = []
        for r in range((datetime.datetime.now().year-1), (datetime.datetime.now().year+2)):
            YEAR_CHOICES.append((r, r))

        MONTH_CHOICES = []
        for r in range(1, 13):
            MONTH_CHOICES.append((r, r))

        AREA_CHOICES = []
        for r in AreaSales.objects.all():
            AREA_CHOICES.append((r.area_id, r.area_id + ' - ' + r.area_name))

        DISTRIBUTOR_CHOICES = []
        for r in Distributor.objects.all():
            DISTRIBUTOR_CHOICES.append(
                (r.distributor_id, r.distributor_id + ' - ' + r.distributor_name))

        widgets = {
            'budget_year': forms.Select(choices=YEAR_CHOICES, attrs={'class': 'form-control'}),
            'budget_month': forms.Select(choices=MONTH_CHOICES, attrs={'class': 'form-control'}),
            'budget_area': forms.Select(choices=AREA_CHOICES, attrs={'class': 'form-control'}),
            'budget_distributor': forms.Select(choices=DISTRIBUTOR_CHOICES, attrs={'class': 'form-control'}),
        }


class FormBudgetUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormBudgetUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['budget_amount'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'readonly': 'readonly'})
        self.fields['budget_upping'].widget = forms.NumberInput(
            attrs={'class': 'form-control'})
        self.fields['budget_total'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'readonly': 'readonly'})

    class Meta:
        model = Budget
        exclude = ['budget_no', 'entry_date', 'entry_by',
                   'update_date', 'update_by', 'budget_year', 'budget_month', 'budget_area', 'budget_distributor']


class FormBudgetView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormBudgetView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['budget_amount'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'readonly': 'readonly'})
        self.fields['budget_upping'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'readonly': 'readonly'})
        self.fields['budget_total'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'readonly': 'readonly'})

    class Meta:
        model = Budget
        fields = ['budget_no', 'budget_year', 'budget_month', 'budget_area',
                  'budget_distributor', 'budget_amount', 'budget_upping', 'budget_total']

        widgets = {
            'budget_year': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'budget_month': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'budget_area': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'budget_distributor': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
        }


class FormBudgetDetailUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormBudgetDetailUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['budget_percent'].widget = forms.NumberInput(
            attrs={'class': 'form-control'})

    class Meta:
        model = BudgetDetail
        fields = ['budget_percent']


class FormBudgetDetailView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormBudgetDetailView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['budget_percent'].widget = forms.NumberInput(
            attrs={'class': 'form-control', 'readonly': 'readonly'})

    class Meta:
        model = BudgetDetail
        fields = ['budget_percent']
