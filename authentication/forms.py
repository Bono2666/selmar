from django import forms


class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['username'].label = 'User Name'
        
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "User Name",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
