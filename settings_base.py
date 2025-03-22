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
    "crispy_bootstrap5",
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
)


TEMPLATES = [
    {
        "APP_DIRS": False,
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
    {
        "menu": "about",
        "label": _("About"),
        "items": [
            # {
            #     "name": "about_us",
            #     "label": _("About Us"),
            #     "url": reverse_lazy("page_code_of_conduct"),
            # },
            # {
            #     "name": "team",
            #     "label": _("Team"),
            #     "url": reverse_lazy("page_code_of_conduct"),
            # },
            {
                "name": "code_of_conduct",
                "label": _("Code of Conduct"),
                "url": reverse_lazy("page_code_of_conduct"),
            },
            # {
            #     "name": "financial_assistance",
            #     "label": _("Financial Assistance"),
            #     "url": reverse_lazy("page_code_of_conduct"),
            # },
            # {
            #     "name": "health_and_safety",
            #     "label": _("Health and Safety"),
            #     "url": reverse_lazy("page_code_of_conduct"),
            # },
            # {
            #     "name": "privacy",
            #     "label": _("Privacy Policy"),
            #     "url": reverse_lazy("page_code_of_conduct"),
            # },
        ],
    },
    # {"menu": "speak_at_pycon", "label": _("Speak at PyCon Africa"), "items": []},
)
