from registration.forms import RegistrationForm

from regapp.models import MyUser


class CustomUserForm(RegistrationForm):
    class Meta:
        model = MyUser
        fields = ('username', 'email')

