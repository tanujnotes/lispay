from django import forms
from registration.forms import RegistrationForm

from regapp.models import MyUser, CATEGORY_CHOICES


class CustomUserForm(RegistrationForm):
    class Meta:
        model = MyUser
        fields = ('username', 'email')


class UpdateProfileForm(forms.ModelForm):
    full_name = forms.CharField(max_length=30, required=True)
    short_bio = forms.CharField(max_length=50, required=False)
    profile_description = forms.CharField(max_length=1000, required=False, widget=forms.Textarea)
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False)
    featured_video = forms.URLField(required=False)
    featured_text = forms.CharField(required=False)
    social_links = forms.CharField(required=False)
    is_creator = forms.BooleanField(required=False)

    class Meta:
        model = MyUser
        fields = ('full_name', 'short_bio', 'profile_description', 'category',
                  'featured_video', 'featured_text', 'social_links', 'is_creator')
