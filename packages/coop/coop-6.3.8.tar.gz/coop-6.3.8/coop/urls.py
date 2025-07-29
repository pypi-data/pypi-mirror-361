import re
from typing import TYPE_CHECKING

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.urls import include, path, re_path
from django.views.static import serve
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from coop.styleguide import urls as styleguide_urls

if TYPE_CHECKING:
    from wagtail.contrib.settings.models import BaseSiteSetting
    from wagtail.images.models import AbstractImage


def asset_redirect(src, dest):
    try:
        asset_url = staticfiles_storage.url(dest)
    except ValueError:

        def view(request):
            raise Http404
    else:

        def view(request):
            return HttpResponsePermanentRedirect(asset_url)

    return re_path(r"^" + re.escape(src) + "$", view)


def favicon_redirect(request):
    if model_string := getattr(settings, "FAVICON_MODEL", None):
        try:
            app_name, model_name = model_string.split(".")
            Model: "BaseSiteSetting" = apps.get_model(app_name, model_name)
            instance = Model.for_request(request)
            if not instance:
                raise Http404("Favicon model not found")
            field = getattr(settings, "FAVICON_FIELD", "favicon")
            src: "AbstractImage" = getattr(instance, field)
            if not src:
                raise Http404("Favicon not found")
            dest = src.get_rendition("format-ico").url
            return HttpResponsePermanentRedirect(dest)
        except LookupError:
            raise Http404("Favicon settings not found")
    else:
        try:
            asset_url = staticfiles_storage.url("images/favicon.png")
        except ValueError:
            raise Http404("Favicon not found")
        return HttpResponsePermanentRedirect(asset_url)


def handler404(request, exception=None):
    request.is_preview = False
    return render(request, "layouts/404.html", {"exception": exception}, status=404)


def handler500(request):
    request.is_preview = False
    return render(request, "layouts/500.html", status=500)


urlpatterns = [
    path("favicon.ico", favicon_redirect),
    asset_redirect("humans.txt", "misc/humans.txt"),
    asset_redirect("robots.txt", "misc/robots.txt"),
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    re_path(r"sitemap\.xml$", sitemap),
    path("_styleguide/", include(styleguide_urls)),
    path("404/", handler404),
    path("500/", handler500),
    path("", include(wagtail_urls)),
]

if settings.DEBUG or getattr(settings, "FORCE_ASSET_SERVING", False):

    def static(prefix, document_root):
        pattern = r"^%s(?P<path>.*)$" % re.escape(prefix.lstrip("/"))
        return [re_path(pattern, serve, kwargs={"document_root": document_root})]

    urlpatterns += static(settings.STATIC_URL, settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, settings.MEDIA_ROOT)
