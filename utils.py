# Utils
import datetime
from dateutil.relativedelta import relativedelta


def clean_youtube_link(youtube_link):
    if not youtube_link or youtube_link is None:
        return "https://www.youtube.com/embed/oc_vB5Xcx1o"  # default video link

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


def get_social_details(request):
    facebook_username = request.POST.get('facebook_username', "")
    facebook_link = check_http(request.POST.get('facebook_link', ""))
    twitter_username = request.POST.get('twitter_username', "")
    twitter_link = check_http(request.POST.get('twitter_link', ""))
    instagram_username = request.POST.get('instagram_username', "")
    instagram_link = check_http(request.POST.get('instagram_link', ""))
    snapchat_username = request.POST.get('snapchat_username', "")
    snapchat_link = check_http(request.POST.get('snapchat_link', ""))
    youtube_username = request.POST.get('youtube_username', "")
    youtube_link = check_http(request.POST.get('youtube_link', ""))
    twitch_username = request.POST.get('twitch_username', "")
    twitch_link = check_http(request.POST.get('twitch_link', ""))
    dribble_username = request.POST.get('dribble_username', "")
    dribble_link = check_http(request.POST.get('dribble_link', ""))
    linkedin_username = request.POST.get('linkedin_username', "")
    linkedin_link = check_http(request.POST.get('linkedin_link', ""))
    blog_username = request.POST.get('blog_username', "")
    blog_link = check_http(request.POST.get('blog_link', ""))
    website_username = request.POST.get('website_username', "")
    website_link = check_http(request.POST.get('website_link', ""))
    merchandise_username = request.POST.get('merchandise_username', "")
    merchandise_link = check_http(request.POST.get('merchandise_link', ""))
    github_username = request.POST.get('github_username', "")
    github_link = check_http(request.POST.get('github_link', ""))
    other_username = request.POST.get('other_username', "")
    other_link = check_http(request.POST.get('other_link', ""))

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
                      "twitch_details": {"twitch_username": twitch_username,
                                         "twitch_link": twitch_link},
                      "dribble_details": {"dribble_username": dribble_username,
                                          "dribble_link": dribble_link},
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


def check_http(url):
    url = url.strip()
    if url is None:
        return ""
    if url.startswith('www.'):
        return "http://" + url
    return url


# def calculate_addons(amount):
#     addons = []
#     addon1_quantity = 0
#     addon10_quantity = 0
#     addon100_quantity = 0
#     addon1000_quantity = 0
#
#     if 10 <= amount <= 99:
#         addon1_quantity = amount % 10
#         addon10_quantity = amount // 10 - 1
#     elif 100 <= amount <= 999:
#         addon1_quantity = amount % 100 % 10
#         addon10_quantity = amount % 100 // 10
#         addon100_quantity = amount // 100 - 1
#     elif 1000 <= amount <= 9999:
#         addon1_quantity = amount % 1000 % 100 % 10
#         addon10_quantity = amount % 1000 % 100 // 10
#         addon100_quantity = amount % 1000 // 100
#         addon1000_quantity = amount // 1000 - 1
#     else:
#         return addons
#
#     if addon1_quantity > 0:
#         addons.append({"addon_code": "addon1", "quantity": addon1_quantity})
#     if addon10_quantity > 0:
#         addons.append({"addon_code": "addon10", "quantity": addon10_quantity})
#     if addon100_quantity > 0:
#         addons.append({"addon_code": "addon100", "quantity": addon100_quantity})
#     if addon1000_quantity > 0:
#         addons.append({"addon_code": "addon1000", "quantity": addon1000_quantity})
#
#     return addons


def calculate_plan(amount):
    if 10 <= amount <= 99:
        return "club2"
    elif 100 <= amount <= 999:
        return "club3"
    elif 1000 <= amount <= 9999:
        return "club4"
    else:
        return "club2"


def is_first_day_of_month():
    today = datetime.date.today()
    first = today.replace(day=1)
    return today == first


def get_subscription_start_at():
    today = datetime.date.today()
    first_of_month = today.replace(day=1)
    first_of_next_month = first_of_month + relativedelta(months=1)
    return int(first_of_next_month.strftime("%s"))
