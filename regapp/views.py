import ast
from io import BytesIO
from django.shortcuts import render
from regapp.models import MyUser, CATEGORY_CHOICES
from regapp.forms import UpdateProfileForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template.defaulttags import register
from PIL import Image, ImageOps
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.postgres.search import SearchVector


def index(request):
    user1 = MyUser.objects.get(username="user1")
    user2 = MyUser.objects.get(username="user2")
    user3 = MyUser.objects.get(username="user3")
    featured_list = {'user1': user1, 'user2': user2, 'user3': user3}
    return render(request, 'regapp/index.html', {'featured_list': featured_list})


def search(request):
    search_query = request.POST.get("search", "").strip()
    if search_query is None:
        return render(request, 'regapp/index.html', {})

    search_results = MyUser.objects.annotate(
        search=SearchVector('username', 'full_name', 'profile_description'), ).filter(search=search_query)
    return render(request, 'regapp/search.html', {'search_results': search_results})


def show_user_profile(request, profile_username):
    try:
        user_profile = MyUser.objects.get(username=profile_username)
    except:
        return HttpResponseRedirect('/regapp/')
    return render(request, 'regapp/profile.html', {'user_profile': user_profile})


# TODO: Pagination in creators
def show_creators(request, category):
    category = category.replace("-", " ").upper()
    try:
        if category == "ALL":
            creators = MyUser.objects.filter(is_creator=True)[:5]
        else:
            creators = MyUser.objects.filter(category=category, is_creator=True)
    except:
        creators = MyUser.objects.all()[:5]
    context = {"creators": creators}
    return render(request, 'regapp/show_creators.html', context)


@login_required
def update_profile(request):
    user = request.user
    form = UpdateProfileForm(request.POST or None,
                             initial={'full_name': user.full_name,
                                      'short_bio': user.short_bio,
                                      'profile_description': user.profile_description,
                                      'category': user.category,
                                      'featured_video': user.featured_video,
                                      'social_links': user.social_links,
                                      'is_creator': user.is_creator})

    if request.method == 'POST':
        if form.is_valid():
            user.full_name = request.POST['full_name']
            user.short_bio = request.POST['short_bio']
            featured_video = request.POST.get('featured_video', "")
            user.featured_video = featured_video.replace('watch?v=', 'embed/')
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
            print(form.errors)

    context = {
        "form": form,
        "categories": CATEGORY_CHOICES
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


@login_required
def login_redirect(request):
    if request.user.full_name and request.user.short_bio:
        url = '/regapp/%s/' % request.user.username
    else:
        url = '/regapp/update_profile/'
    return HttpResponseRedirect(url)
