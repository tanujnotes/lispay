from django import forms
from registration.forms import RegistrationForm

from regapp.models import MyUser


class CustomUserForm(RegistrationForm):
    class Meta:
        model = MyUser
        fields = ('username', 'email')


class UpdateProfileForm(forms.ModelForm):
    full_name = forms.CharField(max_length=30, required=True)
    short_bio = forms.CharField(max_length=50, required=False)
    profile_description = forms.CharField(max_length=1000, required=False, widget=forms.Textarea)
    featured_video = forms.URLField(required=False)
    social_links = forms.CharField(required=False)
    is_creator = forms.BooleanField(required=False)

    class Meta:
        model = MyUser
        fields = ('full_name', 'short_bio', 'profile_description', 'featured_video', 'social_links', 'is_creator')
