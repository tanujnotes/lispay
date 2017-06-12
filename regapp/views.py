from django.shortcuts import render
from regapp.models import MyUser
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required


def index(request):
    creator_list = MyUser.objects.order_by('-date_joined')[:3]
    return render(request, 'regapp/index.html', {'creator_list': creator_list})


def new_index(request):
    creator_list = MyUser.objects.all()
    return render(request, 'regapp/new_profile.html', {'creator_list': creator_list})


def show_user_profile(request, profile_username):
    user_profile = MyUser.objects.get(username=profile_username)
    return render(request, 'regapp/profile.html', {'user_profile': user_profile})


def update_profile(request):
    user_profile = MyUser.objects.get(username=request.user.username)
    return render(request, 'regapp/update_profile.html', {'user_profile': user_profile})


@login_required
def login_redirect(request):
    if request.user.full_name and request.user.short_bio:
        url = '/regapp/%s/' % request.user.username
    else:
        url = '/regapp/update_profile/'
    return HttpResponseRedirect(url)
