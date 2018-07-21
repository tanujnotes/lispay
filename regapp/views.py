import ast
import datetime
import hashlib
import hmac
import json
import logging
from urllib import parse

import requests
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.template.defaulttags import register
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import utils
from regapp.forms import UpdateProfileForm
from regapp.models import MyUser, SubsPlanModel, SubscriptionModel, DataDumpModel, PaymentModel
from userregistration.local_settings import RAZORPAY_KEY_, RAZORPAY_SECRET_

HEADERS = {'Content-Type': 'application/json;charset=UTF-8'}

logger = logging.getLogger(__name__)

CATEGORY_BACKGROUND = {
    "ALL": 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1652&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "MUSIC": 'https://images.unsplash.com/photo-1445985543470-41fba5c3144a?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "MEDIA": 'https://images.unsplash.com/photo-1497015289639-54688650d173?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "GAMES": 'https://images.unsplash.com/photo-1489850846882-35ef10a4b480?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "COMEDY": 'https://images.unsplash.com/photo-1472162072942-cd5147eb3902?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "WRITING": 'https://images.unsplash.com/photo-1462642109801-4ac2971a3a51?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "PODCASTS": 'https://images.unsplash.com/photo-1478737270239-2f02b77fc618?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "EDUCATION": 'https://images.unsplash.com/photo-1462536943532-57a629f6cc60?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "PHOTOGRAPHY": 'https://images.unsplash.com/photo-1495558761807-e324eceafffa?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "PROGRAMMING": 'https://images.unsplash.com/photo-1503444200347-fa86187a2797?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "CRAFTS AND DIY": 'https://images.unsplash.com/photo-1500445040738-cb9363fe7fb5?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "VIDEOS AND FILMS": 'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "DANCE AND THEATER": 'https://images.unsplash.com/photo-1479813183133-f2e9b38ed6c4?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "DRAWING AND PAINTING": 'https://images.unsplash.com/photo-1456086272160-b28b0645b729?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "SCIENCE AND TECHNOLOGY": 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=1650&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
    "OTHERS": 'https://images.unsplash.com/photo-1452421822248-d4c2b47f0c81?auto=format&fit=crop&w=1200&q=80&ixid=dW5zcGxhc2guY29tOzs7Ozs%3D',
}


