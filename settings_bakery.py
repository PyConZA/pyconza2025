from settings_prod import *

ALLOWED_HOSTS = ["*"]

# Remove dev-only apps that break bakery builds
INSTALLED_APPS = tuple(
    a for a in INSTALLED_APPS if a != "debug_toolbar"
)

MIDDLEWARE = tuple(
    m for m in MIDDLEWARE
    if "browser_reload" not in m and "debug_toolbar" not in m
)
