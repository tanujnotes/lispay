import ast, json, requests, datetime
from io import BytesIO
from urllib import parse
from django.shortcuts import render, redirect
from regapp.models import MyUser, SubscriptionModel, DataDumpModel, TransactionModel, CATEGORY_CHOICES
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

ZOHO_AUTH_TOKEN = 'Zoho-authtoken 7ec76e4d322836b915698ec30fa4a2d5'
ZOHO_ORGANIZATION_ID = '650065656'
ZOHO_CONTENT_TYPE = 'application/json;charset=UTF-8'


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


@login_required
def checkout(request, creator):
    amount = request.session['amount']
    cards_response_json = {}
    user = MyUser.objects.get(username=creator)
    if not user.is_creator:
        return render(request, 'regapp/profile.html',
                      {'user_profile': user, 'message': "You can pledge to creator accounts only."})
    if not amount or amount is None:
        return render(request, 'regapp/profile.html',
                      {'user_profile': user, 'message': "Please enter an amount and continue"})

    # Register customer to zoho
    if not request.user.customer_id:
        url = 'https://subscriptions.zoho.com/api/v1/customers'
        headers = {'Authorization': ZOHO_AUTH_TOKEN,
                   'X-com-zoho-subscriptions-organizationid': ZOHO_ORGANIZATION_ID}
        data = {"display_name": request.user.username, "email": request.user.email}

        r = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(r.text)
        if response['code'] == 0:
            request.user.customer_id = response['customer']['customer_id']
            request.user.save()

    # Get all the saved credit cards for customer from zoho
    if request.user.customer_id:
        url = 'https://subscriptions.zoho.com/api/v1/customers/' + request.user.customer_id + '/cards'
        headers = {'Authorization': ZOHO_AUTH_TOKEN,
                   'X-com-zoho-subscriptions-organizationid': ZOHO_ORGANIZATION_ID,
                   'Content-Type': ZOHO_CONTENT_TYPE}
        cards_response = requests.get(url, headers=headers)
        cards_response_json = json.loads(cards_response.text)

    if request.method == 'POST':
        card_id = request.POST.get('card_id', "")
        if not card_id:
            card_number = request.POST.get('card_number', "").strip().replace(" ", "")
            card_cvv = request.POST.get('card_cvv', "").strip()
            card_expiry = request.POST.get('card_expiry', "").strip()
            print(card_number)
            if not card_number or not card_cvv or not card_expiry:
                return render(request, 'regapp/checkout.html', {"error": "Please fill out all the card detail fields."})

            try:
                expiry_month = card_expiry.split('/')[0]
                expiry_year = card_expiry.split('/')[1]
                if int(expiry_month) < 1 or int(expiry_month) > 12:
                    return render(request, 'regapp/checkout.html',
                                  {"cards_json": cards_response_json, 'amount': request.session['amount'],
                                   "creator": creator,
                                   "error": "Invalid value of month in card expiry date. Please check."})
            except:
                return render(request, 'regapp/checkout.html',
                              {"cards_json": cards_response_json, 'amount': request.session['amount'],
                               "creator": creator, "error": "Please fill the card expiry field in correct format."})

            # Save the card details of customer on zoho
            url = 'https://subscriptions.zoho.com/api/v1/customers/' + request.user.customer_id + '/cards'
            headers = {'Authorization': ZOHO_AUTH_TOKEN,
                       'X-com-zoho-subscriptions-organizationid': ZOHO_ORGANIZATION_ID}
            data = {"card_number": card_number, "cvv_number": card_cvv, "expiry_month": expiry_month,
                    "expiry_year": "20" + expiry_year, "payment_gateway": "test_gateway", "street": "DLF Phase 3",
                    "city": "Gurugram",
                    "state": "Haryana", "zip": "122002", "country": "India"}

            r = requests.post(url, headers=headers, data=json.dumps(data))
            response = json.loads(r.text)
            if response['code'] == 0:
                card_id = response['card']['card_id']
            else:
                return render(request, 'regapp/checkout.html',
                              {"cards_json": cards_response_json, 'amount': request.session['amount'],
                               "creator": creator, "error": response['message']})

        # Create the subscription
        url = "https://subscriptions.zoho.com/api/v1/subscriptions"
        headers = {'Authorization': ZOHO_AUTH_TOKEN,
                   'X-com-zoho-subscriptions-organizationid': ZOHO_ORGANIZATION_ID,
                   'Content-Type': ZOHO_CONTENT_TYPE}
        subscription_data = {'customer_id': request.user.customer_id,
                             'card_id': card_id,
                             'auto_collect': True,
                             'plan': {'plan_code': "club2"},
                             'custom_fields': [
                                 {'label': 'subscriber', 'value': request.user.username},
                                 {'label': 'creator', 'value': creator},
                             ]
                             }
        # If customer is not registered on zoho, register while creating the subscription
        if not request.user.customer_id:
            subscription_data['customer'] = {'display_name': request.user.username, 'email': request.user.email}
        # Send subscription request
        r = requests.post(url, headers=headers, data=json.dumps(subscription_data))
        response = json.loads(r.text)

        if response['code'] == 0:
            if not request.user.customer_id:
                request.user.customer_id = response['subscription']['customer']['customer_id']
                request.user.save()

            # Get the custom fields from subscription response
            subscriber_value = ""
            creator_value = ""
            for custom_field in response['subscription']['custom_fields']:
                if custom_field['index'] == 1:
                    subscriber_value = MyUser.objects.get(username=custom_field['value'])
                else:
                    creator_value = MyUser.objects.get(username=custom_field['value'])
            # Save subscription details in database
            s = SubscriptionModel(subscription_id=response['subscription']['subscription_id'],
                                  subscriber=subscriber_value,
                                  creator=creator_value,
                                  status=response['subscription']['status'],
                                  subs_channel="zoho",
                                  amount=response['subscription']['amount'])
            s.save()
            return render(request, 'regapp/profile.html',
                          {'user_profile': user, 'message': "Your subscription was successful. Thank you!"})
        else:
            return render(request, 'regapp/checkout.html',
                          {"cards_json": cards_response_json, 'amount': request.session['amount'], 'creator': creator,
                           "error": response['message']})

    return render(request, 'regapp/checkout.html',
                  {"cards_json": cards_response_json, 'amount': request.session['amount'], 'creator': creator})