@csrf_exempt
@require_POST
def webhook(request):
    try:
        binary_response = request.body
        response = parse.unquote(binary_response.decode("utf-8"))
        jsondata = json.loads(response)
        logger.info(jsondata)
        event_type = jsondata.get('event', 'event_not_found')
        if event_type == "event_not_found" or not DataDumpModel.objects.filter(data=jsondata).exists():
            dump = DataDumpModel(event_type=event_type, data=jsondata)
            dump.save()
        else:
            return HttpResponse(status=200)
    except:
        return redirect(index)

    if event_type == 'event_not_found' or 'payload' not in jsondata or 'contains' not in jsondata:
        return HttpResponse(200)

    if event_type == 'invoice.paid':
        invoice_entity = jsondata['payload']['invoice']['entity']
        payment_entity = jsondata['payload']['payment']['entity']
        subscription_id = invoice_entity['subscription_id']
        payment_id = payment_entity['id']
        subscription = SubscriptionModel.objects.get(subscription_id=subscription_id)
        if subscription.status == 'created':
            subscription.status = 'authenticated'
            subscription.save()

        if PaymentModel.objects.filter(payment_id=payment_id).exists():
            payment = PaymentModel.objects.get(payment_id=payment_id)
            if payment.payment_status != "captured":
                payment.payment_status = payment_entity['status']
            if not payment.tax or not payment.fee:
                payment.tax = payment_entity['tax'] / 100 if payment_entity['tax'] is not None else None
                payment.fee = payment_entity['fee'] / 100 if payment_entity['fee'] is not None else None
            payment.save()

        else:
            payment = PaymentModel(invoice_id=payment_entity['invoice_id'],
                                   subscription_id=subscription_id,
                                   payment_id=payment_id,
                                   payment_type=payment_entity['method'],
                                   payment_status=payment_entity['status'],
                                   subscriber=subscription.subscriber,
                                   creator=subscription.creator,
                                   tax=payment_entity['tax'] / 100 if payment_entity['tax'] is not None else None,
                                   fee=payment_entity['fee'] / 100 if payment_entity['fee'] is not None else None,
                                   captured_amount=payment_entity['amount'] // 100,
                                   total_amount=payment_entity['amount'] // 100,
                                   currency=payment_entity['currency'],
                                   message=payment_entity['notes'])
            payment.save()

            if not subscription.subscriber.mobile:
                subscription.subscriber.mobile = payment_entity['contact']
                subscription.subscriber.save()

    if 'subscription' in jsondata['contains']:
        subscription_id = jsondata['payload']['subscription']['entity']['id']
        subscription = SubscriptionModel.objects.get(subscription_id=subscription_id)

        if event_type == "subscription.activated":
            if subscription.status == "created" or subscription.status == "authenticated" \
                    or subscription.status == "pending" or subscription.status == "halted":
                subscription.status = "active"
            if subscription.paid_count < jsondata['payload']['subscription']['entity']['paid_count']:
                subscription.paid_count = jsondata['payload']['subscription']['entity']['paid_count']
            subscription.save()

        elif event_type == "subscription.charged":
            if subscription.paid_count < jsondata['payload']['subscription']['entity']['paid_count']:
                subscription.paid_count = jsondata['payload']['subscription']['entity']['paid_count']
                subscription.status = "active"
            subscription.save()

            if 'payment' in jsondata['payload']:
                pay_entity = jsondata['payload']['payment']['entity']
                payment_id = pay_entity['id']
                if not PaymentModel.objects.filter(payment_id=payment_id).exists():
                    payment = PaymentModel(invoice_id=pay_entity['invoice_id'],
                                           subscription_id=subscription_id,
                                           payment_id=pay_entity['id'],
                                           payment_type=pay_entity['method'],
                                           payment_status=pay_entity['status'],
                                           subscriber=subscription.subscriber,
                                           creator=subscription.creator,
                                           tax=pay_entity['tax'] / 100 if pay_entity['tax'] is not None else None,
                                           fee=pay_entity['fee'] / 100 if pay_entity['fee'] is not None else None,
                                           captured_amount=pay_entity['amount'] // 100,
                                           total_amount=pay_entity['amount'] // 100,
                                           currency=pay_entity['currency'],
                                           message=subscription.notes)
                    payment.save()
                else:
                    payment = PaymentModel.objects.get(payment_id=payment_id)
                    if payment.payment_status != "captured":
                        payment.payment_status = pay_entity['status']
                        payment.save()

        elif event_type == "subscription.pending":
            if subscription.status not in ['halted', 'cancelled', 'completed']:
                subscription.status = "pending"
                subscription.save()

        # TODO: Handle following three events regarding what to show in Dashboard
        elif event_type == "subscription.halted":
            if subscription.status not in ['halted', 'cancelled', 'completed']:
                subscription.status = "halted"
                subscription.save()

        elif event_type == "subscription.cancelled":
            subscription.status = "cancelled"
            subscription.ended_at = datetime.datetime.now()
            subscription.save()

        elif event_type == "subscription.completed":
            subscription.status = "completed"
            subscription.ended_at = datetime.datetime.now()
            subscription.save()

    if 'payment' in jsondata['contains']:
        payment_id = jsondata['payload']['payment']['entity']['id']
        entity = jsondata['payload']['payment']['entity']
        if PaymentModel.objects.filter(payment_id=payment_id).exists():
            payment = PaymentModel.objects.get(payment_id=payment_id)
            if payment.payment_status != "captured":
                payment.payment_status = entity['status']
            if not payment.tax or not payment.fee:
                payment.tax = entity['tax'] / 100 if entity['tax'] is not None else None
                payment.fee = entity['fee'] / 100 if entity['fee'] is not None else None
            payment.save()

        elif entity['notes'] and 'subscription_id' in entity['notes']:
            notes = entity['notes']
            subscription_id = notes['subscription_id']
            if SubscriptionModel.objects.filter(subscription_id=subscription_id).exists():
                subscription = SubscriptionModel.objects.get(subscription_id=subscription_id)
                payment = PaymentModel(invoice_id=entity['invoice_id'],
                                       subscription_id=subscription_id,
                                       payment_id=entity['id'],
                                       payment_type=entity['method'],
                                       payment_status=entity['status'],
                                       subscriber=MyUser.objects.get(username=notes['subscriber']),
                                       creator=MyUser.objects.get(username=notes['creator']),
                                       tax=entity['tax'] / 100 if entity['tax'] is not None else None,
                                       fee=entity['fee'] / 100 if entity['fee'] is not None else None,
                                       captured_amount=entity['amount'] // 100,
                                       total_amount=entity['amount'] // 100,
                                       currency=entity['currency'],
                                       message=notes)
                payment.save()

                if not subscription.subscriber.mobile:
                    subscription.subscriber.mobile = entity['contact']
                    subscription.subscriber.save()

    return HttpResponse(status=200)


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('show_user_profile', args=(request.user.username,)))

    user1 = MyUser.objects.get(username="user1")
    user2 = MyUser.objects.get(username="user2")
    user3 = MyUser.objects.get(username="user3")
    featured_list = {'user1': user1, 'user2': user2, 'user3': user3}
    logger.info("Opening home page")
    return render(request, 'regapp/index.html', {'featured_list': featured_list})


