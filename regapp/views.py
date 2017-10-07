import ast, utils, json, requests, datetime
from io import BytesIO
from urllib import parse
from django.shortcuts import render, redirect
from regapp.models import MyUser, SubsPlanModel, SubscriptionModel, DataDumpModel, TransactionModel, CATEGORY_CHOICES
from regapp.forms import UpdateProfileForm
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.template.defaulttags import register
from PIL import Image, ImageOps
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.postgres.search import SearchVector
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

RAZORPAY_KEY = "rzp_test_2pcIy5sW4v0mmP"
RAZORPAY_SECRET = "s9CeVjfADlnoRe1fMa22fPCe"
HEADERS = {'Content-Type': 'application/json;charset=UTF-8'}


@csrf_exempt
@require_POST
def webhook(request):
    binary_response = request.body
    response = parse.unquote(binary_response.decode("utf-8"))
    jsondata = json.loads(response[8:])
    print("==============================================================================================")
    print(jsondata)
    event_type = jsondata['event_type']
    dump = DataDumpModel(event_type=event_type, data=jsondata)
    dump.save()
    if event_type == 'invoice_notification':
        invoice_id = jsondata['data']['invoice']['invoice_id']
        subscription_id = jsondata['data']['invoice']['subscriptions'][0]['subscription_id']
        transaction_id = jsondata['data']['invoice']['payments'][0]['payment_id']
        transaction_type = jsondata['data']['invoice']['transaction_type']
        transaction_status = jsondata['data']['invoice']['status']
        subscriber_username = jsondata['data']['invoice']['custom_field_hash']['cf_subsciber']
        subscriber = MyUser.objects.get(username=subscriber_username)
        creator_username = jsondata['data']['invoice']['custom_field_hash']['cf_creator']
        creator = MyUser.objects.get(username=creator_username)
        tax = jsondata['data']['invoice']['tax_total']
        total_amount = jsondata['data']['invoice']['total']
        currency = jsondata['data']['invoice']['currency_code']
        message = jsondata['data']['invoice']['notes']

        transaction = TransactionModel(invoice_id=invoice_id, subscription_id=subscription_id,
                                       transaction_id=transaction_id, transaction_type=transaction_type,
                                       transaction_status=transaction_status, subscriber=subscriber, creator=creator,
                                       tax=tax, total_amount=total_amount, currency=currency, message=message)
        transaction.save()

    return HttpResponse(status=200)