def search(request):
    search_query = request.POST.get("search", "").strip()
    if search_query is None:
        return render(request, 'regapp/index.html', {})

    search_results = MyUser.objects.annotate(
        search=SearchVector('username', 'full_name', 'profile_description'), ).filter(search=search_query)
    return render(request, 'regapp/search.html', {'search_results': search_results})


def show_user_profile(request, profile_username):
    featured_list = SubscriptionModel.objects.filter(subscriber=MyUser.objects.get(username=profile_username)) \
        .filter(status="live")
    try:
        user_profile = MyUser.objects.get(username=profile_username)
    except:
        return HttpResponseRedirect('/regapp/')

    if request.method == 'POST':
        subscription_id = request.POST.get('subscription_id', "").strip()
        if subscription_id:
            url = "https://subscriptions.zoho.com/api/v1/subscriptions/" \
                  + subscription_id \
                  + "/cancel?cancel_at_end=false"
            headers = {'Authorization': ZOHO_AUTH_TOKEN,
                       'X-com-zoho-subscriptions-organizationid': ZOHO_ORGANIZATION_ID,
                       'Content-Type': ZOHO_CONTENT_TYPE}
            r = requests.post(url, headers=headers)
            response = json.loads(r.text)
            if response['code'] == 0:
                subscription = SubscriptionModel.objects.get(subscription_id=subscription_id)
                subscription.status = "cancelled"
                subscription.ended_at = datetime.datetime.now()
                subscription.save()
                return render(request, 'regapp/profile.html',
                              {'user_profile': user_profile, 'message': "Your subscription was cancelled."})
            else:
                return render(request, 'regapp/profile.html',
                              {'user_profile': user_profile, 'error': response['message']})

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
