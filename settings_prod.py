from settings_base import *

try:
    from localsettings import *
except ImportError:
    pass

DEBUG = False
