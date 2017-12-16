from django import forms
from registration.forms import RegistrationForm

from regapp.models import MyUser

RESTRICTED_USERNAMES = (
    'home', 'admin', 'lisplay', 'accounts', 'dashboard', 'update-profile', 'creator-details', 'faq', 'about', 'search',
    'privacy', 'welcome', 'webhook', 'checkout', 'thank-you', 'terms-of-use', 'login-redirect', 'explore-creators')


class CustomUserForm(RegistrationForm):
    class Meta:
        model = MyUser
        fields = ('username', 'email')

    def clean_username(self):
        username = self.cleaned_data.get("username").strip().lower()
        if username in RESTRICTED_USERNAMES:
            raise forms.ValidationError("Username not available")
        return username


class UpdateProfileForm(forms.ModelForm):
    full_name = forms.CharField(max_length=30, required=True)
    short_bio = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(max_length=75, required=False)
    mobile = forms.CharField(max_length=20, required=False)
    social_links = forms.CharField(required=False)
    is_creator = forms.BooleanField(required=False)

    class Meta:
        model = MyUser
        fields = ('full_name', 'short_bio', 'email', 'mobile', 'club_2_reward', 'club_3_reward', 'club_4_reward',
                  'social_links', 'is_creator')