def home(request):
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


def privacy(request):
    return render(request, 'regapp/privacy_policy.html', {})


def terms_of_service(request):
    return render(request, 'regapp/terms_of_service.html', {})


def thank_you(request):
    try:
        binary_response = request.body
        logger.info(binary_response)
        response = parse.unquote(binary_response.decode("utf-8"))
        dump = DataDumpModel(event_type="thank_you_event", data=response)
        dump.save()
        key_value = response.split('&')
        key_value_dict = {}
        for pair in key_value:
            pair_split = pair.split('=')
            key_value_dict[pair_split[0]] = pair_split[1]
    except:
        return redirect(index)

    subscription = SubscriptionModel.objects.filter(subscriber=request.user).latest('created_at')

    key_binary = bytes(RAZORPAY_SECRET_, 'latin-1')
    string_binary = bytes(key_value_dict['razorpay_payment_id'] + '|' + subscription.subscription_id, 'latin-1')
    digest = hmac.new(key_binary, string_binary, digestmod=hashlib.sha256).hexdigest()

    if digest == key_value_dict['razorpay_signature']:
        subscription.status = 'authenticated'
        subscription.save()
        amount = subscription.amount
        creator_username = subscription.creator.username
        creator = MyUser.objects.get(username=creator_username)
        return render(request, 'regapp/thank_you.html',
                      {"creator": creator, "amount": amount, "message": "Your subscription was successful!"})
    else:
        return render(request, 'regapp/thank_you.html', {"message": "Subscription failed!"})


@login_required
def checkout(request, creator):
    return render(request, 'regapp/checkout.html',
                  {'creator': MyUser.objects.get(username=creator),
                   'key': RAZORPAY_KEY_,
                   'amount': request.session['amount'],
                   'subscription_id': request.session['subscription_id'],
                   'subscription_start_day': request.session['subscription_start_day']})


def search(request):
    search_query = request.POST.get("search", "").strip()
    if not search_query or search_query is None:
        return redirect(index)

    try:
        dump = DataDumpModel(event_type="search_lisplay", data={'search_term': search_query})
        dump.save()
    except:
        pass

    search_results_available = True
    search_results = MyUser.objects.filter(is_creator=True).annotate(
        search=SearchVector('username', 'first_name', 'profile_description'), ).filter(search=search_query)
    if not search_results:
        search_results_available = False
        search_results = MyUser.objects.filter(is_creator=True).order_by('-created_at')[:10]

    subscriber_count = {}
    for creator in search_results:
        subscriber_count[creator.username] = SubscriptionModel.objects.filter(creator=creator).filter(
            status__in=['authenticated', 'active', 'pending']).count()

    return render(request, 'regapp/search.html', {'search_results': search_results,
                                                  'search_query': search_query,
                                                  'search_results_available': search_results_available,
                                                  'subscriber_count': subscriber_count})


