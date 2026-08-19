# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

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
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import TemplateView

from .sitemaps import AttractionSitemap, StaticViewSitemap
from .views import (
    AttractionDetailView,
    CyclingTripsView,
    HomeView,
    InquiryView,
    RestaurantTipsView,
    SwimmingTripsView,
    TripsView,
    WeatherView,
    availability_ics,
    llms_txt,
    page_not_found,
    robots_txt,
)

sitemaps = {"static": StaticViewSitemap, "attractions": AttractionSitemap}
handler404 = page_not_found

urlpatterns = i18n_patterns(  # noqa: RUF005
    path("", HomeView.as_view(), name="home"),
    path("pocasi/", WeatherView.as_view(), name="weather"),
    path("vylety/", TripsView.as_view(), name="vylety"),
    path("vylety/cyklovylety/", CyclingTripsView.as_view(), name="cycling"),
    path("vylety/koupani/", SwimmingTripsView.as_view(), name="swimming"),
    path("vylety/restaurace/", RestaurantTipsView.as_view(), name="restaurants"),
    path(
        "vylety/<slug:slug>/",
        AttractionDetailView.as_view(),
        name="attraction_detail",
    ),
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
    path("poptavka/", InquiryView.as_view(), name="poptavka"),
    path(
        "ochrana-osobnich-udaju/",
        TemplateView.as_view(template_name="privacy.html"),
        name="privacy",
    ),
    path(
        "podminky-uziti-fotografii/",
        TemplateView.as_view(template_name="image_license.html"),
        name="image_license",
    ),
) + [
    path("obsazenost.ics", availability_ics, name="availability_ics"),
    path("robots.txt", robots_txt, name="robots"),
    path("llms.txt", llms_txt, name="llms"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps, "template_name": "sitemap.xml"},
        name="sitemap",
    ),
    path("admin/", admin.site.urls),
]
