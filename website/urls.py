from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.page_home, name="page_home"),
    path("tickets", views.page_tickets, name="page_tickets"),
    path("sprints", views.page_sprints, name="page_sprints"),
    path("friends-of-pycon-africa", views.page_friends_of_pycon_africa, name="page_friends_of_pycon_africa"),
    # path("contact", views.page_contact, name="page_contact"),
    path("beginners-day", views.page_beginners_day, name="page_beginners_day"),
    path("donations", views.page_donations, name="page_donations"),
    path("remote-experience", views.page_remote_experience, name="page_remote_experience"),
    path("in-person-event", views.page_in_person_event, name="page_in_person_event"),
    path("volunteering", views.page_volunteering, name="page_volunteering"),
    path("dinner", views.page_dinner, name="page_dinner"),
    path("accommodations", include('accommodations.urls'))
]
