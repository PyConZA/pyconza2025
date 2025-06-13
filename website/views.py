from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail.message import EmailMessage
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import CreateView

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
    model = VisaInvitationLetter
    form_class = VisaLetterForm
    template_name = 'website/visa_letter_form.html'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 'pending'
        response = super().form_valid(form)

        messages.success(
            self.request,
            'Your visa invitation letter request has been submitted successfully.'
            'Our team will review it and get back to you shortly (usually within 3-5 business days).'
        )

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_datetime'] = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        context['current_user'] = self.request.user.username

        existing_letters = VisaInvitationLetter.objects.filter(user=self.request.user).order_by('-created_at')

        if existing_letters.exists():
            context['existing_letter'] = existing_letters.first()
            context['has_existing_letter'] = True
            context['latest_letter'] = existing_letters.first()
        else:
            context['has_existing_letter'] = False

        return context

    def post(self, request, *args, **kwargs):
        if 'resend_email' in request.POST:
            letter_id = request.POST.get('letter_id')
            try:
                letter = VisaInvitationLetter.objects.get(id=letter_id, user=request.user)
            except VisaInvitationLetter.DoesNotExist:
                messages.error(request, "We couldn't find your visa letter request.")
                return redirect(self.request.path)

            if letter.status == 'approved':
                admin_email = EmailMessage(
                    subject=f"Visa Letter Resend Request: {letter.participant_name}",
                    body=f"The user {request.user.username} ({request.user.email}) has requested a resend of their approved visa letter.\n\nLetter ID: {letter.id}\nParticipant: {letter.participant_name}\nEmail: {letter.email}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=['team@pycon.africa'],
                )
                admin_email.send(fail_silently=False)

                messages.success(request, "Your request has been received. The team will resend your visa letter shortly.")
            else:
                messages.info(request, f"Your visa letter is still {letter.get_status_display()}. Please wait for it to be approved first.")

            return redirect(self.request.path)

        return super().post(request, *args, **kwargs)
