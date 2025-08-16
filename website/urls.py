from django.urls import path

from . import views

urlpatterns = [
    path("", views.page_home, name="page_home"),
    path("tickets", views.page_tickets, name="page_tickets"),
    path("friends-of-pycon-africa", views.page_friends_of_pycon_africa, name="page_friends_of_pycon_africa"),
]
