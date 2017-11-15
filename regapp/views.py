import ast
import datetime
import json
import requests
import utils
import logging
from urllib import parse
from userregistration.local_settings import RAZORPAY_KEY_, RAZORPAY_SECRET_

from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template.defaulttags import register
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from regapp.models import MyUser, SubsPlanModel, SubscriptionModel, DataDumpModel

HEADERS = {'Content-Type': 'application/json;charset=UTF-8'}

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def webhook(request):
    binary_response = request.body
    response = parse.unquote(binary_response.decode("utf-8"))
    jsondata = json.loads(response)
    logger.info(jsondata)
    event_type = jsondata['event']
    dump = DataDumpModel(event_type=event_type, data=jsondata)
    dump.save()
    return HttpResponse(status=200)


def index(request):
    user1 = MyUser.objects.get(username="user1")
    user2 = MyUser.objects.get(username="user2")
    user3 = MyUser.objects.get(username="user3")
    featured_list = {'user1': user1, 'user2': user2, 'user3': user3}
    logger.info("Opening home page")
    return render(request, 'regapp/index.html', {'featured_list': featured_list})


def about(request):
    return render(request, 'regapp/about.html', {})


def faq(request):
    return render(request, 'regapp/faq.html', {})


def thank_you(request):
    amount = request.session['amount']
    creator_username = request.session['creator_username']
    creator = MyUser.objects.get(username=creator_username)
    return render(request, 'regapp/thank_you.html', {"creator": creator, "amount": amount})


@login_required
def checkout(request, creator):
    return render(request, 'regapp/checkout.html',
                  {'creator': creator,
                   'amount': request.session['amount'],
                   'subscription_id': request.session['subscription_id']})


def search(request):
    search_query = request.POST.get("search", "").strip()
    if search_query is None:
        return render(request, 'regapp/index.html', {})

    search_results = MyUser.objects.annotate(
        search=SearchVector('username', 'full_name', 'profile_description'), ).filter(search=search_query)
    return render(request, 'regapp/search.html', {'search_results': search_results, "search_query": search_query})


