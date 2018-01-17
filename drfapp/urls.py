from django.conf.urls import url

from drfapp import views

urlpatterns = [
    url(r'^get_creators/$', views.get_creators),
]
