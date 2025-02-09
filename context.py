from django.conf import settings


def context(request):
    return {"conference_name": settings.CONFERENCE_NAME}
