from django.conf.urls import url
from dash import views
from regapp.views import show_user_profile

urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^(?P<profile_username>[\w\_]+)/$', show_user_profile, name='show_user_profile'),
]
