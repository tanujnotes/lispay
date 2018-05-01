import datetime
import json
from io import BytesIO

import requests
from PIL import Image, ImageOps
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Sum
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

import utils
from drfapp.serializers import UserSerializer, SubscriptionSerializer
from regapp.models import MyUser, SubsPlanModel, SubscriptionModel, DataDumpModel, PaymentModel
from userregistration.local_settings import RAZORPAY_KEY_, RAZORPAY_SECRET_

HEADERS = {'Content-Type': 'application/json;charset=UTF-8'}


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_creators(request):
    users = MyUser.objects.filter(is_creator=True)
    serializer = UserSerializer(users, many=True)
    return JsonResponse({"users": serializer.data}, safe=False)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_user(request):
    username = request.GET.get('username', '')
    users = MyUser.objects.get(username=username)
    serializer = UserSerializer(users, many=False)
    return JsonResponse(serializer.data, safe=False)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def update_user(request):
    first_name = request.POST.get('first_name', '')
    short_bio = request.POST.get('short_bio', '')
    mobile = request.POST.get('mobile', '')
    print(request.FILES)

    user = MyUser.objects.get(username=request.user.username)
    if first_name:
        user.first_name = first_name
    if short_bio:
        user.short_bio = short_bio
    if mobile:
        user.mobile = mobile
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
    serializer = UserSerializer(user, many=False)
    return JsonResponse(serializer.data, safe=False)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def update_social_details(request):
    user = MyUser.objects.get(username=request.user.username)
    user.social_links = utils.get_social_details(request)
    user.save()
    serializer = UserSerializer(user, many=False)
    return JsonResponse(serializer.data, safe=False)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def update_creator(request):
    first_name = request.POST.get('first_name', '')
    short_bio = request.POST.get('short_bio', '')
    mobile = request.POST.get('mobile', '')

    user = MyUser.objects.get(username=request.user.username)
    is_creator_string = request.POST.get('is_creator', "")
    user.is_creator = True if is_creator_string == 'true' else False
    user.category = request.POST.get('category', "")
    user.profile_description = request.POST.get('profile_description', "").strip()
    user.featured_text = request.POST.get('featured_text', "").strip()
    user.club_2_reward = request.POST.get('club_2_reward', "").strip()
    user.club_3_reward = request.POST.get('club_3_reward', "").strip()
    user.club_4_reward = request.POST.get('club_4_reward', "").strip()
    featured_video = request.POST.get('featured_video', "").strip()
    user.featured_video = utils.clean_youtube_link(featured_video)

    if first_name:
        user.first_name = first_name
    if short_bio:
        user.short_bio = short_bio
    if mobile:
        user.mobile = mobile

    if not user.first_name or not user.short_bio:  # or not user.profile_description or not user.featured_text:
        return JsonResponse(
            {'response_code': 1, 'response_message': "Please fill all the details"}, safe=False)

    user.save()
    serializer = UserSerializer(user, many=False)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def dashboard(request):
    current_month = datetime.datetime.now().month
    user = request.user

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

    active_subscribers_serializer = SubscriptionSerializer(active_subscribers, many=True)
    cancelled_subscribers_serializer = SubscriptionSerializer(subscribers_cancelled, many=True)

    return JsonResponse({'current_subscribers_count': current_subscribers_count,
                         'this_month_revenue': this_month_revenue if this_month_revenue is not None else 0,
                         'joined_this_month': joined_this_month,
                         'left_this_month': left_this_month,
                         'subscribers_active': active_subscribers_serializer.data,
                         'subscribers_cancelled': cancelled_subscribers_serializer.data,
                         }, safe=False)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def my_subscriptions(request):
    subscriptions = SubscriptionModel.objects.filter(subscriber=request.user).filter(
        status__in=['authenticated', 'active', 'pending', 'halted']).order_by('-created_at')

    subscription_serializer = SubscriptionSerializer(subscriptions, many=True)
    return JsonResponse({"subscriptions": subscription_serializer.data}, safe=False)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def subscription_authenticated(request):
    subscription_id = request.data['subscription_id']
    subscription = SubscriptionModel.objects.get(subscription_id=subscription_id)
    if subscription.status == 'created':
        subscription.status = 'authenticated'
        subscription.save()
    return JsonResponse({'response_code': 0, 'response_message': "Subscription status updated"}, safe=False)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_subscription(request):
    amount = int(request.data['amount'])
    profile_username = request.data['creator']

    # Register customer
    if not request.user.customer_id:
        url = 'https://api.razorpay.com/v1/customers'
        data = {"name": request.user.username, "email": request.user.email}
        r = requests.post(url, headers=HEADERS, data=json.dumps(data), auth=(RAZORPAY_KEY_, RAZORPAY_SECRET_))
        response = json.loads(r.text)
        if 'error' not in response:
            request.user.customer_id = response['id']
            request.user.save()
            dump = DataDumpModel(event_type="customer_registered", data=response)
            dump.save()
        else:
            print(response['error'])
            return JsonResponse({'response_code': 1,
                                 'response_message': response['error']['description']},
                                safe=False)

    # Create the plan
    url = "https://api.razorpay.com/v1/plans"
    data = {'period': 'monthly',
            'interval': 1,
            'item': {'name': 'plan_%s_%s_%s' % (str(amount), profile_username, request.user.username),
                     'amount': amount * 100,  # razorpay accepts amount in paise
                     'currency': 'INR'
                     },
            'notes': {
                "creator": profile_username,
                "subscriber": request.user.username
            }
            }
    r = requests.post(url, headers=HEADERS, data=json.dumps(data), auth=(RAZORPAY_KEY_, RAZORPAY_SECRET_))
    response = json.loads(r.text)
    # Save the plan
    if 'error' not in response:
        plan_id = response['id']
        subscriber_value = MyUser.objects.get(username=response['notes']['subscriber'])
        creator_value = MyUser.objects.get(username=response['notes']['creator'])
        plan = SubsPlanModel(plan_id=plan_id,
                             name=response['item']['name'],
                             description=response['item']['description'],
                             subscriber=subscriber_value,
                             creator=creator_value,
                             amount=int(response['item']['amount'] // 100),
                             interval=int(response['interval']),
                             period=response['period'],
                             currency=response['item']['currency'],
                             notes=response['notes'])
        plan.save()
        dump = DataDumpModel(event_type="subscription_plan_created", data=response)
        dump.save()
    else:
        return JsonResponse({'error': response['error']['description']}, safe=False)

    # Create the subscription payload
    url = "https://api.razorpay.com/v1/subscriptions"
    subs_data = {
        "plan_id": plan_id,
        "customer_id": request.user.customer_id,
        "customer_notify": 0,
        "total_count": 120,
        "start_at": utils.get_subscription_start_at(),
        "notes": {
            "creator": profile_username,
            "subscriber": request.user.username
        },
        "addons": [
            {
                "item": {
                    "name": "First Payment",
                    "amount": amount * 100,  # razorpay accepts amount in paise
                    "currency": "INR"
                }
            }

        ]
    }
    # Request to create subscription
    r = requests.post(url, headers=HEADERS, data=json.dumps(subs_data), auth=(RAZORPAY_KEY_, RAZORPAY_SECRET_))
    response = json.loads(r.text)

    # Save the subscription details
    if 'error' not in response:
        if not request.user.customer_id and response['customer_id'] is not None:
            request.user.customer_id = response['customer_id']
            request.user.save()

        plan = SubsPlanModel.objects.get(plan_id=response['plan_id'])
        subscription_id = response['id']
        subscription_start_at = datetime.datetime.fromtimestamp(response['start_at'])

        # Get the custom fields from subscription response
        subscriber_value = MyUser.objects.get(username=response['notes']['subscriber'])
        creator_value = MyUser.objects.get(username=response['notes']['creator'])

        # Save subscription details in database
        s = SubscriptionModel(subscription_id=subscription_id,
                              plan=plan,
                              subscriber=subscriber_value,
                              creator=creator_value,
                              status=response['status'],
                              subs_channel="razorpay",
                              amount=plan.amount,
                              start_at=subscription_start_at,
                              paid_count=response['paid_count'],
                              notes=response['notes'])
        s.save()
        dump = DataDumpModel(event_type="subscription_created", data=response)
        dump.save()
        return JsonResponse({'response_code': 0,
                             'response_message': "Subscription successful!",
                             'subscription_id': subscription_id,
                             'subscription_start_at': subscription_start_at,
                             'amount': amount
                             }, safe=False)

    else:
        print(response['error'])
        return JsonResponse(
            {'response_code': 1, 'response_message': response['error']['description']}, safe=False)
