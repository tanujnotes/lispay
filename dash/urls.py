from django.conf.urls import url
from dash import views

urlpatterns = [
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
]
