from django.shortcuts import render
from .models import AccommodationRecommendation
from bakery.views import BuildableListView

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
        'contact_emails': settings.CONTACT_US_EMAILS
    }
    return render(request, "website/page_contact.html", context)


def page_beginners_day(request):
    return render(request, "website/page_beginners_day.html")


def page_donations(request):
    return render(request, "website/page_donations.html")


def page_remote_experience(request):
    return render(request, "website/page_remote_experience.html")


def page_in_person_event(request):
    return render(request, "website/page_in_person_event.html")

def page_accommodation_recommendations(request):
    SHUTTLE_CHOICES = [
        ("yes", "Yes"),
        ("no", "No"),
        ("contact", "Contact to confirm"),
    ]

    SHUTTLE_CHOICES_DICT = dict(SHUTTLE_CHOICES)
    accommodations = AccommodationRecommendation.objects.all()
    context = {
        "shuttle_choices": SHUTTLE_CHOICES_DICT,
        "accommodations": accommodations,
    }
    return render(request, "website/page_accommodation_recommendations.html", context)

class Accommodations(BuildableListView):
    model = AccommodationRecommendation
    context_object_name = 'accommodations'
    template_name = 'website/page_accommodation_recommendations.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        SHUTTLE_CHOICES = [
            ("yes", "Yes"),
            ("no", "No"),
            ("contact", "Contact to confirm"),
        ]

        SHUTTLE_CHOICES_DICT = dict(SHUTTLE_CHOICES)
        context['shuttle_choices'] = SHUTTLE_CHOICES_DICT
               
        return context