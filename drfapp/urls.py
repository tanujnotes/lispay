from django.conf.urls import url

from drfapp import views

urlpatterns = [
    url(r'^get_creators/$', views.get_creators),
    url(r'^get_user/$', views.get_user),
]
