from pathlib import Path
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

from wafer.settings import *


CONFERENCE_NAME = "PyCon Africa 2025"


BASE_DIR = Path(__file__).resolve().parent


ROOT_URLCONF = "urls"


INSTALLED_APPS = (
    "template_partials",
    "django_cotton",
    "website",  # for website static content that should be version controlled
    "grants",
    "visa",  # for visa invitation letter requests
    "django_countries",  # django-countries for country selection
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
    "import_export",
    "accommodations",
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
            ),
            "builtins": ["django_browser_reload.templatetags.django_browser_reload"],
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
# from django.urls import reverse_lazy


SOCIAL_LINKS = [
    {"url": "https://bsky.app/profile/za.pycon.org", "icon": "fa-bluesky"},
    {"url": "https://mastodon.social/@pyconafrica", "icon": "fa-brands fa-mastodon"},
    {"url": "https://x.com/pyconafrica", "icon": "fa-brands fa-twitter"},
    {"url": "https://www.instagram.com/pyconafrica", "icon": "fa-brands fa-instagram"},
    {"url": "https://www.facebook.com/pyconafrica", "icon": "fa-brands fa-facebook"},
    {
        "url": "https://www.linkedin.com/company/pyconafrica/",
        "icon": "fa-brands fa-linkedin",
    },
    # {"url": "https://www.youtube.com/@PyconAfrica", "icon": "fa-brands fa-youtube"},
    {"url": "https://www.youtube.com/@pyconza", "icon": "fa-brands fa-youtube"},
    
    {"url": "https://discord.gg/zaAKDnzZGw", "icon": "fa-brands fa-discord"},
]


WAFER_MENUS += (
    {
        "menu": "about",
        "label": _("About"),
        "items": [
            # {
            #     "name": "blog",
            #     "label": _("Blog"),
            #     "url": "https://pyconafrica.blogspot.com/",
            # },
            {
                "name": "donations",
                "label": _("Donations"),
                "url": reverse_lazy("page_donations"),
            },
            {
                "name": "volunteering",
                "label": _("Volunteering"),
                "url": reverse_lazy("page_volunteering"),
            },
            # {
            #     "name": "contact",
            #     "label": _("Contact Us"),
            #     "url": reverse_lazy("page_contact"),
            # },
        ],
    },
    {
        'menu': "events",
        'label': _("Events"),
        "items": [
            {
                "menu": "beginners_day",
                "label": _("8 Oct: Beginners Day (FREE)"),
                "url": reverse_lazy("page_beginners_day"),
            },
            {
                "menu": "in_person_event",
                "label": _("9-10 Oct: In Person Conference"),
                "url": reverse_lazy("page_in_person_event"),
            },
            {
                "menu": "remote_experience",
                "label": _("9-10 Oct: Online Conference"),
                "url": reverse_lazy("page_remote_experience"),
            },
            {
                "menu": "sprints",
                "label": _("11-12 Oct: Sprints"),
                "url": reverse_lazy("page_sprints"),
            },
            {
                "menu": "friends",
                "label": _("30 Aug: Friends of PyCon Africa (FREE)"),
                "url": reverse_lazy("page_friends_of_pycon_africa"),
            },
        ]
    },
    {
        "menu": "tickets",
        "label": _("Tickets"),
        "items": [{"url": reverse_lazy("page_tickets"), "label": _("Buy Tickets")}],
    },
    {
        "menu": "venue",
        "label": _("Venue"),
        "items":[
           {
                "menu": "remote_experience",
                "label": _("Online Venue"),
                "url": reverse_lazy("page_remote_experience"),
            },
            {
                "menu": "accommodation",
                "label": _("Accommodation"),
                "url": reverse_lazy("accommodation_recommendations"),
            },
        ]
    },
    {
        "menu": "talks",
        "label": "Talks",
        "items": [
            {"name": "schedule", "label": _("Schedule"),
              "url": reverse_lazy("wafer_full_schedule")},
            {
                "url": reverse_lazy("wafer_users_talks"),
                "label": _("Accepted Talks")
            },
            {
                "url": reverse_lazy("wafer_talks_speakers"),
                "label": _("Speakers")
            }
        ]
    }

)


CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"

CRISPY_TEMPLATE_PACK = "tailwind"

WAFER_HIDE_LOGIN = False

COTTON_SNAKE_CASED_NAMES = False


INTERNAL_IPS = [  # needed for debugtoolbar
    "127.0.0.1",
]


WAFER_TALKS_OPEN = False
WAFER_REGISTRATION_OPEN = False
# The form used for talk submission
WAFER_TALK_FORM = "website.talks.forms.TalkForm"


# Set the timezone to the conference timezone
USE_TZ = True
TIME_ZONE = "Africa/Johannesburg"

# Default static and media locations - we rely on apache to redirect
# accordingly.
# These are named to not clash with the repo contents
STATIC_ROOT = BASE_DIR / "localstatic"
MEDIA_ROOT = BASE_DIR / "localmedia"

# Point static mirror away from the default, which is relative to the
# wafer package
BUILD_DIR = BASE_DIR / "mirror"

# Hide non-speaker profiles
WAFER_PUBLIC_ATTENDEE_LIST = False

GRANT_APPLICATIONS_OPEN = False
VISA_LETTER_REQUESTS_OPEN = False


VISA_ORGANISER_NAME = "Adam Piskorski"
VISA_ORGANISER_ROLE = "Director of the Python Software Society of South Africa"
VISA_ORGANISER_CONTACT_EMAIL = "pyconza@piskorski.me"
VISA_ORGANISER_CONTACT_PHONE = "+27 79 899 2319"
VISA_CONFERENCE_LOCATION = "Johannesburg, South Africa"
VISA_DEFAULT_EMBASSY_ADDRESS = "Embassy of South Africa"
WEBSITE_URL = "https://africa.pycon.org"
CONFERENCE_LOCATION = "Johannesburg, South Africa"
CONFERENCE_DATES = "8 - 12 October 2025"

WAFER_TALK_REVIEW_SCORES = (0, 5)


CONTACT_US_EMAILS = {
    'team' : 'team@pycon.org',
    'sponsorship':'sponsorship@pycon.africa'
}

SOCIAL_MEDIA_ENTRIES = {
    'linkedin': _('LinkedIn Profile link'),
    'twitter': _('Twitter Profile link'),
    'bluesky': _('BlueSky Profile link'),
    'fediverse': _('Fediverse Profile link'),
    'other': _('Other Social'),
}
