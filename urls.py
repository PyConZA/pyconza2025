from debug_toolbar import urls as debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path, path

admin.autodiscover()

urlpatterns = [
    re_path(r"^accounts/", include("wafer.registration.urls")),
    re_path(r"^users/", include("wafer.users.urls")),
    re_path(r"^talks/", include("wafer.talks.urls")),
    re_path(r"^sponsors/", include("wafer.sponsors.urls")),
    re_path(r"^pages/", include("wafer.pages.urls")),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^markitup/", include("markitup.urls")),
    re_path(r"^schedule/", include("wafer.schedule.urls")),
    re_path(r"^tickets/", include("wafer.tickets.urls")),
    re_path(r"^kv/", include("wafer.kv.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
    path("", include("website.urls")),
]

# Serve media and debug toolbar
if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar_urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
