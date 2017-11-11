import datetime
import utils
from io import BytesIO

from PIL import Image, ImageOps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from dash.forms import UpdateCreatorForm
from regapp.forms import UpdateProfileForm
from regapp.models import CATEGORY_CHOICES, SubscriptionModel, MyUser


@login_required
def dashboard(request):
    current_month = datetime.datetime.now().month
    user = MyUser.objects.get(username=request.user.username)
    current_subscribers_count = SubscriptionModel.objects.filter(
        creator=user).filter(
        status="live").count()
    last_month_revenue = 0  # TODO: Implement a transaction table
    joined_this_month = SubscriptionModel.objects.filter(creator=user).filter(
        created_at__month=current_month).count()
    left_this_month = SubscriptionModel.objects.filter(creator=user).filter(
        updated_at__month=current_month).filter(status="cancelled").count()
    subscribers = SubscriptionModel.objects.filter(creator=user).filter(status="live")

    context = {
        'current_subscribers_count': current_subscribers_count,
        'last_month_revenue': last_month_revenue,
        'joined_this_month': joined_this_month,
        'left_this_month': left_this_month,
        'subscribers': subscribers
    }
    return render(request, 'dash/dashboard.html', context)


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
            user.social_links = utils.get_social_details(request)
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
                user.featured_image = featured_image
                image = Image.open(BytesIO(request.FILES['featured_image'].read()))
                image_buffer = BytesIO()
                if image.mode != "RGB":
                    image = image.convert("RGB")

                cover_image = ImageOps.fit(image, (1000, 500), Image.ANTIALIAS)
                cover_image.save(image_buffer, format='JPEG')
                im = InMemoryUploadedFile(
                    image_buffer,
                    None,
                    user.featured_image.url,
                    'image/jpeg',
                    image_buffer.tell(),
                    None)
                user.featured_image = im

            if 'picture' in request.FILES:
                picture = request.FILES['picture']
                user.picture = picture
                image = Image.open(BytesIO(request.FILES['picture'].read()))
                image_buffer = BytesIO()
                thumbnail_image_buffer = BytesIO()
                if image.mode != "RGB":
                    image = image.convert("RGB")

                profile_image = ImageOps.fit(image, (500, 500), Image.ANTIALIAS)
                profile_image.save(image_buffer, format='JPEG')
                im = InMemoryUploadedFile(
                    image_buffer,
                    None,
                    user.picture.url,
                    'image/jpeg',
                    image_buffer.tell(),
                    None)
                user.picture = im

                thumbnail_image = ImageOps.fit(image, (200, 200), Image.ANTIALIAS)
                thumbnail_image.save(thumbnail_image_buffer, format='JPEG')
                im = InMemoryUploadedFile(
                    thumbnail_image_buffer,
                    None,
                    user.picture.url,
                    'image/jpeg',
                    thumbnail_image_buffer.tell(),
                    None)
                user.thumbnail = im
            user.save()
            messages.add_message(request, messages.INFO, "Profile updated successfully!")
            return redirect(update_profile)
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
                                      'full_name': user.full_name,
                                      'short_bio': user.short_bio,
                                      'profile_description': user.profile_description,
                                      'category': user.category,
                                      'featured_video': user.featured_video,
                                      'featured_text': user.featured_text})

    if request.method == 'POST':
        if form.is_valid():
            user.is_creator = ("is_creator" in request.POST)
            user.category = request.POST.get('category', "")
            user.full_name = request.POST.get('full_name', "").strip()
            user.short_bio = request.POST.get('short_bio', "").strip()
            user.profile_description = request.POST.get('profile_description', "").strip()
            user.featured_text = request.POST.get('featured_text', "").strip()
            featured_video = request.POST.get('featured_video', "").strip()
            user.featured_video = utils.clean_youtube_link(featured_video)

            if not user.full_name or not user.short_bio or not user.profile_description or not user.featured_text:
                error = "Please fill up all the required fields!"
                context = {
                    "form": form,
                    "categories": CATEGORY_CHOICES,
                    "errors": error,
                }
                return render(request, 'dash/creator_details.html', context)

            user.save()
            message = "Creator details updated successfully!"
            context = {
                "form": form,
                "categories": CATEGORY_CHOICES,
                "message": message,
            }
            return render(request, 'dash/creator_details.html', context)
        else:
            error = "Invalid values in form!"
            for field, errors in form.errors.items():
                print('Field: {} Errors: {}'.format(field, ','.join(errors)))

    context = {
        "form": form,
        "categories": CATEGORY_CHOICES,
        "errors": error,
    }
    return render(request, 'dash/creator_details.html', context)
