

from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import SetPasswordForm

User = get_user_model()

from django import forms

class AddressForm(forms.Form):
    packageId = forms.IntegerField(widget=forms.HiddenInput())
    newEndX = forms.CharField(label='New Destination X', max_length=30)
    newEndY = forms.CharField(label='New Destination Y', max_length=30)


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'phone_number']  # 只更新电子邮件和电话号码


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label="New password", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="New password confirmation", widget=forms.PasswordInput)

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={'class': 'custom-input', 'placeholder': 'Current Password'}),
        required=True
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'custom-input', 'placeholder': 'New Password'}),
        required=True
    )
    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'custom-input', 'placeholder': 'Confirm New Password'}),
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user  # Save the user instance
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Your current password is incorrect.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and new_password != confirm_password:
            raise ValidationError("New passwords must match.")
        return cleaned_data