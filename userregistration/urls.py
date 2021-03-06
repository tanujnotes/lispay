"""userregistration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from allauth.account.views import confirm_email as allauthemailconfirmation
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from regapp import views

urlpatterns = [
                  url(r'^$', views.index, name='index'),
                  # url(r'^', include('django.contrib.auth.urls')), # uncomment for rest-auth password reset link
                  url(r'^admin/', admin.site.urls),
                  url(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
                      name="robots_file"),
                  url(r'^', include('dash.urls')),
                  url(r'^', include('regapp.urls')),
                  url(r'^api/', include('drfapp.urls')),
                  url(r'^accounts/', include('allauth.urls')),
                  url(r'^rest-auth/', include('rest_auth.urls')),
                  url(r'^rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$', allauthemailconfirmation,
                      name="account_confirm_email"),
                  url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
