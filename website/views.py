from django.shortcuts import render


def page_home(request):
    return render(request, "website/page_home.html")


def page_tickets(request):
    return render(request, "website/page_tickets.html")


def page_sprints(request):
    return render(request, "website/page_sprints.html")


def page_friends_of_pycon_africa(request):
    return render(request, "website/page_friends_of_pycon_africa.html")


def page_contact(request):
    from django.conf import settings
    context = {
        'social_links': settings.SOCIAL_LINKS,
        'contact_emails': getattr(settings, 'CONTACT_US_EMAILS', {})
    }
    return render(request, "website/page_contact.html", context)


def page_beginners_day(request):
    return render(request, "website/page_beginners_day.html")


def page_donations(request):
    return render(request, "website/page_donations.html")
