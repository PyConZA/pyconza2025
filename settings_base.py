from pathlib import Path
from django.utils.translation import gettext_lazy as _

from wafer.settings import *


CONFERENCE_NAME = "PyCon Africa 2025"


BASE_DIR = Path(__file__).resolve().parent


ROOT_URLCONF = "urls"


INSTALLED_APPS = (
    "django_cotton",
    "website",  # for website static content that should be version controlled
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.redirects",
    "reversion",
    "bakery",
    "crispy_forms",
    "crispy_tailwind",
    "rest_framework",
    "django_select2",
    "wafer",
    "wafer.kv",
    "wafer.registration",
    "wafer.talks",
    "wafer.schedule",
    "wafer.users",
    "wafer.sponsors",
    "wafer.pages",
    "wafer.tickets",
    "wafer.compare",
    # Django isn't finding the overridden templates
    "markitup",
    "registration",
    "django.contrib.admin",
    "django_browser_reload",  # https://github.com/adamchainz/django-browser-reload
    "debug_toolbar",  # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
)


TEMPLATES = [
    {
        "APP_DIRS": True,  # Changed to True for Debugtoolbar
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "wafer.context_processors.site_info",
                "wafer.context_processors.navigation_info",
                "wafer.context_processors.menu_info",
                "wafer.context_processors.registration_settings",
                "context.context",
            )
        },
    },
]


MIDDLEWARE = (
    "debug_toolbar.middleware.DebugToolbarMiddleware",  # see warning here: https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware",
)


# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = "/static/"
STATIC_ROOT = ""
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# STORAGES = {
#     "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#     },
# }
from django.urls import reverse_lazy


WAFER_MENUS += (
    # {"menu": "sponsors", "label": _("Sponsors"), "items": []},
)


CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"

CRISPY_TEMPLATE_PACK = "tailwind"

WAFER_HIDE_LOGIN = False

COTTON_SNAKE_CASED_NAMES = False


INTERNAL_IPS = [  # needed for debugtoolbar
    "127.0.0.1",
]
