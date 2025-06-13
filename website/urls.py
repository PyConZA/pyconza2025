from django.urls import path

from . import views
from .views import VisaLetterCreateView

urlpatterns = [
    path("", views.page_home, name="page_home"),
    path('visa-application/', VisaLetterCreateView.as_view(), name='visa_letter_form'),
]
