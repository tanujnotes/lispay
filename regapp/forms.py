from django import forms

from regapp.models import MyUser


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
