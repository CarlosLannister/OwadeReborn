from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions


class LoginForm(forms.Form):
    user_username = forms.CharField(label="Username")
    user_password = forms.CharField(label="Password", widget=forms.PasswordInput())

