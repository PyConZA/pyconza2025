from django.shortcuts import render
from django.conf import settings


from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages

from .forms.visa_letter import VisaLetterForm
from .models import VisaInvitationLetter


MD_DIR_PATH = settings.BASE_DIR / "md_content"


def page_home(request):
    return render(request, "website/page_home.html")


def page_code_of_conduct(request):
    with open(MD_DIR_PATH / "page_code_of_conduct.md") as f:
        content = f.read()
    context = {"content": content}
    return render(request, "website/page_code_of_conduct.html", context=context)


class VisaLetterCreateView(LoginRequiredMixin, CreateView):
    """View to display and process the visa letter generation form."""
    model = VisaInvitationLetter
    form_class = VisaLetterForm
    template_name = 'website/visa_letter_form.html'
    success_url = reverse_lazy('success_page')

    def form_valid(self, form):
        """Process the form when it's valid."""
        form.instance.user = self.request.user
        form.instance.status = 'pending'

        response = super().form_valid(form)

        messages.success(
            self.request,
            'Your visa invitation letter request has been submitted. ' +
            'You will receive the letter by email once it has been approved.'
        )

        return response

    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)

        context['current_datetime'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        context['current_user'] = self.request.user.username

        return context