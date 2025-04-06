from django.conf import settings


def context(request):
    return {
        "conference_name": settings.CONFERENCE_NAME,
        "social_links": settings.SOCIAL_LINKS,
    }
