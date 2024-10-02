# -*- encoding: utf-8 -*-
import os

from wafer.settings import *

try:
    from localsettings import *
except ImportError:
    pass

from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

pyconzadir = os.path.dirname(__file__)


STATICFILES_DIRS = (os.path.join(pyconzadir, "static"),)

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

TEMPLATES[0]["DIRS"] = (os.path.join(pyconzadir, "templates"),) + TEMPLATES[0]["DIRS"]

WAFER_MENUS += (
    {"menu": "about", "label": _("About"), "items": []},
    {"menu": "venue", "label": _("Venue"), "items": []},
    {"menu": "tickets", "label": _("Tickets"), "items": []},
    {"menu": "sponsors", "label": _("Sponsors"), "items": []},
    {
        "menu": "talks",
        "label": _("Talks"),
        "items": [
                       {
                            "name": "schedule", "label": _("Schedule"),
                            "url": reverse_lazy("wafer_full_schedule"),
                       },
                       {
                           "name": "accepted-talks",
                           "label": _("Accepted Talks"),
                           "url": reverse_lazy("wafer_users_talks"),
                       },
                       {
                           "name": "speakers",
                           "label": _("Speakers"),
                           "url": reverse_lazy("wafer_talks_speakers"),
                       },
        ],
    },
    {"menu": "news", "label": _("News"), "items": []},
    {
        "menu": "previous-pycons",
        "label": _("Past PyConZAs"),
        "items": [
            {
                "name": "pyconza2012",
                "label": _("PyConZA 2012"),
                "url": "https://2012.za.pycon.org/",
            },
            {
                "name": "pyconza2013",
                "label": _("PyConZA 2013"),
                "url": "https://2013.za.pycon.org/",
            },
            {
                "name": "pyconza2014",
                "label": _("PyConZA 2014"),
                "url": "https://2014.za.pycon.org/",
            },
            {
                "name": "pyconza2015",
                "label": _("PyConZA 2015"),
                "url": "https://2015.za.pycon.org/",
            },
            {
                "name": "pyconza2016",
                "label": _("PyConZA 2016"),
                "url": "https://2016.za.pycon.org/",
            },
            {
                "name": "pyconza2017",
                "label": _("PyConZA 2017"),
                "url": "https://2017.za.pycon.org/",
            },
            {
                "name": "pyconza2018",
                "label": _("PyConZA 2018"),
                "url": "https://2018.za.pycon.org/",
            },
            {
                "name": "pyconza2019",
                "label": _("PyConZA 2019"),
                "url": "https://2019.za.pycon.org/",
            },
            {
                "name": "pyconza2020",
                "label": _("PyConZA 2020"),
                "url": "https://2020.za.pycon.org/",
            },
            {
                "name": "pyconza2021",
                "label": _("PyConZA 2021"),
                "url": "https://2021.za.pycon.org/",
            },
            {
                "name": "pyconza2022",
                "label": _("PyConZA 2022"),
                "url": "https://2022.za.pycon.org/",
            },
            {
                "name": "pyconza2023",
                "label": _("PyConZA 2023"),
                "url": "https://2023.za.pycon.org/",
            },
        ],
    },
    {
        "name": "twitter",
        "label": "Twitter",
        "image": "/static/img/twitter.svg",
        "url": "https://twitter.com/pyconza",
    },
    {
        "name": "mastodon",
        "label": "Mastodon",
        "image": "/static/img/mastodon.svg",
        "url": "https://fosstodon.org/@pyconza",
    },
    {
        "name": "bluesky",
        "label": "Bluesky",
        "image": "/static/img/bluesky.svg",
        "url": "https://bsky.app/profile/za.pycon.org",
    },
)


_TICKET_TIERS = ("Student", "Pensioner", "Individual", "Corporate", "Sponsored",
                 "takealot: Bulk", "Thinkst: Platinum Sponsor", "SARAO: Gold Sponsor",
                 "Praelexis: Bulk", "Afrolabs: Patron Sponsor", "CHPC: Patron+Exhibitor",
                 "CoCT: Silver+Extra Tickets", "AWS: Silver Sponser")
_CAPE_TOWN_TICKET_TYPES = [
    f"{tier} ({kind})"
    for tier in _TICKET_TIERS
    for kind in ("Cape Town", "Cape Town, Early Bird")
]
_ONLINE_TICKET_TYPES = [
    f"{tier} ({kind})"
    for tier in _TICKET_TIERS
    for kind in ("Online", "Online, Early Bird")
]

_TUTORIAL_MODERN_WEB_TICKET_TYPES = [
        'Tutorial: Modern web frontend development with Python, HTMX and friends (Cape Town)'
]


def tickets_sold(ticket_types):
    """ Return number of tickets sold. """
    from wafer.tickets.models import Ticket, TicketType

    ticket_type_ids = TicketType.objects.filter(name__in=ticket_types)
    return Ticket.objects.filter(type_id__in=ticket_type_ids).count()


def cape_town_tickets_sold():
    """ Number of tickets sold for the Durban in-person conference. """
    return tickets_sold(_CAPE_TOWN_TICKET_TYPES)


def cape_town_tickets_remaining():
    """ Number of tickets remaining for the Durban in-person conference. """
    return max(0, 200 - cape_town_tickets_sold())


def online_tickets_sold():
    """ Number of tickets sold for the online conference. """
    return tickets_sold(_ONLINE_TICKET_TYPES)


def tutorial_modern_web_tickets_sold():
    """ Number of tickets sold for the devops tutorial. """
    return tickets_sold(_TUTORIAL_MODERN_WEB_TICKET_TYPES)


CRISPY_TEMPLATE_PACK = "bootstrap5"
MARKITUP_FILTER = (
    "markdown.markdown",
    {
        "safe_mode": False,
        "extensions": [
            "mdx_outline",
            "attr_list",
            "mdx_attr_cols",
            "markdown.extensions.tables",
            "markdown.extensions.codehilite",
            "mdx_variables",
            "mdx_staticfiles",
        ],
        "extension_configs": {
            "mdx_variables": {
                "vars": {
                    "cape_town_tickets_sold": cape_town_tickets_sold,
                    "cape_town_tickets_remaining": cape_town_tickets_remaining,
                    "online_tickets_sold": online_tickets_sold,
                    "tutorial_modern_web_tickets_sold": tutorial_modern_web_tickets_sold,
                }
            }
        },
    },
)
WAFER_PAGE_MARKITUP_FILTER = MARKITUP_FILTER

# Set the timezone to the conference timezone
USE_TZ = True
TIME_ZONE = "Africa/Johannesburg"

# Default static and media locations - we rely on apache to redirect
# accordingly.
# These are named to not clash with the repo contents
STATIC_ROOT = os.path.join(pyconzadir, "localstatic")
MEDIA_ROOT = os.path.join(pyconzadir, "localmedia")

# Point static mirror away from the default, which is relative to the
# wafer package
BUILD_DIR = os.path.join(pyconzadir, "mirror")

# Hide non-speaker profiles
WAFER_PUBLIC_ATTENDEE_LIST = False

# Will be needed for the static site generation
# WAFER_HIDE_LOGIN = True

# Needed to add pyconza-funding app
# INSTALLED_APPS = ('pyconza.funding', ) + INSTALLED_APPS
# ROOT_URLCONF = 'urls'

# Talks submissions are open
WAFER_TALKS_OPEN = True

# Ticket sales are open
WAFER_REGISTRATION_OPEN = True
WAFER_REGISTRATION_MODE = "ticket"


