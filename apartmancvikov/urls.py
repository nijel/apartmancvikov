"""
apartmancvikov URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

Examples
--------
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))


"""

from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = i18n_patterns(  # noqa: RUF005
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("vylety/", TemplateView.as_view(template_name="vylety.html"), name="vylety"),
    path("cenik/", TemplateView.as_view(template_name="cenik.html"), name="cenik"),
    path(
        "obsazenost/",
        TemplateView.as_view(template_name="obsazenost.html"),
        name="obsazenost",
    ),
    path(
        "kontakt/",
        TemplateView.as_view(template_name="kontakt.html"),
        name="kontakt",
    ),
) + [
    path("admin/", admin.site.urls),
]
