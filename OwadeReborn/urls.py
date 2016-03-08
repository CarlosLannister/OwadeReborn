"""OwadeReborn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import RedirectView

import owade.views as views

urlpatterns = [
    url(r'^login', admin.site.urls),
    url(r'^$', views.index , name='index'),
    url(r'^$', RedirectView.as_view(url='/'), name='index'),
    url(r'^extract$', views.extractView),
    url(r'^analyze$', views.analizeView),
    url(r'^launch$', views.launchView),
    url(r'^refresh_intern_log$', views.refreshInternLogView),
    url(r'^refresh_terminal_log$', views.refreshTerminalLogView),

]
