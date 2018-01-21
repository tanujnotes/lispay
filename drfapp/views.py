import datetime
import json

import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

import utils
from drfapp.serializers import UserSerializer
from regapp.models import MyUser, SubsPlanModel, SubscriptionModel, DataDumpModel
from userregistration.local_settings import RAZORPAY_KEY_, RAZORPAY_SECRET_

HEADERS = {'Content-Type': 'application/json;charset=UTF-8'}


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_creators(request):
    users = MyUser.objects.all()
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
    full_name = request.POST.get('full_name', '')
    user = MyUser.objects.get(username=request.user.username)
    user.full_name = full_name
    user.save()
    serializer = UserSerializer(user, many=False)
    return JsonResponse(serializer.data, safe=False)


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
