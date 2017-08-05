from django import forms
from registration.forms import RegistrationForm

from regapp.models import MyUser, CATEGORY_CHOICES


class CustomUserForm(RegistrationForm):
    class Meta:
        model = MyUser
        fields = ('username', 'email')


class UpdateProfileForm(forms.ModelForm):
    full_name = forms.CharField(max_length=30, required=True)
    social_links = forms.CharField(required=False)
    is_creator = forms.BooleanField(required=False)

    class Meta:
        model = MyUser
        fields = ('full_name', 'social_links', 'is_creator')
