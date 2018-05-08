from django.conf.urls import url

from drfapp import views

urlpatterns = [
    url(r'^get_user/$', views.get_user),
    url(r'^dashboard/$', views.dashboard),
    url(r'^update_user/$', views.update_user),
    url(r'^get_creators/$', views.get_creators),
    url(r'^update_creator/$', views.update_creator),
    url(r'^my_subscriptions/$', views.my_subscriptions),
    url(r'^get_firebase_token/$', views.get_firebase_token),
    url(r'^create_subscription/$', views.create_subscription),
    url(r'^update_social_details/$', views.update_social_details),
    url(r'^subscription_authenticated/$', views.subscription_authenticated),
]
