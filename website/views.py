from django.conf import settings
from django.shortcuts import render

from django.shortcuts import render

# MD_DIR_PATH = settings.BASE_DIR / "md_content"


def page_home(request):
    return render(request, "website/page_home.html")


def page_tickets(request):
    return render(request, "website/page_tickets.html")
