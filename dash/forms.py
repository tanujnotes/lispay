from django import forms

from regapp.models import MyUser, CATEGORY_CHOICES


class UpdateCreatorForm(forms.ModelForm):
    is_creator = forms.BooleanField(required=False)
    full_name = forms.CharField(max_length=30, required=True)
    short_bio = forms.CharField(max_length=30, required=False)
    profile_description = forms.CharField(max_length=1000, required=False, widget=forms.Textarea)
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False)
    featured_video = forms.URLField(required=False)
    featured_text = forms.CharField(required=False)
    club_2_reward = forms.CharField(max_length=200, required=False)
    club_3_reward = forms.CharField(max_length=200, required=False)
    club_4_reward = forms.CharField(max_length=200, required=False)

    class Meta:
        model = MyUser
        fields = ('is_creator', 'full_name', 'short_bio', 'profile_description', 'category', 'featured_video',
                  'featured_text', 'club_2_reward', 'club_3_reward', 'club_4_reward')
