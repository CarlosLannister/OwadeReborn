from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions


class LoginForm(forms.Form):
    user_username = forms.CharField(label="Username")
    user_password = forms.CharField(label="Password", widget=forms.PasswordInput())

class AnalyzeForm(forms.Form):
    image = forms.CharField(label='Select an image', help_text='dd format')


    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('image', css_class='input-xlarge'),
        'radio_buttons',
        FormActions(
            Submit('save_changes', 'Save changes', css_class="btn-primary"),
            Submit('cancel', 'Cancel'),
        )
    )
