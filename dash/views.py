from utils import *
from io import BytesIO
from django.shortcuts import render
from regapp.forms import UpdateProfileForm
from regapp.models import CATEGORY_CHOICES
from dash.forms import UpdateCreatorForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from PIL import Image, ImageOps
from django.core.files.uploadedfile import InMemoryUploadedFile


@login_required
def dashboard(request):
    return render(request, 'dash/dashboard.html', {})


@login_required
def update_profile(request):
    error = ""
    user = request.user
    form = UpdateProfileForm(request.POST or None,
                             initial={'full_name': user.full_name,
                                      'social_links': user.social_links})

    if request.method == 'POST':
        if form.is_valid():
            user.full_name = request.POST['full_name'].strip()
            user.social_links = get_social_details(request)
            if 'picture' in request.FILES:
                picture = request.FILES['picture']
                user.picture = picture
                image = Image.open(BytesIO(request.FILES['picture'].read()))
                buffer = BytesIO()
                if image.mode != "RGB":
                    image = image.convert("RGB")

                image = ImageOps.fit(image, (200, 200), Image.ANTIALIAS)
                image.save(buffer, format='JPEG')
                im = InMemoryUploadedFile(
                    buffer,
                    None,
                    user.picture.url,
                    'image/jpeg',
                    buffer.tell(),
                    None)
                user.thumbnail = im
            user.save()
            return HttpResponseRedirect('/dash/update_profile/')
        else:
            error = "Please fill all the required fields!"
            print(form.errors)

    context = {
        "form": form,
        "errors": error,
    }
    return render(request, 'dash/update_profile.html', context)


@login_required
def creator_details(request):
    error = ""
    user = request.user
    form = UpdateCreatorForm(request.POST or None,
                             initial={'is_creator': user.is_creator,
                                      'short_bio': user.short_bio,
                                      'profile_description': user.profile_description,
                                      'category': user.category,
                                      'featured_video': user.featured_video,
                                      'featured_text': user.featured_text})

    if request.method == 'POST':
        if form.is_valid():
            user.is_creator = ("is_creator" in request.POST)
            user.category = request.POST.get('category', "")
            user.short_bio = request.POST.get('short_bio', "").strip()
            user.profile_description = request.POST.get('profile_description', "").strip()
            user.featured_text = request.POST.get('featured_text', "").strip()
            featured_video = request.POST.get('featured_video', "").strip()
            user.featured_video = clean_youtube_link(featured_video)

            if not user.short_bio or not user.profile_description or not user.featured_text:
                error = "Please fill up all the required fields!"
                context = {
                    "form": form,
                    "categories": CATEGORY_CHOICES,
                    "errors": error,
                }
                return render(request, 'dash/creator_details.html', context)

            user.save()
            return HttpResponseRedirect('/dash/creator_details/')
        else:
            error = "Please fill all the required fields!"
            print(form.errors)

    context = {
        "form": form,
        "categories": CATEGORY_CHOICES,
        "errors": error,
    }
    return render(request, 'dash/creator_details.html', context)
