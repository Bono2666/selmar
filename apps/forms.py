from django import forms
from django.forms import ModelForm
from apps.models import *
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm, UserCreationForm
import datetime


class FormUser(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(FormUser, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['user_id'].label = 'User ID'
        self.fields['username'].label = 'User Name'
        self.fields['email'].label = 'Email'
        self.fields['position'].label = 'Position'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'
        self.fields['user_id'].widget = forms.TextInput(
            {'class': 'form-control-sm'})
        self.fields['username'].widget = forms.TextInput(
            {'class': 'form-control-sm'})
        self.fields['email'].widget = forms.EmailInput(
            {'class': 'form-control-sm'})
        self.fields['password1'].widget = forms.PasswordInput(
            {'class': 'form-control-sm'})
        self.fields['password2'].widget = forms.PasswordInput(
            {'class': 'form-control-sm'})

    class Meta:
        model = User
        exclude = ['date_joined', 'password', 'is_active', 'is_staff',
                   'is_superuser', 'entry_date', 'entry_by', 'update_date', 'update_by']


class FormUserView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormUserView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['username'].label = 'User Name'
        self.fields['email'].label = 'Email'
        self.fields['position'].label = 'Position'
        self.fields['username'].widget = forms.TextInput(
            {'class': 'form-control-sm', 'readonly': 'readonly'})
        self.fields['email'].widget = forms.EmailInput(
            {'class': 'form-control-sm', 'readonly': 'readonly'})

    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'position']

        widgets = {
            'position': forms.Select(attrs={'class': 'form-control form-select-sm', 'disabled': 'disabled'}),
        }


class FormUserUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormUserUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['username'].label = 'User Name'
        self.fields['email'].label = 'Email'
        self.fields['position'].label = 'Position'
        self.fields['username'].widget = forms.TextInput(
            {'class': 'form-control-sm'})
        self.fields['email'].widget = forms.EmailInput(
            {'class': 'form-control-sm'})

    class Meta:
        model = User
        exclude = ['user_id', 'password', 'date_joined',
                   'is_active', 'is_staff', 'is_superuser', 'entry_date', 'entry_by', 'update_date', 'update_by']

        widgets = {
            'position': forms.Select(attrs={'class': 'form-control form-select-sm'}),
        }


class FormChangePassword(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(FormChangePassword, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['old_password'].label = 'Old Password'
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'New Password Confirmation'
        self.fields['old_password'].widget = forms.PasswordInput(
            {'class': 'form-control-sm'})
        self.fields['new_password1'].widget = forms.PasswordInput(
            {'class': 'form-control-sm'})
        self.fields['new_password2'].widget = forms.PasswordInput(
            {'class': 'form-control-sm'})


class FormSetPassword(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(FormSetPassword, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'New Password Confirmation'
        self.fields['new_password1'].widget = forms.PasswordInput(
            {'class': 'form-control-sm'})
        self.fields['new_password2'].widget = forms.PasswordInput(
            {'class': 'form-control-sm'})


class FormDistributor(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormDistributor, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['distributor_id'].label = 'Distributor ID'
        self.fields['distributor_name'].label = 'Distributor Name'
        self.fields['sap_code'].label = 'SAP ID'
        self.fields['distributor_id'].widget = forms.TextInput(
            {'class': 'form-control-sm text-uppercase'})
        self.fields['distributor_name'].widget = forms.TextInput(
            {'class': 'form-control-sm'})
        self.fields['sap_code'].widget = forms.TextInput(
            {'class': 'form-control-sm'})

    class Meta:
        model = Distributor
        exclude = ['entry_date', 'entry_by', 'update_date', 'update_by']


class FormDistributorView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormDistributorView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['distributor_name'].label = 'Distributor Name'
        self.fields['sap_code'].label = 'SAP ID'
        self.fields['distributor_name'].widget = forms.TextInput(
            {'class': 'form-control-sm', 'readonly': 'readonly'})
        self.fields['sap_code'].widget = forms.TextInput(
            {'class': 'form-control-sm', 'readonly': 'readonly'})

    class Meta:
        model = Distributor
        fields = ['distributor_id', 'distributor_name', 'sap_code']


class FormDistributorUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormDistributorUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['distributor_name'].label = 'Distributor Name'
        self.fields['sap_code'].label = 'SAP ID'
        self.fields['distributor_name'].widget = forms.TextInput(
            {'class': 'form-control-sm'})
        self.fields['sap_code'].widget = forms.TextInput(
            {'class': 'form-control-sm'})

    class Meta:
        model = Distributor
        exclude = ['distributor_id', 'entry_date',
                   'entry_by', 'update_date', 'update_by']


class FormAreaSales(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAreaSales, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['area_id'].label = 'Area Sales ID'
        self.fields['area_name'].label = 'Area Sales Name'
        self.fields['manager'].label = 'Area Sales Manager'
        self.fields['area_id'].widget = forms.TextInput(
            {'class': 'form-control-sm text-uppercase'})
        self.fields['area_name'].widget = forms.TextInput(
            {'class': 'form-control-sm'})
        self.fields['manager'].widget = forms.TextInput(
            {'class': 'form-control-sm'})

    class Meta:
        model = AreaSales
        exclude = ['entry_date', 'entry_by', 'update_date', 'update_by']


class FormAreaSalesView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAreaSalesView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['area_name'].label = 'Area Sales Name'
        self.fields['manager'].label = 'Area Sales Manager'
        self.fields['area_name'].widget = forms.TextInput(
            {'class': 'form-control-sm', 'readonly': 'readonly'})
        self.fields['manager'].widget = forms.TextInput(
            {'class': 'form-control-sm', 'readonly': 'readonly'})

    class Meta:
        model = AreaSales
        fields = ['area_id', 'area_name', 'manager']


class FormAreaSalesUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormAreaSalesUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['area_name'].label = 'Area Sales Name'
        self.fields['manager'].label = 'Area Sales Manager'
        self.fields['area_name'].widget = forms.TextInput(
            {'class': 'form-control-sm'})
        self.fields['manager'].widget = forms.TextInput(
            {'class': 'form-control-sm'})

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


class FormPosition(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormPosition, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['position_id'].label = 'Position ID'
        self.fields['position_name'].label = 'Position Name'
        self.fields['position_id'].widget = forms.TextInput(
            {'class': 'form-control-sm text-uppercase', 'placeholder': 'XXX'})
        self.fields['position_name'].widget = forms.TextInput(
            {'class': 'form-control-sm'})

    class Meta:
        model = Position
        exclude = ['entry_date', 'entry_by', 'update_date', 'update_by']


class FormPositionUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormPositionUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['position_name'].label = 'Position Name'
        self.fields['position_name'].widget = forms.TextInput(
            {'class': 'form-control-sm'})

    class Meta:
        model = Position
        exclude = ['position_id', 'entry_date',
                   'entry_by', 'update_date', 'update_by']


class FormPositionView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormPositionView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['position_name'].label = 'Position Name'
        self.fields['position_name'].widget = forms.TextInput(
            {'class': 'form-control-sm', 'readonly': 'readonly'})

    class Meta:
        model = Position
        fields = ['position_id', 'position_name']


class FormMenu(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormMenu, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['menu_id'].label = 'Menu ID'
        self.fields['menu_name'].label = 'Menu Name'
        self.fields['menu_remark'].label = 'Description'
        self.fields['menu_id'].widget = forms.TextInput(
            {'class': 'form-control-sm text-uppercase'})
        self.fields['menu_name'].widget = forms.TextInput(
            {'class': 'form-control-sm'})
        self.fields['menu_remark'].widget = forms.Textarea(
            {'class': 'form-control-sm', 'rows': 3})

    class Meta:
        model = Menu
        exclude = ['entry_date', 'entry_by', 'update_date', 'update_by']


class FormMenuUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormMenuUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['menu_name'].label = 'Menu Name'
        self.fields['menu_remark'].label = 'Description'
        self.fields['menu_name'].widget = forms.TextInput(
            {'class': 'form-control-sm'})
        self.fields['menu_remark'].widget = forms.Textarea(
            {'class': 'form-control-sm', 'rows': 3})

    class Meta:
        model = Menu
        exclude = ['menu_id', 'entry_date',
                   'entry_by', 'update_date', 'update_by']


class FormMenuView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormMenuView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['menu_name'].label = 'Menu Name'
        self.fields['menu_remark'].label = 'Description'
        self.fields['menu_name'].widget = forms.TextInput(
            {'class': 'form-control-sm', 'readonly': 'readonly'})
        self.fields['menu_remark'].widget = forms.Textarea(
            {'class': 'form-control-sm', 'rows': 3, 'readonly': 'readonly'})

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
        self.fields['channel_id'].label = 'Channel ID'
        self.fields['channel_name'].label = 'Channel Name'
        self.fields['channel_id'].widget = forms.TextInput(
            {'class': 'form-control-sm text-uppercase'})
        self.fields['channel_name'].widget = forms.TextInput(
            {'class': 'form-control-sm'})

    class Meta:
        model = Channel
        exclude = ['entry_date', 'entry_by', 'update_date', 'update_by']


class FormChannelUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormChannelUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['channel_name'].label = 'Channel Name'
        self.fields['channel_name'].widget = forms.TextInput(
            {'class': 'form-control-sm'})

    class Meta:
        model = Channel
        exclude = ['channel_id', 'entry_date',
                   'entry_by', 'update_date', 'update_by']


class FormChannelView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormChannelView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['channel_name'].label = 'Channel Name'
        self.fields['channel_name'].widget = forms.TextInput(
            {'class': 'form-control-sm', 'readonly': 'readonly'})

    class Meta:
        model = Channel
        fields = ['channel_id', 'channel_name']


class FormBudget(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormBudget, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['budget_year'].label = 'Year'
        self.fields['budget_month'].label = 'Month'
        self.fields['budget_area'].label = 'Area'
        self.fields['budget_distributor'].label = 'Distributor'
        self.fields['budget_amount'].label = 'Beginning Balance'
        self.fields['budget_upping'].label = 'Upping Price'
        self.fields['budget_total'].label = 'Total Budget'
        self.fields['budget_amount'].widget = forms.NumberInput(
            attrs={'class': 'form-control-sm no-spinners'})
        self.fields['budget_upping'].widget = forms.NumberInput(
            attrs={'class': 'form-control-sm', 'readonly': 'readonly'})
        self.fields['budget_total'].widget = forms.NumberInput(
            attrs={'class': 'form-control-sm', 'readonly': 'readonly'})

    class Meta:
        model = Budget
        exclude = ['budget_id', 'budget_status', 'entry_date',
                   'entry_by', 'update_date', 'update_by']

        YEAR_CHOICES = []
        for r in range((datetime.datetime.now().year-1), (datetime.datetime.now().year+2)):
            YEAR_CHOICES.append((r, r))

        MONTH_CHOICES = []
        for r in range(1, 13):
            MONTH_CHOICES.append((r, r))

        widgets = {
            'budget_year': forms.Select(choices=YEAR_CHOICES, attrs={'class': 'form-control form-select-sm'}),
            'budget_month': forms.Select(choices=MONTH_CHOICES, attrs={'class': 'form-control form-select-sm'}),
        }


class FormBudgetUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormBudgetUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['budget_upping'].label = 'Upping Price'
        self.fields['budget_upping'].widget = forms.NumberInput(
            attrs={'class': 'form-control-sm no-spinners'})

    class Meta:
        model = Budget
        fields = ['budget_upping']


class FormBudgetView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormBudgetView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['budget_year'].label = 'Year'
        self.fields['budget_month'].label = 'Month'
        self.fields['budget_area'].label = 'Area'
        self.fields['budget_distributor'].label = 'Distributor'
        self.fields['budget_amount'].label = 'Beginning Balance'
        self.fields['budget_upping'].label = 'Upping Price'
        self.fields['budget_total'].label = 'Total Budget'
        self.fields['budget_amount'].widget = forms.TextInput(
            attrs={'class': 'form-control-sm', 'readonly': 'readonly'})
        self.fields['budget_upping'].widget = forms.TextInput(
            attrs={'class': 'form-control-sm', 'readonly': 'readonly'})
        self.fields['budget_total'].widget = forms.TextInput(
            attrs={'class': 'form-control-sm', 'readonly': 'readonly'})

    class Meta:
        model = Budget
        fields = ['budget_id', 'budget_year', 'budget_month', 'budget_area',
                  'budget_distributor', 'budget_amount', 'budget_upping', 'budget_total']

        widgets = {
            'budget_area': forms.Select(attrs={'class': 'form-control form-select-sm', 'disabled': 'disabled'}),
            'budget_distributor': forms.Select(attrs={'class': 'form-control form-select-sm', 'disabled': 'disabled'}),
        }


class FormBudgetDetailUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormBudgetDetailUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['budget_percent'].label = 'Percent'
        self.fields['budget_percent'].widget = forms.NumberInput(
            attrs={'class': 'form-control-sm no-spinners'})

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


class FormBudgetApproval(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormBudgetApproval, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['area'].label = 'Area'
        self.fields['approver1'].label = 'Financial Planning Supervisor'
        self.fields['approver2'].label = 'Financial Planning Manager'
        self.fields['approver1'].widget = forms.Select(
            attrs={'class': 'form-control form-select-sm'})
        self.fields['approver2'].widget = forms.Select(
            attrs={'class': 'form-control form-select-sm'})

    class Meta:
        model = Budget
        fields = '__all__'


class FormBudgetApprovalView(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormBudgetApprovalView, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['area'].label = 'Area'
        self.fields['approver1'].label = 'Financial Planning Supervisor'
        self.fields['approver2'].label = 'Financial Planning Manager'
        self.fields['approver1'].widget = forms.Select(
            attrs={'class': 'form-control form-select-sm', 'disabled': 'disabled'})
        self.fields['approver2'].widget = forms.Select(
            attrs={'class': 'form-control form-select-sm', 'disabled': 'disabled'})

    class Meta:
        model = Budget
        fields = ['area', 'approver1', 'approver2']


class FormBudgetApprovalUpdate(ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormBudgetApprovalUpdate, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['approver1'].label = 'Financial Planning Supervisor'
        self.fields['approver2'].label = 'Financial Planning Manager'
        self.fields['approver1'].widget = forms.Select(
            attrs={'class': 'form-control form-select-sm'})
        self.fields['approver2'].widget = forms.Select(
            attrs={'class': 'form-control form-select-sm'})

    class Meta:
        model = Budget
        fields = ['approver1', 'approver2']
