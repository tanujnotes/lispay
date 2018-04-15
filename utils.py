# Utils
import datetime

from dateutil.relativedelta import relativedelta


def clean_youtube_link(youtube_link):
    try:
        if not youtube_link or youtube_link is None:
            return "https://www.youtube.com/embed/caxNXMpQND4"  # default video link
        if "youtube.com" not in youtube_link and "youtu.be" not in youtube_link:
            return "https://www.youtube.com/embed/caxNXMpQND4"  # default video link

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
    except:
        return "https://www.youtube.com/embed/caxNXMpQND4"  # default video link


def get_social_details(request):
    facebook_link = check_http(request.POST.get('facebook_link', ""))
    twitter_link = check_http(request.POST.get('twitter_link', ""))
    instagram_link = check_http(request.POST.get('instagram_link', ""))
    snapchat_link = check_http(request.POST.get('snapchat_link', ""))
    youtube_link = check_http(request.POST.get('youtube_link', ""))
    soundcloud_link = check_http(request.POST.get('soundcloud_link', ""))
    twitch_link = check_http(request.POST.get('twitch_link', ""))
    dribble_link = check_http(request.POST.get('dribble_link', ""))
    linkedin_link = check_http(request.POST.get('linkedin_link', ""))
    blog_link = check_http(request.POST.get('blog_link', ""))
    website_link = check_http(request.POST.get('website_link', ""))
    merchandise_link = check_http(request.POST.get('merchandise_link', ""))
    github_link = check_http(request.POST.get('github_link', ""))
    playstore_link = check_http(request.POST.get('playstore_link', ""))
    appstore_link = check_http(request.POST.get('appstore_link', ""))
    other_link = check_http(request.POST.get('other_link', ""))

    social_details = {
        "facebook_link": facebook_link,
        "twitter_link": twitter_link,
        "instagram_link": instagram_link,
        "snapchat_link": snapchat_link,
        "youtube_link": youtube_link,
        "soundcloud_link": soundcloud_link,
        "twitch_link": twitch_link,
        "dribble_link": dribble_link,
        "linkedin_link": linkedin_link,
        "blog_link": blog_link,
        "website_link": website_link,
        "merchandise_link": merchandise_link,
        "github_link": github_link,
        "playstore_link": playstore_link,
        "appstore_link": appstore_link,
        "other_link": other_link
    }
    return social_details


def check_http(url):
    url = url.strip()
    if url is None:
        return ""
    if url.startswith('www.'):
        return "http://" + url
    return url


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


# Recurring payment starts at either 1st or 15th of each month
def get_subscription_start_at():
    today = datetime.date.today()
    if today.day <= 15:
        payment_day = today.replace(day=1)
    else:
        payment_day = today.replace(day=15)

    payment_start_date = payment_day + relativedelta(months=1)
    return int(payment_start_date.strftime("%s"))
