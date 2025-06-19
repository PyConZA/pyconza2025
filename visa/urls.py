from django.urls import path

from .views import VisaLetterCreateView

app_name = 'visa'

urlpatterns = [
    path('visa-application/', VisaLetterCreateView.as_view(), name='visa_letter_form'),
]
