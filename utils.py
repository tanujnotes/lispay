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
