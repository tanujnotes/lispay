import datetime
from io import BytesIO

from PIL import Image, ImageOps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.template.defaulttags import register

import utils
from dash.forms import UpdateCreatorForm
from regapp.forms import UpdateProfileForm
from regapp.models import CATEGORY_CHOICES, SubscriptionModel, MyUser, PaymentModel, DataDumpModel


@login_required
def dashboard(request):
    current_month = datetime.datetime.now().month
    user = MyUser.objects.get(username=request.user.username)

    current_subscribers_count = SubscriptionModel.objects.filter(creator=user).filter(
        status__in=['authenticated', 'active', 'pending', 'halted']).count()
    this_month_revenue = PaymentModel.objects.filter(creator=user).filter(created_at__month=current_month).filter(
        payment_status='captured').aggregate(Sum('total_amount')).get('total_amount__sum', 0.0)
    joined_this_month = SubscriptionModel.objects.filter(creator=user).filter(
        created_at__month=current_month).count()
    left_this_month = SubscriptionModel.objects.filter(creator=user).filter(ended_at__month=current_month).filter(
        status__in=['cancelled', 'completed']).count()
    active_subscribers = SubscriptionModel.objects.filter(creator=user).filter(
        status__in=['authenticated', 'active', 'pending', 'halted']).order_by('-created_at')
    subscribers_cancelled = SubscriptionModel.objects.filter(creator=user).filter(
        status='cancelled').order_by('-created_at')

    context = {
        'current_subscribers_count': current_subscribers_count,
        'this_month_revenue': this_month_revenue if this_month_revenue is not None else 0,
        'joined_this_month': joined_this_month,
        'left_this_month': left_this_month,
        'subscribers': active_subscribers,
        'subscribers_cancelled': subscribers_cancelled
    }
    return render(request, 'dash/dashboard.html', context)


@login_required
def update_profile(request):
    error = ""
    user = request.user
    form = UpdateProfileForm(request.POST or None,
                             initial={'full_name': user.full_name,
                                      'email': user.email,
                                      'mobile': user.mobile,
                                      'short_bio': user.short_bio,
                                      'social_links': user.social_links})

    if request.method == 'POST':
        if form.is_valid():
            user.full_name = request.POST.get('full_name', "").strip()
            user.short_bio = request.POST.get('short_bio', "").strip()
            user.mobile = request.POST.get('mobile', "").strip()
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
                    user.username + '_featured.jpeg',
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
                    user.username + '_profile.jpeg',
                    'image/jpeg',
                    image_buffer.tell(),
                    None)
                user.picture = im

                thumbnail_image = ImageOps.fit(image, (200, 200), Image.ANTIALIAS)
                thumbnail_image.save(thumbnail_image_buffer, format='JPEG')
                im = InMemoryUploadedFile(
                    thumbnail_image_buffer,
                    None,
                    user.username + '_thumbnail.jpeg',
                    'image/jpeg',
                    thumbnail_image_buffer.tell(),
                    None)
                user.thumbnail = im
            user.save()
            messages.add_message(request, messages.INFO, "Profile updated successfully!")
            try:
                data = serializers.serialize('json', [user, ])
                dump = DataDumpModel(event_type="profile_updated", data=data)
                dump.save()
            except:
                pass
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
                                      'featured_video': user.featured_video if user.featured_video != "https://www.youtube.com/embed/oc_vB5Xcx1o" else "",
                                      'featured_text': user.featured_text,
                                      'club_2_reward': user.club_2_reward,
                                      'club_3_reward': user.club_3_reward,
                                      'club_4_reward': user.club_4_reward})

    if request.method == 'POST':
        if form.is_valid():
            was_creator_already = user.is_creator

            user.is_creator = ("is_creator" in request.POST)
            user.category = request.POST.get('category', "")
            user.full_name = request.POST.get('full_name', "").strip()
            user.short_bio = request.POST.get('short_bio', "").strip()
            user.profile_description = request.POST.get('profile_description', "").strip()
            user.featured_text = request.POST.get('featured_text', "").strip()
            user.club_2_reward = request.POST.get('club_2_reward', "").strip()
            user.club_3_reward = request.POST.get('club_3_reward', "").strip()
            user.club_4_reward = request.POST.get('club_4_reward', "").strip()
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
            if was_creator_already:
                message = "Creator details updated successfully!"
            else:
                message = "Congratulations! Your creator page is active now.\n" \
                          "You can also set rewards for your supporters (scroll down)."
            context = {
                "form": form,
                "categories": CATEGORY_CHOICES,
                "message": message,
            }
            try:
                data = serializers.serialize('json', [user, ])
                dump = DataDumpModel(event_type="creator_details_updated", data=data)
                dump.save()
            except:
                pass
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


@register.filter
def get_total_payment(monthly_amount, paid_count):
    return monthly_amount * (paid_count + 1)
