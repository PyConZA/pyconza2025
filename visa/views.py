from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView

from visa.forms.visa_letter import VisaLetterForm
from visa.models import VisaInvitationLetter


class VisaLetterCreateView(LoginRequiredMixin, CreateView):
    model = VisaInvitationLetter
    form_class = VisaLetterForm
    template_name = "visa/visa_letter_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not getattr(settings, "VISA_LETTER_REQUESTS_OPEN", False):
            messages.error(request, "Visa letter requests are currently closed.")
            return redirect("wafer_user_profile", username=request.user.username)
        
        if hasattr(request.user, "visa_letter"):
            messages.info(request, "You already have a visa letter request.")
            return redirect("visa:visa_letter_detail")
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Your visa letter request has been submitted successfully. "
            "You will receive an email once it has been reviewed."
        )
        return response

    def get_success_url(self):
        return reverse_lazy("visa:visa_letter_detail")


class VisaLetterUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = VisaInvitationLetter
    form_class = VisaLetterForm
    template_name = "visa/visa_letter_form.html"

    def test_func(self):
        return hasattr(self.request.user, "visa_letter")

    def get_object(self, queryset=None):
        return self.request.user.visa_letter

    def dispatch(self, request, *args, **kwargs):
        if not getattr(settings, "VISA_LETTER_REQUESTS_OPEN", False):
            messages.error(request, "Visa letter requests are currently closed.")
            return redirect("wafer_user_profile", username=request.user.username)
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Your visa letter request has been updated successfully."
        )
        return response

    def get_success_url(self):
        return reverse_lazy("visa:visa_letter_detail")


class VisaLetterDetailView(LoginRequiredMixin, DetailView):
    model = VisaInvitationLetter
    template_name = "visa/visa_letter_detail.html"
    context_object_name = "visa_letter"

    def get_object(self, queryset=None):
        return self.request.user.visa_letter
    
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        except VisaInvitationLetter.DoesNotExist:
            messages.error(
                request,
                "You don't have a visa letter request yet."
            )
            return redirect("visa:visa_letter_form")