def show_user_profile(request, profile_username):
    featured_list = SubscriptionModel.objects.filter(subscriber=MyUser.objects.get(username=profile_username)) \
        .filter(status="active")
    try:
        user_profile = MyUser.objects.get(username=profile_username)
    except:
        return HttpResponseRedirect('/')
    # return HttpResponseRedirect(reverse('reviews-year-archive', args=(year,)))

    request.session['creator_username'] = profile_username

    if request.method == 'POST':
        # Cancel subscription
        subscription_id = request.POST.get('subscription_id', "").strip()
        if subscription_id:
            url = "https://api.razorpay.com/v1/subscriptions/" + subscription_id + "/cancel"
            r = requests.post(url, headers=HEADERS, auth=(RAZORPAY_KEY_, RAZORPAY_SECRET_))
            response = json.loads(r.text)
            if 'error' not in response:
                subscription = SubscriptionModel.objects.get(subscription_id=subscription_id)
                subscription.status = "cancelled"
                subscription.ended_at = datetime.datetime.now()
                subscription.save()
                dump = DataDumpModel(event_type="subscription_cancelled", data=response)
                dump.save()
                return render(request, 'regapp/profile.html',
                              {'user_profile': user_profile, 'message': "Your subscription was cancelled."})
            else:
                return render(request, 'regapp/profile.html',
                              {'user_profile': user_profile,
                               'error': "Subscription cancellation failed. Please try again."})

        try:
            subscription_amount = request.POST.get('amount', "").strip()
            amount = int(subscription_amount)
            if amount < 10:
                return render(request, 'regapp/profile.html',
                              {'user_profile': user_profile,
                               'error': "Subscription amount must not be less than Rs. 10"})
            elif amount > 9999:
                return render(request, 'regapp/profile.html',
                              {'user_profile': user_profile,
                               'error': "Subscription amount must be more than Rs. 9999"})
            else:
                request.session['amount'] = amount
                # return HttpResponseRedirect('/' + profile_username + '/checkout/')
        except:
            return render(request, 'regapp/profile.html',
                          {'user_profile': user_profile, 'error': "Please enter a valid amount"})

        # user = MyUser.objects.get(username=creator)
        if not user_profile.is_creator:
            return render(request, 'regapp/profile.html',
                          {'user_profile': user_profile,
                           'message': "This is not a creator account. You can pledge only to creator accounts."})
        if not amount or amount is None:
            return render(request, 'regapp/profile.html',
                          {'user_profile': user_profile, 'message': "Please enter an amount and continue"})

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
                return render(request, 'regapp/profile.html',
                              {'user_profile': user_profile,
                               'error': "Failed to create subscription. Please try again!"})

        # Create the plan
        url = "https://api.razorpay.com/v1/plans"
        data = {'period': 'monthly',
                'interval': 1,
                'item': {'name': 'plan_' + str(amount),
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
        else:
            return render(request, 'regapp/profile.html',
                          {'user_profile': user_profile, 'error': "Failed to create subscription. Please try again!"})

        # Create the subscription
        url = "https://api.razorpay.com/v1/subscriptions"
        subs_data = {
            "plan_id": plan_id,
            "customer_id": request.user.customer_id,
            "customer_notify": 0,
            "total_count": 6,
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
        # Make the request to create subscription
        r = requests.post(url, headers=HEADERS, data=json.dumps(subs_data), auth=(RAZORPAY_KEY_, RAZORPAY_SECRET_))
        response = json.loads(r.text)
        # Save the subscription details
        if 'error' not in response:
            if not request.user.customer_id and response['customer_id'] is not None:
                request.user.customer_id = response['customer_id']
                request.user.save()

            plan = SubsPlanModel.objects.get(plan_id=response['plan_id'])
            subscription_id = response['id']
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
                                  notes=response['notes'])
            s.save()
            dump = DataDumpModel(event_type="subscription_created", data=response)
            dump.save()
            request.session['subscription_id'] = subscription_id
            return HttpResponseRedirect('/' + profile_username + '/checkout/')

        else:
            return render(request, 'regapp/profile.html',
                          {'user_profile': user_profile, 'error': "Failed to create subscription. Please try again!"})

    return render(request, 'regapp/profile.html', {'user_profile': user_profile, 'featured_list': featured_list})


def show_creators(request, category, page="1"):
    try:
        page = int(page)
    except:
        page = 1

    category = category.replace("-", " ").upper()
    try:
        if category == "ALL":
            creators = MyUser.objects.filter(is_creator=True)
        else:
            creators = MyUser.objects.filter(category=category, is_creator=True)
    except:
        creators = MyUser.objects.filter(is_creator=True)

    paginator = Paginator(creators, 20)
    try:
        creators = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        creators = paginator.page(page)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        page = paginator.num_pages
        creators = paginator.page(page)

    context = {"creators": creators, "category": category, "page": page, "total_pages": paginator.num_pages}
    return render(request, 'regapp/show_creators.html', context)


@login_required
def login_redirect(request):
    if request.user.full_name:
        url = '/%s/' % request.user.username
    else:
        url = '/update_profile/'
    return HttpResponseRedirect(url)


def clean_youtube_link(youtube_link):
    if "watch" in youtube_link and "&" in youtube_link:
        key_values = youtube_link.split("?")[1]
        key_values = key_values.split("&")
        for pair in key_values:
            if "v=" in pair:
                return "https://www.youtube.com/embed/" + pair.split("=")[1]
    elif "watch" in youtube_link:
        return youtube_link.replace('watch?v=', 'embed/')
    elif "youtu.be" in youtube_link:
        video_id = youtube_link.split("/")[1]
        return "https://www.youtube.com/embed/" + video_id
    else:
        return youtube_link


@register.filter
def get_item(dictionary, args):
    if args is None or dictionary is None or dictionary is "":
        return ""
    arg_list = [arg.strip() for arg in args.split(',')]
    try:
        dictionary = ast.literal_eval(dictionary)
    except:
        return None
    if dictionary.get(arg_list[0]) is None or dictionary.get(arg_list[0]).get(arg_list[1]) is None:
        return ""
    return dictionary.get(arg_list[0]).get(arg_list[1])


@register.filter(name='times')
def times(number):
    return range(number)  # Usage {% for i in 15|times %}  {% endfor %}


@register.filter(name='range')
def filter_range(start, end):
    return range(start, end + 1)  # Usage {% for i in 1|range:10 %}  {% endfor %}
