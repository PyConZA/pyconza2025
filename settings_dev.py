from django.utils.translation import gettext_lazy as _

from settings_base import *

DEBUG = True

SECRET_KEY = "8iysa30^no&oi5kv$k1w)#gsxzrylr-h6%)loz71expnbf7z%)"


EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = "gitignore/emails"


def show_toolbar(request):
    """Always show the debug toolbar"""
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    "RENDER_PANELS": True,
    "RESULTS_CACHE_SIZE": 100,
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.templates.TemplatesPanel"
    ]
}
