from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.page_home, name="page_home"),
    path(
        "code_of_conduct",
        TemplateView.as_view(template_name="website/page_code_of_conduct.html"),
        name="page_code_of_conduct",
    ),
]
