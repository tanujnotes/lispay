from django.shortcuts import render
from regapp.models import MyUser


def index(request):
    creator_list = MyUser.objects.order_by('-date_joined')[:3]
    return render(request, 'regapp/index.html', {'creator_list': creator_list})


def new_index(request):
    creator_list = MyUser.objects.all()
    return render(request, 'regapp/new_profile.html', {'creator_list': creator_list})


def show_user_profile(request, profile_username):
    user_profile = MyUser.objects.get(username=profile_username)
    return render(request, 'regapp/profile.html', {'user_profile': user_profile})