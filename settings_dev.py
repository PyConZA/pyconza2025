from settings_base import *
from django.utils.translation import gettext_lazy as _

DEBUG = True

SECRET_KEY = "8iysa30^no&oi5kv$k1w)#gsxzrylr-h6%)loz71expnbf7z%)"


EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = "gitignore/emails"
