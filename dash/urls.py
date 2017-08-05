from django.conf.urls import url
from dash import views
from regapp.views import show_user_profile

urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^update_profile/$', views.update_profile, name='update_profile'),
    url(r'^creator_details/$', views.creator_details, name='creator_details'),
    url(r'^(?P<profile_username>[\w\_]+)/$', show_user_profile, name='show_user_profile'),
]
