from django.conf.urls import url

from regapp import views

# Don't forget to add the url name in RESTRICTED_USERNAMES

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^home/$', views.home, name='home'),
    url(r'^about/$', views.about, name='about'),
    url(r'^search/$', views.search, name='search'),
    url(r'^privacy/$', views.privacy, name='privacy'),
    url(r'^welcome/$', views.welcome, name='welcome'),
    url(r'^webhook/$', views.webhook, name='webhook'),
    url(r'^checkout/$', views.checkout, name='checkout'),
    url(r'^thank-you/$', views.thank_you, name='thank_you'),
    url(r'^terms-of-service/$', views.terms_of_service, name='terms_of_service'),
    url(r'^login-redirect/$', views.login_redirect, name='login_redirect'),
    url(r'^explore-creators/(?P<category>[\w\-]+)/$', views.explore_creators, name='explore_creators'),
    url(r'^explore-creators/(?P<category>[\w\-]+)/(?P<page>[0-9]+)/$', views.explore_creators, name='explore_creators'),
    url(r'^(?P<creator>[\w\_]+)/checkout/$', views.checkout, name='checkout'),
    url(r'^(?P<profile_username>[\w\_]+)/$', views.show_user_profile, name='show_user_profile'),
]
