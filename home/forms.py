from django import forms

class UserForms(forms.Form):
    first_name = forms.CharField(label="first_name", max_length=100, required=True)
    last_name = forms.CharField(label="last_name", max_length=100, required=True)
    email = forms.EmailField(label="email", required=True)
    password = forms.CharField(label="password", required=True)
    confirm_password = forms.CharField(label="confirm_password", required=True)