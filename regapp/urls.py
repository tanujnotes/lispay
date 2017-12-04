from django.conf.urls import url
from regapp import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^about/$', views.about, name='about'),
    url(r'^search/$', views.search, name='search'),
    url(r'^privacy/$', views.privacy, name='privacy'),
    url(r'^welcome/$', views.welcome, name='welcome'),
    url(r'^webhook/$', views.webhook, name='webhook'),
    url(r'^checkout/$', views.checkout, name='checkout'),
    url(r'^thank-you/$', views.thank_you, name='thank_you'),
    url(r'^login-redirect/$', views.login_redirect, name='login_redirect'),
    url(r'^explore-creators/(?P<category>[\w\-]+)/$', views.explore_creators, name='explore_creators'),
    url(r'^explore-creators/(?P<category>[\w\-]+)/(?P<page>[0-9]+)/$', views.explore_creators, name='explore_creators'),
    url(r'^(?P<creator>[\w\_]+)/checkout/$', views.checkout, name='checkout'),
    url(r'^(?P<profile_username>[\w\_]+)/$', views.show_user_profile, name='show_user_profile'),
]
