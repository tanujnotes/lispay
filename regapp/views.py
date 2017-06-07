from django.shortcuts import render
#from registration.backends.simple.views import RegistrationView
from django.core.mail import send_mail


#class MyRegistrationView(RegistrationView):
#    def get_success_url(self, user):
#        print(user.email)
#        print("*****************************************************")
#        send_mail('Subject here', 'Here is the message.', 'thetanuj1@gmail.com',[user.email], fail_silently=False)
#        return '/regapp/'

def index(request):
    return render(request, 'regapp/index.html', {})