def show_user_profile(request, profile_username):
    try:
        user_profile = MyUser.objects.get(username=profile_username)
    except:
        return redirect(index)

    subscribed_to = {}
    if request.user.is_authenticated() and request.user.username == profile_username:
        subscribed_to = SubscriptionModel.objects.filter(
            subscriber=MyUser.objects.get(username=request.user.username)).filter(
            status__in=['authenticated', 'active', 'pending'])

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

                subscribed_to = SubscriptionModel.objects.filter(
                    subscriber=MyUser.objects.get(username=request.user.username)).filter(
                    status__in=['authenticated', 'active', 'pending'])
                return render(request, 'regapp/profile.html',
                              {'user_profile': user_profile, 'subscribed_to': subscribed_to,
                               'message': "Your subscription was cancelled."})
            else:
                return render(request, 'regapp/profile.html',
                              {'user_profile': user_profile, 'subscribed_to': subscribed_to,
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

        if not request.user.is_authenticated():
            return HttpResponseRedirect('/accounts/signup/')

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
                              {'user_profile': user_profile, 'subscribed_to': subscribed_to,
                               'error': "Failed to create subscription. Please try again!"})

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
            return render(request, 'regapp/profile.html',
                          {'user_profile': user_profile, 'subscribed_to': subscribed_to,
                           'error': "Failed to create subscription. Please try again!"})

        # Create the subscription
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
            request.session['subscription_id'] = subscription_id
            request.session['subscription_start_day'] = subscription_start_at.day
            return HttpResponseRedirect('/' + profile_username + '/checkout/')

        else:
            return render(request, 'regapp/profile.html',
                          {'user_profile': user_profile, 'subscribed_to': subscribed_to,
                           'error': "Failed to create subscription. Please try again!"})

    return render(request, 'regapp/profile.html', {'user_profile': user_profile, 'subscribed_to': subscribed_to})


def explore_creators(request, category, page="1"):
    try:
        page = int(page)
    except:
        page = 1

    category = category.replace("-", " ").upper()
    # try:
    #     if category == "ALL":
    #         creators = MyUser.objects.filter(is_creator=True)
    #     else:
    #         creators = MyUser.objects.filter(category=category, is_creator=True)
    # except:
    #     creators = MyUser.objects.filter(is_creator=True)

    creators = MyUser.objects.filter(is_creator=True).order_by('-created_at')
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

    subscriber_count = {}
    for creator in creators:
        subscriber_count[creator.username] = SubscriptionModel.objects.filter(creator=creator).filter(
            status__in=['authenticated', 'active', 'pending']).count()

    number_of_creators = len(creators)
    half = number_of_creators // 2 if number_of_creators % 2 == 0 else (number_of_creators // 2) + 1
    creators_part_1 = creators[0:half]
    creators_part_2 = creators[half:number_of_creators]

    context = {"creators_part_1": creators_part_1, "creators_part_2": creators_part_2, "category": category,
               "page": page, "total_pages": paginator.num_pages, 'subscriber_count': subscriber_count,
               'background': CATEGORY_BACKGROUND[category]}
    return render(request, 'regapp/explore_creators.html', context)


@login_required
def welcome(request):
    error = ""
    # if request.user.first_name:
    #     return HttpResponseRedirect('/%s/' % request.user.username)

    form = UpdateProfileForm(request.POST or None, initial={'first_name': request.user.first_name})
    if request.method == 'POST':
        if form.is_valid():
            request.user.first_name = request.POST['first_name'].strip()
            request.user.save()
            if "is_creator" in request.POST:
                return HttpResponseRedirect('/creator-details/')
            else:
                return HttpResponseRedirect('/%s/' % request.user.username)
        else:
            print(form.errors)

    context = {
        "form": form,
        "errors": form.errors,
    }
    return render(request, 'regapp/welcome.html', context)


@login_required
def login_redirect(request):
    next_url = request.GET.get('next', '')

    if request.user.first_name:
        if next_url:
            url = next_url
        else:
            url = '/%s/' % request.user.username
    else:
        if next_url:
            url = '/welcome/?next=%s' % next_url
        else:
            url = '/welcome/'

    return HttpResponseRedirect(url)


@register.filter
def get_value(dictionary, key):
    try:
        dictionary = ast.literal_eval(dictionary)
    except:
        return ""
    return dictionary.get(key)


@register.filter(name='times')
def times(number):
    return range(number)  # Usage {% for i in 15|times %}  {% endfor %}


@register.filter(name='range')
def filter_range(start, end):
    return range(start, end + 1)  # Usage {% for i in 1|range:10 %}  {% endfor %}
