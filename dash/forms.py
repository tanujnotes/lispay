from django import forms
from regapp.models import MyUser, CATEGORY_CHOICES


class UpdateCreatorForm(forms.ModelForm):
    is_creator = forms.BooleanField(required=False)
    short_bio = forms.CharField(max_length=50, required=False)
    profile_description = forms.CharField(max_length=1000, required=False, widget=forms.Textarea)
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False)
    featured_video = forms.URLField(required=False)
    featured_text = forms.CharField(required=False)

    class Meta:
        model = MyUser
        fields = ('is_creator', 'short_bio', 'profile_description', 'category', 'featured_video', 'featured_text')
