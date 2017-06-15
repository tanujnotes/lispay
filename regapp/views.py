from django.shortcuts import render
from regapp.models import MyUser
from regapp.forms import UpdateProfileForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
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


@login_required
def update_profile(request):
    user = request.user
    form = UpdateProfileForm(request.POST or None,
                             initial={'full_name': user.full_name,
                                      'short_bio': user.short_bio,
                                      'profile_description': user.profile_description,
                                      'featured_video': user.featured_video,
                                      'social_links': user.social_links,
                                      'is_creator': user.is_creator})

    if request.method == 'POST':
        if form.is_valid():
            user.full_name = request.POST['full_name']
            user.short_bio = request.POST['short_bio']
            user.featured_video = request.POST.get('featured_video', "")
            user.profile_description = request.POST.get('profile_description', "")
            user.is_creator = ("is_creator" in request.POST)

            user.save()
            return HttpResponseRedirect('regapp/%s/' % user.username)
        else:
            print(form.errors)

    context = {
        "form": form
    }
    return render(request, 'regapp/update_profile.html', context)


@login_required
def login_redirect(request):
    if request.user.full_name and request.user.short_bio:
        url = '/regapp/%s/' % request.user.username
    else:
        url = '/regapp/update_profile/'
    return HttpResponseRedirect(url)
