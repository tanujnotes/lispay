from django import forms
from regapp.models import MyUser
from registration.forms import RegistrationForm


class CustomUserForm(RegistrationForm):
    class Meta:
        model = MyUser
        fields = ('username', 'email')


class UpdateProfileForm(forms.ModelForm):
    full_name = forms.CharField(max_length=30, required=True)
    mobile = forms.CharField(max_length=20, required=False)
    social_links = forms.CharField(required=False)
    is_creator = forms.BooleanField(required=False)

    class Meta:
        model = MyUser
        fields = ('full_name', 'mobile', 'social_links', 'is_creator')
