from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail.message import EmailMessage
from django.http.response import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import CreateView

from visa.forms.visa_letter import VisaLetterForm
from .models import VisaInvitationLetter


class VisaLetterCreateView(LoginRequiredMixin, CreateView):
    model = VisaInvitationLetter
    form_class = VisaLetterForm
    template_name = "visa/visa_letter_form.html"

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = "pending"
        response = super().form_valid(form)

        self.request.session["visa_form_success"] = True

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_datetime"] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        context["current_user"] = self.request.user.username

        context["form_submitted"] = self.request.session.pop("visa_form_success", False)

        context["error_message"] = self.request.session.pop("visa_error", None)
        context["success_message"] = self.request.session.pop("visa_success", None)
        context["info_message"] = self.request.session.pop("visa_info", None)

        try:
            existing_letter = get_object_or_404(VisaInvitationLetter, user=self.request.user)
            context["existing_letter"] = existing_letter
            context["has_existing_letter"] = True
            context["latest_letter"] = existing_letter
        except Http404:
            context["has_existing_letter"] = False

        return context

    def post(self, request, *args, **kwargs):
        if "resend_email" in request.POST:
            letter = get_object_or_404(VisaInvitationLetter, user=request.user)

            if letter.status == "approved":
                admin_email = EmailMessage(
                    subject=f"Visa Letter Resend Request: {letter.participant_name}",
                    body=f"The user {request.user.username} ({request.user.email}) has requested a resend of their approved visa letter.\n\nLetter ID: {letter.id}\nParticipant: {letter.participant_name}\nEmail: {request.user.email}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=["team@pycon.africa"],
                )
                admin_email.send(fail_silently=False)

                request.session["visa_success"] = (
                    "Your request has been received. The team will resend your visa letter shortly."
                )
            else:
                request.session["visa_info"] = (
                    f"Your visa letter is still {letter.get_status_display()}. Please wait for it to be approved first."
                )

            return redirect(self.request.path)

        return super().post(request, *args, **kwargs)
