from django.conf.urls import url
from regapp import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new/$', views.new_index, name='new_index'),
    url(r'^login_redirect/$', views.login_redirect, name='login_redirect'),
    url(r'^(?P<profile_username>[\w\_]+)/$', views.show_user_profile, name='show_user_profile'),
]
