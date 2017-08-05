import json
from utils import *
from io import BytesIO
from django.shortcuts import render
from regapp.forms import UpdateProfileForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from PIL import Image, ImageOps
from django.core.files.uploadedfile import InMemoryUploadedFile


def dashboard(request):
    return render(request, 'dash/dashboard.html', {})


# @login_required
def update_profile(request):
    error = ""
    user = request.user
    form = UpdateProfileForm(request.POST or None,
                             initial={'full_name': user.full_name,
                                      'social_links': user.social_links})

    if request.method == 'POST':
        if form.is_valid():
            user.full_name = request.POST['full_name']
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