def index(request):
    user1 = MyUser.objects.get(username="user1")
    user2 = MyUser.objects.get(username="user2")
    user3 = MyUser.objects.get(username="user3")
    featured_list = {'user1': user1, 'user2': user2, 'user3': user3}
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
    plan_id = ""
    subscription_id = ""
    amount = request.session['amount']
    user = MyUser.objects.get(username=creator)
    if not user.is_creator:
        return render(request, 'regapp/profile.html',
                      {'user_profile': user, 'message': "You can pledge to creator accounts only."})
    if not amount or amount is None:
        return render(request, 'regapp/profile.html',
                      {'user_profile': user, 'message': "Please enter an amount and continue"})

    # Register customer
    if not request.user.customer_id:
        url = 'https://api.razorpay.com/v1/customers'
        data = {"name": request.user.username, "email": request.user.email}
        r = requests.post(url, headers=HEADERS, data=json.dumps(data), auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
        response = json.loads(r.text)
        if 'error' not in response:
            request.user.customer_id = response['id']
            request.user.save()
            dump = DataDumpModel(event_type="customer_registered", data=response)
            dump.save()

    # Create the plan
    url = "https://api.razorpay.com/v1/plans"
    data = {'period': 'monthly',
            'interval': 1,
            'item': {'name': 'plan_' + str(amount),
                     'amount': amount * 100,  # razorpay accepts amount in paise
                     'currency': 'INR'
                     },
            'notes': {
                "creator": creator,
                "subscriber": request.user.username
            }
            }
    r = requests.post(url, headers=HEADERS, data=json.dumps(data), auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
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

    # Create the subscription
    url = "https://api.razorpay.com/v1/subscriptions"
    subs_data = {
        "plan_id": plan_id,
        "customer_id": request.user.customer_id,
        "customer_notify": 0,
        "total_count": 6,
        "start_at": utils.get_subscription_start_at(),
        "notes": {
            "creator": creator,
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

    r = requests.post(url, headers=HEADERS, data=json.dumps(subs_data), auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
    response = json.loads(r.text)
    if 'error' not in response:
        if not request.user.customer_id and response['customer_id'] is not None:
            request.user.customer_id = response['customer_id']
            request.user.save()

        # Get the custom fields from subscription response
        subscriber_value = MyUser.objects.get(username=response['notes']['subscriber'])
        creator_value = MyUser.objects.get(username=response['notes']['creator'])
        plan = SubsPlanModel.objects.get(plan_id=response['plan_id'])
        subscription_id = response['id']
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
        request.session['creator_username'] = creator
        # return render(request, 'regapp/checkout.html',
        #               {'amount': request.session['amount'], 'creator': creator, "error": response['message']})

    return render(request, 'regapp/checkout.html',
                  {'amount': request.session['amount'], 'creator': creator, 'subscription_id': subscription_id})


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
        return HttpResponseRedirect('/regapp/')

    if request.method == 'POST':
        # Cancel subscription
        subscription_id = request.POST.get('subscription_id', "").strip()
        if subscription_id:
            url = "https://api.razorpay.com/v1/subscriptions/" + subscription_id + "/cancel"
            r = requests.post(url, headers=HEADERS, auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
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
                              {'user_profile': user_profile, 'error': "Subscription amount must not be less than 10"})
            elif amount > 9999:
                return render(request, 'regapp/profile.html',
                              {'user_profile': user_profile, 'error': "Subscription amount must be less than 1000"})
            else:
                request.session['amount'] = amount
                return HttpResponseRedirect('/regapp/' + profile_username + '/checkout/')
        except:
            return render(request, 'regapp/profile.html',
                          {'user_profile': user_profile, 'error': "Please enter a valid amount"})

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
def update_profile(request):
    error = ""
    user = request.user
    form = UpdateProfileForm(request.POST or None,
                             initial={'full_name': user.full_name,
                                      'short_bio': user.short_bio,
                                      'profile_description': user.profile_description,
                                      'category': user.category,
                                      'featured_video': user.featured_video,
                                      'featured_text': user.featured_text,
                                      'social_links': user.social_links,
                                      'is_creator': user.is_creator})

    if request.method == 'POST':
        if form.is_valid():
            user.full_name = request.POST['full_name']
            user.short_bio = request.POST['short_bio']
            featured_video = request.POST.get('featured_video', "")
            user.featured_video = clean_youtube_link(featured_video)
            user.featured_text = request.POST.get('featured_text', "")
            user.profile_description = request.POST.get('profile_description', "")
            user.category = request.POST.get('category', "")
            user.is_creator = ("is_creator" in request.POST)
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
            return HttpResponseRedirect('/regapp/%s/' % user.username)
        else:
            error = "Please fill all the required fields!"
            print(form.errors)

    context = {
        "form": form,
        "categories": CATEGORY_CHOICES,
        "errors": error
    }
    return render(request, 'regapp/update_profile.html', context)


def get_social_details(request):
    facebook_username = request.POST.get('facebook_username', "")
    facebook_link = request.POST.get('facebook_link', "")
    twitter_username = request.POST.get('twitter_username', "")
    twitter_link = request.POST.get('twitter_link', "")
    instagram_username = request.POST.get('instagram_username', "")
    instagram_link = request.POST.get('instagram_link', "")
    snapchat_username = request.POST.get('snapchat_username', "")
    snapchat_link = request.POST.get('snapchat_link', "")
    youtube_username = request.POST.get('youtube_username', "")
    youtube_link = request.POST.get('youtube_link', "")
    googleplus_username = request.POST.get('googleplus_username', "")
    googleplus_link = request.POST.get('googleplus_link', "")
    linkedin_username = request.POST.get('linkedin_username', "")
    linkedin_link = request.POST.get('linkedin_link', "")
    blog_username = request.POST.get('blog_username', "")
    blog_link = request.POST.get('blog_link', "")
    website_username = request.POST.get('website_username', "")
    website_link = request.POST.get('website_link', "")
    merchandise_username = request.POST.get('merchandise_username', "")
    merchandise_link = request.POST.get('merchandise_link', "")
    github_username = request.POST.get('github_username', "")
    github_link = request.POST.get('github_link', "")
    other_username = request.POST.get('other_username', "")
    other_link = request.POST.get('other_link', "")

    social_details = {"facebook_details": {"facebook_username": facebook_username,
                                           "facebook_link": facebook_link},
                      "twitter_details": {"twitter_username": twitter_username,
                                          "twitter_link": twitter_link},
                      "instagram_details": {"instagram_username": instagram_username,
                                            "instagram_link": instagram_link},
                      "snapchat_details": {"snapchat_username": snapchat_username,
                                           "snapchat_link": snapchat_link},
                      "youtube_details": {"youtube_username": youtube_username,
                                          "youtube_link": youtube_link},
                      "googleplus_details": {"googleplus_username": googleplus_username,
                                             "googleplus_link": googleplus_link},
                      "linkedin_details": {"linkedin_username": linkedin_username,
                                           "linkedin_link": linkedin_link},
                      "blog_details": {"blog_username": blog_username,
                                       "blog_link": blog_link},
                      "website_details": {"website_username": website_username,
                                          "website_link": website_link},
                      "merchandise_details": {"merchandise_username": merchandise_username,
                                              "merchandise_link": merchandise_link},
                      "github_details": {"github_username": github_username,
                                         "github_link": github_link},
                      "other_details": {"other_username": other_username,
                                        "other_link": other_link}
                      }
    return social_details


@login_required
def login_redirect(request):
    if request.user.full_name:
        url = '/regapp/%s/' % request.user.username
    else:
        url = '/dash/update_profile/'
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
