from django.conf.urls import url

from dash import views

# Don't forget to add the url name in RESTRICTED_USERNAMES

urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^update-profile/$', views.update_profile, name='update_profile'),
    url(r'^creator-details/$', views.creator_details, name='creator_details'),
]
