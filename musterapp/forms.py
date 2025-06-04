from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class PasswordResetForm(forms.Form):
    employee_id = forms.CharField(max_length=100, label='Employee ID')
    old_password = forms.CharField(widget=forms.PasswordInput(), label='Old Password')
    new_password = forms.CharField(widget=forms.PasswordInput(), label='New Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirm Password')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("New password and confirm password must match.")

        return cleaned_data
