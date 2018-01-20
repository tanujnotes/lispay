from django.conf.urls import url

from drfapp import views

urlpatterns = [
    url(r'^get_creators/$', views.get_creators),
    url(r'^get_user/$', views.get_user),
    url(r'^create_subscription/$', views.create_subscription),
    url(r'^subscription_authenticated/$', views.subscription_authenticated),
]
